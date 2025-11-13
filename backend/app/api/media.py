# backend/app/api/media.py

import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings      # Settings-Instanz importieren
from app.services.media_processor import generate_image_thumbnail, transcode_video, process_scene_media
from app.db import get_db
from app.models import SzeneORM, MediumORM

router = APIRouter(prefix="/media", tags=["media"])

# Basis-Verzeichnis für statische Medien – kommt nun aus settings
BASE: Path = settings.media_static_path

# Logger für Fehlersuche und Monitoring
logger = logging.getLogger("app.api.media")


def list_files(folder: Path) -> list[str]:
    """
    Gibt alle Dateinamen in einem Verzeichnis zurück.
    Wirft 404, wenn das Verzeichnis fehlt oder kein Ordner ist.
    """
    if not folder.exists() or not folder.is_dir():
        logger.warning(f"Ordner nicht gefunden: {folder}")
        raise HTTPException(status_code=404, detail=f"Ordner nicht gefunden: {folder}")
    return sorted(p.name for p in folder.iterdir() if p.is_file())


def get_media_type(file_path: Path) -> str:
    """
    Bestimmt den MIME-Type anhand der Dateiendung.
    Unterstützt: .jpg/.jpeg, .png, .mp4, .mp3
    """
    ext = file_path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".mp4":
        return "video/mp4"
    if ext == ".mp3":
        return "audio/mpeg"
    # Fallback für unbekannte Typen
    return "application/octet-stream"


# --- Bilder Endpoints ---

@router.get("/images/movies/{movie_id}", response_model=list[str])
def list_movie_images(movie_id: int):
    """
    Listet alle Bilddateien für einen Film.
    """
    folder = BASE / "images" / "movies" / str(movie_id)
    return list_files(folder)


@router.get("/images/movies/{movie_id}/{filename}")
def get_movie_image(movie_id: int, filename: str):
    """
    Liefert eine einzelne Bilddatei aus.
    """
    file_path = BASE / "images" / "movies" / str(movie_id) / filename
    if not file_path.exists() or not file_path.is_file():
        logger.error(f"Bild nicht gefunden: {file_path}")
        raise HTTPException(status_code=404, detail=f"Bild nicht gefunden: {filename}")
    return FileResponse(path=file_path, media_type=get_media_type(file_path))


# --- Videos Endpoints ---

@router.get("/videos/movies/{movie_id}", response_model=list[str])
def list_movie_videos(movie_id: int):
    """
    Listet alle Videodateien für einen Film.
    """
    folder = BASE / "videos" / "movies" / str(movie_id)
    return list_files(folder)


@router.get("/videos/movies/{movie_id}/{filename}")
def get_movie_video(movie_id: int, filename: str):
    """
    Liefert eine einzelne Videodatei aus.
    """
    file_path = BASE / "videos" / "movies" / str(movie_id) / filename
    if not file_path.exists() or not file_path.is_file():
        logger.error(f"Video nicht gefunden: {file_path}")
        raise HTTPException(status_code=404, detail=f"Video nicht gefunden: {filename}")
    return FileResponse(path=file_path, media_type=get_media_type(file_path))


# --- Audio Endpoints ---

@router.get("/audio/movies/{movie_id}", response_model=list[str])
def list_movie_audio(movie_id: int):
    """
    Listet alle Audiodateien für einen Film.
    """
    folder = BASE / "audio" / "movies" / str(movie_id)
    return list_files(folder)


@router.get("/audio/movies/{movie_id}/{filename}")
def get_movie_audio(movie_id: int, filename: str):
    """
    Liefert eine einzelne Audiodatei aus.
    """
    file_path = BASE / "audio" / "movies" / str(movie_id) / filename
    if not file_path.exists() or not file_path.is_file():
        logger.error(f"Audio nicht gefunden: {file_path}")
        raise HTTPException(status_code=404, detail=f"Audio nicht gefunden: {filename}")
    return FileResponse(path=file_path, media_type=get_media_type(file_path))


# --- Media Processing Endpoint ---

@router.post("/process/{movie_id}")
def process_media(movie_id: int, background_tasks: BackgroundTasks):
    """
    Startet Thumbnail-Erzeugung und Video-Transcoding im Hintergrund:
    - Bilder → Thumbnails (200×200 px)
    - Videos → 720p MP4
    """
    # Bilder verarbeiten
    images_dir = BASE / "images" / "movies" / str(movie_id)
    if images_dir.exists() and images_dir.is_dir():
        for img in images_dir.iterdir():
            if img.is_file():
                background_tasks.add_task(generate_image_thumbnail, movie_id, img.name)

    # Videos verarbeiten
    videos_dir = BASE / "videos" / "movies" / str(movie_id)
    if videos_dir.exists() and videos_dir.is_dir():
        for vid in videos_dir.iterdir():
            if vid.is_file():
                background_tasks.add_task(transcode_video, movie_id, vid.name, "720p")

    return {"status": "Verarbeitung gestartet"}


# --- Scene Media Endpoints ---

@router.get("/scenes/{scene_id}/media", response_model=list[str])
def list_scene_media(scene_id: int, db_session: Session = Depends(get_db)):
    """
    Listet alle Mediendateien für eine Szene.
    """
    # Prüfen, ob die Szene existiert
    szene = db_session.query(SzeneORM).filter(SzeneORM.id == scene_id).first()
    if not szene:
        raise HTTPException(status_code=404, detail=f"Szene mit ID {scene_id} nicht gefunden")

    # Medien aus der Datenbank abrufen
    medien = db_session.query(MediumORM).filter(MediumORM.szene_id == scene_id).all()
    return [medium.dateipfad for medium in medien]


@router.get("/scenes/{scene_id}/media/{media_id}")
def get_scene_media(scene_id: int, media_id: int, db_session: Session = Depends(get_db)):
    """
    Liefert eine einzelne Mediendatei einer Szene aus.
    """
    # Medium aus der Datenbank abrufen
    medium = db_session.query(MediumORM).filter(
        MediumORM.id == media_id,
        MediumORM.szene_id == scene_id
    ).first()

    if not medium:
        raise HTTPException(status_code=404, detail=f"Medium mit ID {media_id} für Szene {scene_id} nicht gefunden")

    # Pfad zur Datei ermitteln
    file_path = Path(medium.dateipfad)
    if not file_path.exists() or not file_path.is_file():
        logger.error(f"Mediendatei nicht gefunden: {file_path}")
        raise HTTPException(status_code=404, detail=f"Mediendatei nicht gefunden: {file_path}")

    return FileResponse(path=file_path, media_type=get_media_type(file_path))


@router.post("/scenes/{scene_id}/upload")
async def upload_scene_media(
    scene_id: int,
    medientyp: str = Form(...),
    file: UploadFile = File(...),
    db_session: Session = Depends(get_db)
):
    """
    Lädt eine Mediendatei für eine Szene hoch und verarbeitet sie.
    """
    # Prüfen, ob die Szene existiert
    szene = db_session.query(SzeneORM).filter(SzeneORM.id == scene_id).first()
    if not szene:
        raise HTTPException(status_code=404, detail=f"Szene mit ID {scene_id} nicht gefunden")

    # Prüfen, ob der Medientyp gültig ist
    if medientyp not in ["audio", "video"]:
        raise HTTPException(status_code=400, detail=f"Ungültiger Medientyp: {medientyp}")

    # Temporäre Datei speichern
    temp_dir = BASE / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    temp_file = temp_dir / file.filename
    with open(temp_file, "wb") as f:
        content = await file.read()
        f.write(content)

    # Datei verarbeiten
    try:
        processed_path = process_scene_media(scene_id, szene.film_id, str(temp_file), medientyp)

        # In Datenbank speichern
        medium = MediumORM(
            szene_id=scene_id,
            dateipfad=str(processed_path),
            medientyp=medientyp
        )
        db_session.add(medium)
        db_session.commit()
        db_session.refresh(medium)

        return {
            "id": medium.id,
            "szene_id": medium.szene_id,
            "dateipfad": medium.dateipfad,
            "medientyp": medium.medientyp
        }
    except Exception as e:
        logger.error(f"Fehler beim Verarbeiten der Mediendatei: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Verarbeiten der Mediendatei: {str(e)}")
    finally:
        # Temporäre Datei löschen
        if temp_file.exists():
            temp_file.unlink()
