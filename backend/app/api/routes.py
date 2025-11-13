# backend/app/api/routes.py

import logging
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.config import settings
from app.services.wiki_importer import WikiImporter
from app.services.media_processor import generate_image_thumbnail, transcode_video
from app.models.movie import MovieORM
from app.models.movie_schema import (
    MovieCreate,
    Movie as MovieSchema,
)
from app.auth import get_current_user

# ──────────────────────────────────────────────────────────────────────────────
# ROUTER-DEFINITIONEN
# ──────────────────────────────────────────────────────────────────────────────

# Root-Router für allgemeine (öffentliche) Endpunkte
router = APIRouter(tags=["root"])

# Wiki-Router: alle Endpunkte unter /wiki, benötigen Authentifizierung
wiki_router = APIRouter(
    prefix="/wiki",
    tags=["wiki"],
    dependencies=[Depends(get_current_user)]
)

# Movie-Router: alle Endpunkte unter /movies, benötigen Authentifizierung
movie_router = APIRouter(
    prefix="/movies",
    tags=["movies"],
    dependencies=[Depends(get_current_user)]
)

# Media-Router: alle Endpunkte unter /media, keine Auth erforderlich
media_router = APIRouter(
    prefix="/media",
    tags=["media"]
)


# ──────────────────────────────────────────────────────────────────────────────
# DATENMODELLS (Pydantic) FÜR REQUEST UND RESPONSE
# ──────────────────────────────────────────────────────────────────────────────

class WikiImportRequest(BaseModel):
    """
    Request-Body für Bulk-Import: Liste von Film-Titeln.
    """
    titles: List[str]


class WikiImportStatus(BaseModel):
    """
    Response-Model für den Fortschritt des Wiki-Imports.
    """
    status: str
    processed: int
    errors: int


class MediaItem(BaseModel):
    """
    Response-Model für einzelne Media-Ressource.
    """
    id: int
    url: str
    type: str
    title: Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────────
# GLOBALE STATUS-VERFOLGUNG FÜR BACKGROUND-IMPORT
# ──────────────────────────────────────────────────────────────────────────────

# Initialer Status für Wiki-Import-Aufträge
import_status: Dict[str, int | str] = {
    "status": "idle",
    "processed": 0,
    "errors": 0
}


# ──────────────────────────────────────────────────────────────────────────────
# HELFERFUNKTIONEN FÜR MEDIA-VERZEICHNISSE
# ──────────────────────────────────────────────────────────────────────────────

# Basis-Pfad für statische Medien (Images, Videos, Audio)
BASE: Path = settings.media_static_path

logger = logging.getLogger("app.api.media")


def list_files(folder: Path) -> List[str]:
    """
    Gibt die Dateinamen in einem Ordner zurück.
    Wirft HTTP 404, wenn Ordner nicht existiert oder keine Verzeichnis ist.
    """
    if not folder.exists() or not folder.is_dir():
        logger.warning(f"Verzeichnis nicht gefunden: {folder}")
        raise HTTPException(status_code=404, detail=f"Ordner nicht gefunden: {folder}")
    # Nur reguläre Dateien, alphabetisch sortiert
    return sorted(p.name for p in folder.iterdir() if p.is_file())


def get_media_type(file_path: Path) -> str:
    """
    Ermittelt den MIME-Type anhand der Dateiendung.
    Unterstützt JPEG, PNG, MP4, MP3; sonst application/octet-stream.
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
    return "application/octet-stream"


# ──────────────────────────────────────────────────────────────────────────────
# ROOT-ENDPOINT
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/")
def read_root():
    """
    GET /
    Gibt eine einfache Willkommensnachricht zurück.
    """
    return {"message": "Willkommen bei der Museum API"}


# ──────────────────────────────────────────────────────────────────────────────
# MEDIA-ÜBERSICHT (Mock-Implementierung)
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/media")
def list_media():
    """
    GET /media
    Gibt eine Beispiel-Liste aller Medientypen zurück (Mock).
    """
    return {
        "items": [
            {"id": 1, "url": "/media/1", "type": "image", "title": "Sample Image"},
            {"id": 2, "url": "/media/2", "type": "video", "title": "Sample Video"},
            {"id": 3, "url": "/media/3", "type": "audio", "title": "Sample Audio"},
        ]
    }


@router.get("/media/{media_id}", response_model=MediaItem)
def get_media(media_id: int):
    """
    GET /media/{media_id}
    Gibt Details eines einzelnen Media-Elements zurück (Mock).
    """
    media_type = (
        "image"
        if media_id % 3 == 1
        else "video"
        if media_id % 3 == 2
        else "audio"
    )
    return {
        "id": media_id,
        "url": f"/static/media/{media_id}",
        "type": media_type,
        "title": f"Sample Media {media_id}",
    }


# ──────────────────────────────────────────────────────────────────────────────
# WIKI IMPORT (BULK + STATUS)
# ──────────────────────────────────────────────────────────────────────────────

@wiki_router.post("/import", status_code=201)
def import_from_wiki(
    request: WikiImportRequest,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db),
):
    """
    POST /wiki/import
    Startet den Bulk-Import von Filmdaten aus Wikipedia im Hintergrund.
    - Resettet den Global-Status
    - Legt Background-Task an, der Titel abarbeitet und in die DB schreibt
    """
    global import_status

    # Status-Reset
    import_status = {"status": "running", "processed": 0, "errors": 0}

    def import_titles(titles: List[str], session: Session):
        """
        Hintergrund-Task: für jeden Titel
        - prüft Duplikate
        - legt neuen MovieORM an
        - füllt Felder über WikiImporter
        - aktualisiert Status
        """
        global import_status

        for title in titles:
            try:
                # Nur neu anlegen, wenn nicht vorhanden
                existing = session.query(MovieORM).filter_by(titel=title).first()
                if not existing:
                    movie = MovieORM(titel=title, erscheinungsjahr=2000)
                    session.add(movie)
                    session.commit()
                    session.refresh(movie)

                    data = WikiImporter.fetch(title)
                    for key, value in data.items():
                        if value:
                            setattr(movie, key, value)
                    session.commit()

                import_status["processed"] += 1

            except Exception as e:
                import_status["errors"] += 1
                logger.error(f"Fehler beim Import von {title}: {e}")

        import_status["status"] = "completed"

    # Task zur Abarbeitung ins BackgroundTasks-Objekt einreihen
    background_tasks.add_task(import_titles, request.titles, session=db_session)

    return {
        "task_id": "123",  # kann später durch echte ID ersetzt werden
        "status": "started",
        "titles": len(request.titles),
    }


@wiki_router.get("/import/status", response_model=WikiImportStatus)
def get_import_status():
    """
    GET /wiki/import/status
    Gibt den aktuellen Status des Bulk-Imports zurück.
    """
    return import_status


# ──────────────────────────────────────────────────────────────────────────────
# FILM-ENDPOINTS (CRUD + Einzel-Import)
# ──────────────────────────────────────────────────────────────────────────────

@movie_router.get("/", response_model=List[MovieSchema])
def read_movies(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_db),
):
    """
    GET /movies/
    Liefert eine paginierte Liste aller Filme aus der DB.

    Raises:
        HTTPException: Bei Datenbankfehlern oder ungültigen Parametern
    """
    try:
        if skip < 0:
            raise HTTPException(status_code=400, detail="Parameter 'skip' muss größer oder gleich 0 sein")
        if limit <= 0:
            raise HTTPException(status_code=400, detail="Parameter 'limit' muss größer als 0 sein")

        return db_session.query(MovieORM).offset(skip).limit(limit).all()
    except HTTPException:
        # HTTPException direkt weiterleiten
        raise
    except Exception as e:
        # Andere Fehler in 500 Internal Server Error umwandeln
        logger.error(f"Datenbankfehler in read_movies: {str(e)}")
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Abrufen der Filme")


@movie_router.get("/{movie_id}", response_model=MovieSchema)
def read_movie(
    movie_id: int,
    db_session: Session = Depends(get_db),
):
    """
    GET /movies/{movie_id}
    Liefert einen einzelnen Film oder 404, wenn nicht gefunden.

    Raises:
        HTTPException: 
            - 400: Bei ungültiger Film-ID
            - 404: Wenn der Film nicht gefunden wird
            - 500: Bei Datenbankfehlern
    """
    try:
        if movie_id <= 0:
            raise HTTPException(status_code=400, detail="Film-ID muss größer als 0 sein")

        movie = db_session.query(MovieORM).filter(MovieORM.id == movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Film nicht gefunden")
        return movie
    except HTTPException:
        # HTTPException direkt weiterleiten
        raise
    except Exception as e:
        # Andere Fehler in 500 Internal Server Error umwandeln
        logger.error(f"Datenbankfehler in read_movie (ID {movie_id}): {str(e)}")
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Abrufen des Films")


@movie_router.post("/", response_model=MovieSchema, status_code=201)
def create_movie(
    movie: MovieCreate,
    db_session: Session = Depends(get_db),
):
    """
    POST /movies/
    Legt einen neuen Film an, wirft 409, wenn bereits vorhanden.

    Raises:
        HTTPException: 
            - 400: Bei ungültigen Filmdaten
            - 409: Wenn der Film bereits existiert
            - 422: Bei Validierungsfehlern
            - 500: Bei Datenbankfehlern
    """
    try:
        # Validierung der Eingabedaten
        if not movie.titel or not movie.titel.strip():
            raise HTTPException(status_code=400, detail="Filmtitel darf nicht leer sein")
        if movie.erscheinungsjahr and (movie.erscheinungsjahr < 1800 or movie.erscheinungsjahr > 2100):
            raise HTTPException(status_code=400, detail="Erscheinungsjahr muss zwischen 1800 und 2100 liegen")

        # Prüfen, ob der Film bereits existiert
        try:
            exists = (
                db_session.query(MovieORM)
                .filter_by(titel=movie.titel, erscheinungsjahr=movie.erscheinungsjahr)
                .first()
            )
            if exists:
                raise HTTPException(status_code=409, detail="Film existiert bereits")
        except Exception as db_error:
            logger.error(f"Datenbankfehler bei der Duplikatsprüfung: {str(db_error)}")
            raise HTTPException(status_code=500, detail="Datenbankfehler bei der Duplikatsprüfung")

        # Film anlegen
        try:
            movie_orm = MovieORM(**movie.model_dump())
            db_session.add(movie_orm)
            db_session.commit()
            db_session.refresh(movie_orm)
            return movie_orm
        except ValueError as ve:
            # Validierungsfehler beim Erstellen des ORM-Objekts
            raise HTTPException(status_code=422, detail=f"Validierungsfehler: {str(ve)}")
        except Exception as db_error:
            # Rollback bei Datenbankfehlern
            db_session.rollback()
            logger.error(f"Datenbankfehler beim Anlegen des Films: {str(db_error)}")
            raise HTTPException(status_code=500, detail="Datenbankfehler beim Anlegen des Films")
    except HTTPException:
        # HTTPException direkt weiterleiten
        raise
    except Exception as e:
        # Andere unerwartete Fehler
        logger.error(f"Unerwarteter Fehler in create_movie: {str(e)}")
        raise HTTPException(status_code=500, detail="Unerwarteter Fehler beim Anlegen des Films")


@movie_router.post("/import/{movie_id}", response_model=MovieSchema)
def import_movie_metadata(
    movie_id: int,
    db_session: Session = Depends(get_db),
):
    """
    POST /movies/import/{movie_id}
    Importiert fehlende Metadaten für einen vorhandenen Film aus Wikipedia.

    Raises:
        HTTPException: 
            - 400: Bei ungültiger Film-ID
            - 404: Wenn der Film nicht gefunden wird
            - 422: Bei Validierungsfehlern
            - 500: Bei Datenbankfehlern
            - 502: Bei Fehlern beim Wiki-Import
            - 503: Bei Netzwerkproblemen
    """
    try:
        if movie_id <= 0:
            raise HTTPException(status_code=400, detail="Film-ID muss größer als 0 sein")

        # Film aus der Datenbank abrufen
        try:
            film = db_session.query(MovieORM).filter(MovieORM.id == movie_id).first()
            if not film:
                raise HTTPException(status_code=404, detail="Film nicht gefunden")

            # Prüfen, ob der Film einen Titel hat
            if not film.titel or not film.titel.strip():
                raise HTTPException(status_code=422, detail="Film hat keinen Titel für den Import")
        except HTTPException:
            raise
        except Exception as db_error:
            logger.error(f"Datenbankfehler beim Abrufen des Films (ID {movie_id}): {str(db_error)}")
            raise HTTPException(status_code=500, detail="Datenbankfehler beim Abrufen des Films")

        # Daten aus Wikipedia importieren
        try:
            data = WikiImporter.fetch(film.titel)

            # Nur leere Felder überschreiben
            for key, value in data.items():
                if getattr(film, key, None) in (None, "", []):
                    setattr(film, key, value)

            # Änderungen speichern
            try:
                db_session.commit()
                db_session.refresh(film)
                return film
            except Exception as commit_error:
                db_session.rollback()
                logger.error(f"Datenbankfehler beim Speichern der importierten Daten: {str(commit_error)}")
                raise HTTPException(status_code=500, detail="Datenbankfehler beim Speichern der importierten Daten")

        except ValueError as ve:
            # Validierungsfehler beim Import
            logger.warning(f"Validierungsfehler beim Import für Film {movie_id}: {str(ve)}")
            # Film zur manuellen Review markieren
            try:
                film.pruefung = True
                db_session.commit()
            except Exception:
                db_session.rollback()
            raise HTTPException(status_code=422, detail=f"Validierungsfehler beim Import: {str(ve)}")

        except ConnectionError as ce:
            # Netzwerkprobleme
            logger.error(f"Netzwerkfehler beim Import für Film {movie_id}: {str(ce)}")
            # Film zur manuellen Review markieren
            try:
                film.pruefung = True
                db_session.commit()
            except Exception:
                db_session.rollback()
            raise HTTPException(status_code=503, detail=f"Netzwerkfehler beim Import: {str(ce)}")

        except Exception as import_error:
            # Andere Import-Fehler
            logger.error(f"Fehler beim Wiki-Import für Film {movie_id}: {str(import_error)}")
            # Film zur manuellen Review markieren
            try:
                film.pruefung = True
                db_session.commit()
            except Exception:
                db_session.rollback()
            raise HTTPException(status_code=502, detail=f"Fehler beim Wiki-Import: {str(import_error)}")

    except HTTPException:
        # HTTPException direkt weiterleiten
        raise
    except Exception as e:
        # Unerwartete Fehler
        logger.error(f"Unerwarteter Fehler in import_movie_metadata: {str(e)}")
        raise HTTPException(status_code=500, detail="Unerwarteter Fehler beim Import der Filmdaten")


# ──────────────────────────────────────────────────────────────────────────────
# MEDIA-ENDPOINTS (IMAGES, VIDEOS, AUDIO, PROCESSING)
# ──────────────────────────────────────────────────────────────────────────────

# --- Bilder ---

@media_router.get("/images/movies/{movie_id}", response_model=List[str])
def list_movie_images(movie_id: int):
    """
    GET /media/images/movies/{movie_id}
    Listet alle Bilder zu einem Film auf.
    """
    folder = BASE / "images" / "movies" / str(movie_id)
    return list_files(folder)


@media_router.get("/images/movies/{movie_id}/{filename}")
def get_movie_image(movie_id: int, filename: str):
    """
    GET /media/images/movies/{movie_id}/{filename}
    Liefert eine Bilddatei zurück, wirft 404, wenn nicht vorhanden.
    """
    file_path = BASE / "images" / "movies" / str(movie_id) / filename
    if not file_path.exists() or not file_path.is_file():
        logger.error(f"Bild nicht gefunden: {file_path}")
        raise HTTPException(status_code=404, detail=f"Bild nicht gefunden: {filename}")
    return FileResponse(path=file_path, media_type=get_media_type(file_path))


# --- Videos ---

@media_router.get("/videos/movies/{movie_id}", response_model=List[str])
def list_movie_videos(movie_id: int):
    """
    GET /media/videos/movies/{movie_id}
    Listet alle Videodateien zu einem Film auf.
    """
    folder = BASE / "videos" / "movies" / str(movie_id)
    return list_files(folder)


@media_router.get("/videos/movies/{movie_id}/{filename}")
def get_movie_video(movie_id: int, filename: str):
    """
    GET /media/videos/movies/{movie_id}/{filename}
    Liefert eine Videodatei zurück, wirft 404, wenn nicht vorhanden.
    """
    file_path = BASE / "videos" / "movies" / str(movie_id) / filename
    if not file_path.exists() or not file_path.is_file():
        logger.error(f"Video nicht gefunden: {file_path}")
        raise HTTPException(status_code=404, detail=f"Video nicht gefunden: {filename}")
    return FileResponse(path=file_path, media_type=get_media_type(file_path))


# --- Audio ---

@media_router.get("/audio/movies/{movie_id}", response_model=List[str])
def list_movie_audio(movie_id: int):
    """
    GET /media/audio/movies/{movie_id}
    Listet alle Audiodateien zu einem Film auf.
    """
    folder = BASE / "audio" / "movies" / str(movie_id)
    return list_files(folder)


@media_router.get("/audio/movies/{movie_id}/{filename}")
def get_movie_audio(movie_id: int, filename: str):
    """
    GET /media/audio/movies/{movie_id}/{filename}
    Liefert eine Audiodatei zurück, wirft 404, wenn nicht vorhanden.
    """
    file_path = BASE / "audio" / "movies" / str(movie_id) / filename
    if not file_path.exists() or not file_path.is_file():
        logger.error(f"Audio nicht gefunden: {file_path}")
        raise HTTPException(status_code=404, detail=f"Audio nicht gefunden: {filename}")
    return FileResponse(path=file_path, media_type=get_media_type(file_path))


# --- Media-Processing (Thumbnails, Transcoding) ---

@media_router.post("/process/{movie_id}")
def process_media(movie_id: int, background_tasks: BackgroundTasks):
    """
    POST /media/process/{movie_id}
    Startet Bild- und Videoverarbeitung im Hintergrund:
      - erzeugt Thumbnails (200×200) für Bilder
      - transcodiert Videos auf 720p

    Raises:
        HTTPException: 
            - 400: Bei ungültiger Film-ID
            - 404: Wenn keine Mediendateien gefunden werden
            - 500: Bei unerwarteten Fehlern
    """
    try:
        if movie_id <= 0:
            raise HTTPException(status_code=400, detail="Film-ID muss größer als 0 sein")

        # Zähler für gefundene Mediendateien
        media_count = 0

        # Bilder-Verarbeitung einreihen
        try:
            images_dir = BASE / "images" / "movies" / str(movie_id)
            if images_dir.exists() and images_dir.is_dir():
                for img in images_dir.iterdir():
                    if img.is_file():
                        # Prüfen, ob es sich um ein Bild handelt
                        if img.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                            background_tasks.add_task(generate_image_thumbnail, movie_id, img.name)
                            media_count += 1
                        else:
                            logger.warning(f"Überspringe Nicht-Bild-Datei: {img}")
        except Exception as img_error:
            logger.error(f"Fehler beim Einreihen der Bildverarbeitung: {str(img_error)}")
            # Wir werfen hier keine Exception, um die Videoverarbeitung trotzdem zu versuchen

        # Video-Verarbeitung einreihen
        try:
            videos_dir = BASE / "videos" / "movies" / str(movie_id)
            if videos_dir.exists() and videos_dir.is_dir():
                for vid in videos_dir.iterdir():
                    if vid.is_file():
                        # Prüfen, ob es sich um ein Video handelt
                        if vid.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                            background_tasks.add_task(transcode_video, movie_id, vid.name, "720p")
                            media_count += 1
                        else:
                            logger.warning(f"Überspringe Nicht-Video-Datei: {vid}")
        except Exception as vid_error:
            logger.error(f"Fehler beim Einreihen der Videoverarbeitung: {str(vid_error)}")
            # Wir werfen hier keine Exception, wenn wir bereits Bilder gefunden haben

        # Prüfen, ob Mediendateien gefunden wurden
        if media_count == 0:
            raise HTTPException(status_code=404, detail="Keine Mediendateien für diesen Film gefunden")

        return {
            "status": "Verarbeitung gestartet", 
            "media_count": media_count,
            "message": f"Verarbeitung von {media_count} Mediendateien gestartet"
        }

    except HTTPException:
        # HTTPException direkt weiterleiten
        raise
    except Exception as e:
        # Unerwartete Fehler
        logger.error(f"Unerwarteter Fehler in process_media: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Starten der Medienverarbeitung: {str(e)}")
