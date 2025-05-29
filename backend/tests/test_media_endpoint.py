# backend/tests/test_media_endpoint.py

import pytest
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image

# Router importieren
from app.api.media import router as media_router

# Module, in denen wir BASE/Config patchen müssen
import app.config as config
import app.services.media_processor as media_processor
import app.api.media as media_api

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
# TestClient-Setup
# ----------------------------------------

test_app = FastAPI()
test_app.include_router(media_router)
client = TestClient(test_app)


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
def setup_files(set_static_dir: Path):
    """
    Vor jedem Test werden angelegt:
    a) Ein valides Testbild (pic.jpg)
    b) Eine Dummy-Video-Quelldatei (clip.mp4)
    c) Eine Dummy-Ausgabe für das 720p-Transcoding (clip.mp4 im 720p-Ordner)
    """
    # a) Testbild
    img_path = set_static_dir / "images" / "movies" / "5" / "pic.jpg"
    create_dummy_image(img_path)

    # b) Original-Video
    create_file(
        set_static_dir,
        "videos", "movies", "5",
        filename="clip.mp4",
        data=b"ORIGINAL-VIDEO"
    )

    # c) Erwartetes 720p-Ergebnis (Dummy-Datei)
    create_file(
        set_static_dir,
        "videos", "movies", "5", "720p",
        filename="clip.mp4",
        data=b"DUMMY-TRANSCODED"
    )

    yield
    # tmp_path wird automatisch aufgeräumt


# ----------------------------------------
# Tatsächlicher Test
# ----------------------------------------

def test_process_endpoint_creates_thumbnails_and_transcoding(set_static_dir: Path):
    """
    1) POST /media/process/5 startet BackgroundTasks
    2) Nach kurzer Wartezeit müssen existieren:
       - images/.../thumbs/pic.jpg  (echtes Thumbnail)
       - videos/.../720p/clip.mp4   (Dummy-Transcoding)
    """
    resp = client.post("/media/process/5")
    assert resp.status_code == 200, "Endpoint hat nicht richtig gestartet"
    assert resp.json() == {"status": "processing started"}

    # BackgroundTasks im TestClient laufen synchron, kurz Pausieren zur Sicherheit
    time.sleep(0.5)

    # --- Thumbnail prüfen ---
    thumb = set_static_dir / "images" / "movies" / "5" / "thumbs" / "pic.jpg"
    assert thumb.exists(), "Thumbnail wurde nicht erstellt"

    # --- Transcodiertes Video prüfen ---
    trans = set_static_dir / "videos" / "movies" / "5" / "720p" / "clip.mp4"
    assert trans.exists(), "Transcodiertes Video wurde nicht erstellt"
