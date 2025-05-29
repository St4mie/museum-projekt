# backend/app/services/media_processor.py

from pathlib import Path
from PIL import Image
import subprocess
import shutil
import logging

# Zentrale Konfiguration importieren
from app.config import MEDIA_STATIC_PATH as BASE  # Filesystem-Pfad für Medien

# Logger für Fehlersuche
logger = logging.getLogger("app.services.media_processor")


def generate_image_thumbnail(movie_id: int, filename: str, size=(200, 200)) -> Path:
    """
    Erzeugt ein Vorschaubild (Thumbnail) für ein Bild:
    1. Quelle: BASE/images/movies/{movie_id}/{filename}
    2. Ziel:   BASE/images/movies/{movie_id}/thumbs/{filename}
    """
    src = BASE / "images" / "movies" / str(movie_id) / filename
    dest_dir = BASE / "images" / "movies" / str(movie_id) / "thumbs"
    dest_dir.mkdir(parents=True, exist_ok=True)

    thumb_path = dest_dir / filename
    with Image.open(src) as img:
        img.thumbnail(size)
        img.save(thumb_path, format=img.format)
    return thumb_path


def transcode_video(movie_id: int, filename: str, resolution="720p") -> Path:
    """
    Transkodiert ein Video mit ffmpeg:
    1. Quelle: BASE/videos/movies/{movie_id}/{filename}
    2. Ziel:   BASE/videos/movies/{movie_id}/{resolution}/{filename}
    Falls ffmpeg fehlt oder fehlschlägt, wird als Fallback
    die Quelldatei kopiert.
    """
    src = BASE / "videos" / "movies" / str(movie_id) / filename

    # Auflösungs-Mapping
    res_map = {"720p": "1280:720", "480p": "854:480"}
    size = res_map.get(resolution, res_map["480p"])

    dest_dir = BASE / "videos" / "movies" / str(movie_id) / resolution
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / filename
    cmd = [
        "ffmpeg",
        "-i", str(src),
        "-vf", f"scale={size}",
        "-c:a", "copy",
        str(dest)
    ]

    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        logger.warning(f"Transcoding failed ({e!r}), copying original as fallback")
        shutil.copy2(src, dest)
    return dest
