# backend/tests/test_scene_media_endpoint.py

import pytest
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
import io
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Router importieren
from app.api.media import router as media_router

# Module, in denen wir BASE/Config patchen müssen
import app.config as config
import app.services.media_processor as media_processor
import app.api.media as media_api

# Für DB-Mocking
from app.db import Base, get_db
from app.models import MovieORM, SzeneORM, MediumORM

# ----------------------------------------
# Hilfsfunktionen für Tests
# ----------------------------------------

def create_dummy_image(path: Path, size=(100, 100), color=(255, 0, 0)):
    """
    Erzeugt ein simples JPEG-Bild an der gegebenen Stelle.
    - path: vollständiger Pfad inklusive Dateiname
    - size: (Breite, Höhe)
    - color: RGB-Farb-Tupel
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color)
    img.save(path, format="JPEG")


def create_file(root: Path, *subdirs: str, filename: str, data: bytes):
    """
    Legt eine Datei mit den gegebenen Bytes an:
      root / subdirs / filename
    - root: Basisverzeichnis
    - subdirs: beliebig viele Unterordner
    - filename: Name der Datei
    - data: Rohdaten als Bytes
    """
    file_path = root.joinpath(*subdirs, filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(data)
    return file_path


# ----------------------------------------
# In-Memory-DB für Tests
# ----------------------------------------

@pytest.fixture
def test_db():
    """
    Erstellt eine In-Memory-SQLite-DB für Tests.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Test-Daten einfügen
    db = TestingSessionLocal()
    
    # Film anlegen
    movie = MovieORM(
        id=5,
        titel="Test Film",
        erscheinungsjahr=2023,
        regisseur="Test Regisseur",
        beschreibung="Test Beschreibung"
    )
    db.add(movie)
    db.commit()
    
    # Szene anlegen
    szene = SzeneORM(
        id=10,
        film_id=5,
        name="Test Szene",
        beschreibung="Test Szene Beschreibung"
    )
    db.add(szene)
    db.commit()
    
    # Medium anlegen
    medium = MediumORM(
        id=15,
        szene_id=10,
        dateipfad="/path/to/test/media.mp4",
        medientyp="video"
    )
    db.add(medium)
    db.commit()
    
    # Dependency Override
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    return override_get_db


# ----------------------------------------
# TestClient-Setup
# ----------------------------------------

@pytest.fixture
def client(test_db):
    """
    Erstellt einen TestClient mit DB-Dependency-Override.
    """
    app = FastAPI()
    app.include_router(media_router)
    app.dependency_overrides[get_db] = test_db
    return TestClient(app)


# ----------------------------------------
# Fixture: Temporärer MEDIA_STATIC_PATH
# ----------------------------------------

@pytest.fixture
def set_static_dir(tmp_path: Path, monkeypatch):
    """
    Override aller BASE-Pfade und der Config-Variable:
    1) config.MEDIA_STATIC_PATH
    2) media_processor.BASE
    3) media_api.BASE

    So schreiben alle Funktionen in dasselbe tmp_path.
    """
    # 1) Patch der zentralen Config
    monkeypatch.setattr(config, "MEDIA_STATIC_PATH", tmp_path)
    # 2) Patch der BASE-Konstanten in den Modulen
    monkeypatch.setattr(media_processor, "BASE", tmp_path)
    monkeypatch.setattr(media_api, "BASE", tmp_path)
    return tmp_path


# ----------------------------------------
# Autouse-Fixture: Setup für Input- & Output-Files
# ----------------------------------------

@pytest.fixture(autouse=True)
def setup_files(set_static_dir: Path, monkeypatch):
    """
    Vor jedem Test werden angelegt:
    a) Ein valides Testbild (pic.jpg)
    b) Eine Dummy-Video-Quelldatei (clip.mp4)
    c) Eine Dummy-Audio-Quelldatei (audio.mp3)
    d) Pfad für Medium in der DB anpassen
    """
    # a) Testbild
    img_path = set_static_dir / "images" / "movies" / "5" / "pic.jpg"
    create_dummy_image(img_path)

    # b) Original-Video
    video_path = create_file(
        set_static_dir,
        "videos", "movies", "5",
        filename="clip.mp4",
        data=b"ORIGINAL-VIDEO"
    )

    # c) Original-Audio
    audio_path = create_file(
        set_static_dir,
        "audio", "movies", "5",
        filename="audio.mp3",
        data=b"ORIGINAL-AUDIO"
    )
    
    # d) Pfad für Medium in der DB anpassen (monkeypatching)
    def mock_query_first(*args, **kwargs):
        medium = MediumORM(
            id=15,
            szene_id=10,
            dateipfad=str(video_path),
            medientyp="video"
        )
        return medium
    
    # Monkeypatch für die DB-Abfrage
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_query_first)

    yield
    # tmp_path wird automatisch aufgeräumt


# ----------------------------------------
# Tests
# ----------------------------------------

def test_list_scene_media(client):
    """
    Test für GET /scenes/{scene_id}/media
    """
    response = client.get("/scenes/10/media")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_scene_media(client, set_static_dir):
    """
    Test für GET /scenes/{scene_id}/media/{media_id}
    """
    response = client.get("/scenes/10/media/15")
    assert response.status_code == 200
    # FileResponse gibt Binärdaten zurück, daher kein JSON


def test_upload_scene_media(client, set_static_dir):
    """
    Test für POST /scenes/{scene_id}/upload
    """
    # Testdatei erstellen
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    
    # Datei hochladen
    response = client.post(
        "/scenes/10/upload",
        files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        data={"medientyp": "video"}
    )
    
    assert response.status_code == 200
    assert "id" in response.json()
    assert "dateipfad" in response.json()
    assert "medientyp" in response.json()
    assert response.json()["szene_id"] == 10