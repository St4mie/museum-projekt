# backend/tests/test_api.py

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Korrekte Imports: wir nutzen das app-Package, nicht backend.app
from app.db import Base, get_db
from app.models.movie import MovieORM
from app.api.endpoints import router

# ---------------------------------------------------------------------
# File-based SQLite DB für Tests einrichten
# ---------------------------------------------------------------------
import os
# Create a test database file in the current directory
TEST_DB_FILE = "test.db"
# Remove the file if it exists
if os.path.exists(TEST_DB_FILE):
    os.remove(TEST_DB_FILE)
SQLITE_URL = f"sqlite:///{TEST_DB_FILE}"
engine = create_engine(
    SQLITE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Schema einmalig in der Test-DB anlegen
Base.metadata.create_all(bind=engine)

# Debug: Print the tables that were created
from sqlalchemy import text
with engine.connect() as conn:
    # Get all table names
    tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    print("Created tables:", [table[0] for table in tables])

# ---------------------------------------------------------------------
# FastAPI-Dependency-Override: statt MariaDB unsere In-Memory-DB nutzen
# ---------------------------------------------------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new FastAPI app for testing
test_app = FastAPI()
test_app.include_router(router)

# Override the get_db dependency
test_app.dependency_overrides[get_db] = override_get_db

# Create a TestClient
client = TestClient(test_app)

# ---------------------------------------------------------------------
# Fixture: Vor jedem Test DB leeren
# ---------------------------------------------------------------------
@pytest.fixture(autouse=True)
def clear_db():
    session = TestingSessionLocal()
    session.query(MovieORM).delete()
    session.commit()
    session.close()
    yield

# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------
def test_read_empty_movies():
    """GET /movies/ liefert anfangs eine leere Liste"""
    response = client.get("/movies/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_and_read_movie():
    """POST /movies/ legt einen Film an, GET /movies/ liest ihn aus"""
    payload = {"title": "Test Movie", "release_year": 2025}

    # anlegen
    r1 = client.post("/movies/", json=payload)
    assert r1.status_code == 201
    movie = r1.json()
    assert movie["title"] == "Test Movie"
    assert movie["release_year"] == 2025
    assert "id" in movie

    # auslesen
    r2 = client.get("/movies/")
    assert r2.status_code == 200
    data = r2.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Movie"

def test_prevent_duplicate_movie():
    """POST /movies/ mit gleichem Titel+Jahr schlägt mit 409 fehl"""
    payload = {"title": "Dup", "release_year": 2020}
    assert client.post("/movies/", json=payload).status_code == 201

    r2 = client.post("/movies/", json=payload)
    assert r2.status_code == 409
    assert "already exists" in r2.json()["detail"].lower()

def test_import_from_wiki_success(monkeypatch):
    """POST /movies/import/{id} füllt Felder erfolgreich aus WikiImporter"""
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
        "app.services.wiki_importer.WikiImporter.fetch",
        staticmethod(lambda _: fake_data)
    )

    # Import
    r2 = client.post(f"/movies/import/{movie_id}")
    assert r2.status_code == 200
    out = r2.json()
    for k, v in fake_data.items():
        assert out[k] == v

def test_import_from_wiki_failure(monkeypatch):
    """POST /movies/import/{id} bei Import-Error setzt review=True und liefert 502"""
    r = client.post("/movies/", json={"title": "Err Title", "release_year": 1999})
    mid = r.json()["id"]

    # WikiImporter.fetch wirft Exception
    monkeypatch.setattr(
        "app.services.wiki_importer.WikiImporter.fetch",
        staticmethod(lambda _: (_ for _ in ()).throw(RuntimeError("oh no")))
    )

    # Import
    r2 = client.post(f"/movies/import/{mid}")
    assert r2.status_code == 502
    body = r2.json()
    assert "oh no" in body["detail"]

    # DB-Prüfung: review=True
    session = TestingSessionLocal()
    obj = session.get(MovieORM, mid)
    assert obj.review is True
    session.close()
