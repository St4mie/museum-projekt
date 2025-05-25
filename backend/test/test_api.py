import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db import Base, get_db
from backend.app.main import app

# Import all models to ensure they are registered with Base

# Typ-Annotation für die IDE, damit FastAPI-spezifische Attribute erkannt werden
app: FastAPI = app

# ---------------------------------------------------------------------
# File-based SQLite DB für Tests einrichten
# ---------------------------------------------------------------------
import os
import tempfile

# Create a temporary file for the SQLite database
db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
db_file.close()

# Use the file path for the SQLite database
SQLITE_URL = f"sqlite:///{db_file.name}"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Make sure all models are imported and registered with Base
from backend.app.models.movie import MovieORM

# Schema einmalig in der Test-DB anlegen
Base.metadata.create_all(bind=engine)

# Clean up the temporary file when the tests are done
import atexit
atexit.register(lambda: os.unlink(db_file.name))

# ---------------------------------------------------------------------
# FastAPI-Dependency-Override: statt MariaDB unsere In-Memory-DB nutzen
# ---------------------------------------------------------------------
def override_get_db():
    """Override von get_db, um Tests mit In-Memory-DB durchzuführen."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ---------------------------------------------------------------------
# Fixture: Vor jedem Test die Movie-Tabelle leeren
# ---------------------------------------------------------------------
@pytest.fixture(autouse=True)
def clear_db():
    """Leert die Movie-Tabelle vor jedem Testlauf."""
    session = TestingSessionLocal()
    session.query(MovieORM).delete()
    session.commit()
    session.close()
    yield

# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------
def test_read_empty_movies():
    """GET /movies/ liefert anfangs eine leere Liste."""
    response = client.get("/movies/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_and_read_movie():
    """POST /movies/ legt einen Film an und GET /movies/ liest ihn aus."""
    payload = {"title": "Test Movie", "release_year": 2025}

    # Film anlegen
    r1 = client.post("/movies/", json=payload)
    assert r1.status_code == 201
    movie = r1.json()
    assert movie["title"] == "Test Movie"
    assert movie["release_year"] == 2025
    assert "id" in movie

    # Film abrufen
    r2 = client.get("/movies/")
    assert r2.status_code == 200
    data = r2.json()
    assert isinstance(data, list) and len(data) == 1
    assert data[0]["title"] == "Test Movie"

def test_prevent_duplicate_movie():
    """POST /movies/ mit gleichem Titel+Jahr schlägt mit 409 fehl."""
    payload = {"title": "Dup", "release_year": 2020}
    assert client.post("/movies/", json=payload).status_code == 201

    r2 = client.post("/movies/", json=payload)
    assert r2.status_code == 409
    assert "already exists" in r2.json()["detail"].lower()

def test_import_from_wiki_success(monkeypatch):
    """POST /movies/import/{id} füllt Felder erfolgreich aus WikiImporter."""
    # Film ohne Details anlegen
    r = client.post("/movies/", json={"title": "Some Title", "release_year": 2000})
    movie_id = r.json()["id"]

    # WikiImporter.fetch stubben
    fake_data = {
        "description": "Desc",
        "director": "Dir",
        "author": "Auth",
        "main_cast": "A,B,C",
        "poster_url": "http://img"
    }
    monkeypatch.setattr(
        "backend.app.services.wiki_importer.WikiImporter.fetch",
        staticmethod(lambda _: fake_data)
    )

    # Import aufrufen
    r2 = client.post(f"/movies/import/{movie_id}")
    assert r2.status_code == 200
    out = r2.json()
    for k, v in fake_data.items():
        assert out[k] == v

def test_import_from_wiki_failure(monkeypatch):
    """POST /movies/import/{id} bei Import-Error setzt review=True und liefert 502."""
    # Film anlegen
    r = client.post("/movies/", json={"title": "Err Title", "release_year": 1999})
    mid = r.json()["id"]

    # Ausnahme in WikiImporter.fetch auslösen
    monkeypatch.setattr(
        "backend.app.services.wiki_importer.WikiImporter.fetch",
        staticmethod(lambda _: (_ for _ in ()).throw(RuntimeError("oh no")))
    )

    # Import aufrufen
    r2 = client.post(f"/movies/import/{mid}")
    assert r2.status_code == 502
    assert "oh no" in r2.json()["detail"]

    # Überprüfen, dass review=True gesetzt wurde
    session = TestingSessionLocal()
    obj = session.get(MovieORM, mid)
    assert obj.review is True
    session.close()
