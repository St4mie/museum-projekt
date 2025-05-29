# backend/app/api/media.py

import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from app.config import MEDIA_STATIC_PATH     # Zentrale Config: Pfad zu statischen Medien
from app.services.media_processor import generate_image_thumbnail, transcode_video

router = APIRouter(prefix="/media", tags=["media"])

# Basis-Verzeichnis für statische Medien – kommt aus config.py
BASE: Path = MEDIA_STATIC_PATH

# Logger für Fehlersuche und Monitoring
logger = logging.getLogger("app.api.media")


def list_files(folder: Path) -> list[str]:
    """
    Gibt alle Dateinamen in einem Verzeichnis zurück.
    Wirft 404, wenn das Verzeichnis fehlt oder kein Ordner ist.
    """
    if not folder.exists() or not folder.is_dir():
        logger.warning(f"Folder not found: {folder}")
        raise HTTPException(status_code=404, detail=f"Folder not found: {folder}")
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
        logger.error(f"Image not found: {file_path}")
        raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
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
        logger.error(f"Video not found: {file_path}")
        raise HTTPException(status_code=404, detail=f"Video not found: {filename}")
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
        logger.error(f"Audio not found: {file_path}")
        raise HTTPException(status_code=404, detail=f"Audio not found: {filename}")
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

    return {"status": "processing started"}
