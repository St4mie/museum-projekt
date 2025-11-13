# tests/test_integration.py
# ----------------------------------------------------
# Integrationstests für die gesamte FastAPI-Anwendung
# ----------------------------------------------------

# Stellt sicher, dass die App-Version in den Settings vorhanden ist,
# damit der Import von app.main nicht scheitert.
import os
os.environ.setdefault("APP_APP_VERSION", "0.1.0")

import pytest
import base64
from fastapi.testclient import TestClient

# Die echte App inkl. aller Router und Abhängigkeiten
from app.main import app as real_app
from app.db import Base, SessionLocal, engine, get_db
from app.models.movie import MovieORM

# -----------------------------------------------------------------------------
# Konstanten für die Bulk-Import-Tests
# -----------------------------------------------------------------------------
FILM_TITLES = [
    "Citizen Kane",
    "The Godfather",
    "Pulp Fiction",
    "Casablanca",
    "The Shawshank Redemption",
    "The Dark Knight",
    "Forrest Gump",
    "Schindler's List",
    "Star Wars: Episode IV – A New Hope",
    "The Lord of the Rings: The Fellowship of the Ring",
    "Inception",
    "Fight Club",
]

# -----------------------------------------------------------------------------
# 1. Datenbank-Setup (MariaDB) für die gesamte Test-Session
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Einmalig: Alle Tabellen erstellen, damit Tests gegen eine leere Schema starten.
    """
    Base.metadata.create_all(bind=engine)
    yield
    # Optional: Nach allen Tests wieder abreißen
    # Base.metadata.drop_all(bind=engine)


# -----------------------------------------------------------------------------
# 2. Dependency-Override: immer dieselbe MariaDB-Session verwenden
# -----------------------------------------------------------------------------
def override_get_db():
    """
    FastAPI-Dependency-Override für get_db:
    Nutzt SessionLocal() statt SQLite-Voreinstellung.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------------------------------------------------------
# 3. TestClient-Fixture mit Basic-Auth (dev/devpass)
# -----------------------------------------------------------------------------
@pytest.fixture()
def client(settings):
    """
    Erzeugt einen TestClient, der automatisch den Basic-Auth-Header setzt.
    Verwendet die Default-Credentials aus der settings-Fixture.
    """
    # Dependency-Override für die DB
    # Initialize dependency_overrides as a dictionary if it doesn't exist
    if not hasattr(real_app, "dependency_overrides"):
        real_app.dependency_overrides = {}
    real_app.dependency_overrides[get_db] = override_get_db

    # Basic-Auth-Header erstellen
    credentials = f"{settings.test_user}:{settings.test_pass}"
    encoded = base64.b64encode(credentials.encode()).decode()
    auth_header = {"Authorization": f"Basic {encoded}"}

    # Client konfigurieren
    test_client = TestClient(real_app)
    test_client.headers.update(auth_header)
    return test_client


# -----------------------------------------------------------------------------
# 4. Isolation: Vor jedem Test alle Movie-Einträge löschen
# -----------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def clear_db():
    """
    Vor jedem einzelnen Test: Tabelle movies leeren.
    """
    db = SessionLocal()
    db.query(MovieORM).delete()
    db.commit()
    db.close()
    yield


# -----------------------------------------------------------------------------
# 5. Smoke-Tests (Root, Docs, OpenAPI, Media)
# -----------------------------------------------------------------------------

def test_root(client):
    """Die Root-Route '/' liefert HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_docs(client):
    """Die Swagger-Oberfläche '/docs' ist erreichbar (HTTP 200)."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi(client):
    """Die OpenAPI-Spezifikation '/openapi.json' liegt vor."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data


def test_list_media(client):
    """Liste aller Medien über '/media' abrufbar (HTTP 200)."""
    response = client.get("/media")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_media_detail(client):
    """Details zu einem Medium '/media/1' liefern id, url und type."""
    response = client.get("/media/1")
    assert response.status_code == 200
    data = response.json()
    for field in ("id", "url", "type"):
        assert field in data


# -----------------------------------------------------------------------------
# 6. Auth-Tests für /movies/
# -----------------------------------------------------------------------------

def test_movies_unauthorized():
    """Ohne Auth: /movies/ gibt HTTP 401 zurück."""
    no_auth_client = TestClient(real_app)
    response = no_auth_client.get("/movies/")
    assert response.status_code == 401


def test_movies_authorized(client):
    """Mit gültiger Auth: /movies/ gibt HTTP 200 und Liste zurück."""
    response = client.get("/movies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# -----------------------------------------------------------------------------
# 7. CRUD-Tests für die Movie-API
# -----------------------------------------------------------------------------

def test_read_empty_movies(client):
    """GET /movies/ liefert initial eine leere Liste."""
    response = client.get("/movies/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_read_movie(client):
    """POST /movies/ erstellt neuen Film, GET listet ihn auf."""
    payload = {"title": "Test Movie", "release_year": 2025}
    # Anlegen
    create_resp = client.post("/movies/", json=payload)
    assert create_resp.status_code == 201
    movie = create_resp.json()
    assert movie["title"] == payload["title"]
    assert movie["release_year"] == payload["release_year"]
    assert "id" in movie

    # Lesen
    list_resp = client.get("/movies/")
    assert list_resp.status_code == 200
    all_movies = list_resp.json()
    assert len(all_movies) == 1
    assert all_movies[0]["title"] == payload["title"]


def test_prevent_duplicate_movie(client):
    """POST mit gleichem Titel+Jahr liefert HTTP 409."""
    payload = {"title": "Dup", "release_year": 2020}
    assert client.post("/movies/", json=payload).status_code == 201
    dup_resp = client.post("/movies/", json=payload)
    assert dup_resp.status_code == 409
    assert "existiert bereits" in dup_resp.json()["detail"].lower()


# -----------------------------------------------------------------------------
# 8. Tests für Einzel-Import aus dem Wiki
# -----------------------------------------------------------------------------

def test_import_from_wiki_success(client, monkeypatch):
    """POST /movies/import/{id} fügt Felder gemäß WikiImporter.fetch hinzu."""
    # Erst Film ohne Zusatzdaten anlegen
    base = client.post("/movies/", json={"title": "Some Title", "release_year": 2000})
    mid = base.json()["id"]

    # Mock WikiImporter.fetch für Erfolgsszenario
    fake = {
        "description": "Desc",
        "director": "Dir",
        "author": "Auth",
        "main_cast": "A,B,C",
        "poster_url": "http://img"
    }
    monkeypatch.setattr(
        "app.services.wiki_importer.WikiImporter.fetch",
        staticmethod(lambda _: fake)
    )

    # Import antriggern
    resp = client.post(f"/movies/import/{mid}")
    assert resp.status_code == 200
    result = resp.json()
    for k, v in fake.items():
        assert result[k] == v


def test_import_from_wiki_failure(client, monkeypatch):
    """POST /movies/import/{id} bei Fehler setzt review=True und liefert 502."""
    base = client.post("/movies/", json={"title": "Err Title", "release_year": 1999})
    mid = base.json()["id"]

    # Mock WikiImporter.fetch für Fehler
    monkeypatch.setattr(
        "app.services.wiki_importer.WikiImporter.fetch",
        staticmethod(lambda _: (_ for _ in ()).throw(RuntimeError("oh no")))
    )

    # Import antriggern
    resp = client.post(f"/movies/import/{mid}")
    assert resp.status_code == 502

    # DB-Prüfung: review-Flag muss True sein
    db = SessionLocal()
    obj = db.query(MovieORM).filter(MovieORM.id == mid).first()
    assert obj.review is True
    db.close()


# -----------------------------------------------------------------------------
# 9. Tests für Bulk-Import und Statusabfrage
# -----------------------------------------------------------------------------

def test_import_films(client):
    """POST /wiki/import bulk-importiert alle FILM_TITLES."""
    resp = client.post("/wiki/import", json={"titles": FILM_TITLES})
    assert resp.status_code in (200, 201)
    j = resp.json()
    assert isinstance(j, dict)


def test_import_status(client):
    """GET /wiki/import/status liefert Status, processed und errors."""
    resp = client.get("/wiki/import/status")
    assert resp.status_code == 200
    j = resp.json()
    for key in ("status", "processed", "errors"):
        assert key in j
