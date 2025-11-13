# backend/app/services/media_processor.py

from pathlib import Path
from PIL import Image
import subprocess
import shutil
import logging
from typing import Literal

# Zentrale Konfiguration importieren
from app.config import settings  # Settings-Instanz importieren

# Basisverzeichnis für Medien kommt jetzt aus den Einstellungen
BASE: Path = settings.media_static_path

# Logger für Debugging
logger = logging.getLogger("app.services.media_processor")


def generate_image_thumbnail(movie_id: int, filename: str, size=(200, 200)) -> Path:
    """
    Erzeugt ein Thumbnail für ein Bild:
    1. Quelle: BASE/images/movies/{movie_id}/{filename}
    2. Ziel: BASE/images/movies/{movie_id}/thumbs/{filename}

    Raises:
        ValueError: Wenn movie_id oder filename ungültig sind
        FileNotFoundError: Wenn die Quelldatei nicht existiert
        PermissionError: Wenn keine Schreibrechte für das Zielverzeichnis vorliegen
        IOError: Bei Problemen mit dem Dateizugriff
        Exception: Bei anderen Fehlern während der Bildverarbeitung
    """
    if not movie_id or movie_id <= 0:
        raise ValueError(f"Ungültige Film-ID: {movie_id}")
    if not filename or not filename.strip():
        raise ValueError("Dateiname darf nicht leer sein")

    try:
        src = BASE / "images" / "movies" / str(movie_id) / filename

        # Prüfen, ob die Quelldatei existiert
        if not src.exists():
            raise FileNotFoundError(f"Quelldatei nicht gefunden: {src}")
        if not src.is_file():
            raise FileNotFoundError(f"Pfad ist keine Datei: {src}")

        dest_dir = BASE / "images" / "movies" / str(movie_id) / "thumbs"
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise PermissionError(f"Keine Berechtigung zum Erstellen des Verzeichnisses: {dest_dir}")
        except Exception as e:
            raise IOError(f"Fehler beim Erstellen des Verzeichnisses: {str(e)}")

        thumb_path = dest_dir / filename
        try:
            with Image.open(src) as img:
                img.thumbnail(size)
                img.save(thumb_path, format=img.format)
            return thumb_path
        except IOError as e:
            raise IOError(f"Fehler beim Öffnen oder Speichern des Bildes: {str(e)}")
        except Exception as e:
            raise Exception(f"Unerwarteter Fehler bei der Bildverarbeitung: {str(e)}")
    except (ValueError, FileNotFoundError, PermissionError, IOError) as e:
        # Spezifische Fehler weiterleiten
        logger.error(f"Fehler bei generate_image_thumbnail: {str(e)}")
        raise e
    except Exception as e:
        # Alle anderen Fehler protokollieren und weiterleiten
        logger.error(f"Unbehandelter Fehler bei generate_image_thumbnail: {str(e)}")
        raise Exception(f"Fehler bei der Thumbnail-Generierung: {str(e)}")


def transcode_video(movie_id: int, filename: str, resolution="720p") -> Path:
    """
    Transkodiert ein Video mit ffmpeg:
    1. Quelle: BASE/videos/movies/{movie_id}/{filename}
    2. Ziel: BASE/videos/movies/{movie_id}/{resolution}/{filename}
    Wenn ffmpeg fehlt oder fehlschlägt, wird die Quelldatei als Fallback kopiert.

    Raises:
        ValueError: Wenn movie_id, filename oder resolution ungültig sind
        FileNotFoundError: Wenn die Quelldatei nicht existiert
        PermissionError: Wenn keine Schreibrechte für das Zielverzeichnis vorliegen
        IOError: Bei Problemen mit dem Dateizugriff
        RuntimeError: Wenn die Transkodierung fehlschlägt und der Fallback nicht funktioniert
        Exception: Bei anderen unerwarteten Fehlern
    """
    if not movie_id or movie_id <= 0:
        raise ValueError(f"Ungültige Film-ID: {movie_id}")
    if not filename or not filename.strip():
        raise ValueError("Dateiname darf nicht leer sein")
    if not resolution or not resolution.strip():
        raise ValueError("Auflösung darf nicht leer sein")

    try:
        src = BASE / "videos" / "movies" / str(movie_id) / filename

        # Prüfen, ob die Quelldatei existiert
        if not src.exists():
            raise FileNotFoundError(f"Quelldatei nicht gefunden: {src}")
        if not src.is_file():
            raise FileNotFoundError(f"Pfad ist keine Datei: {src}")

        # Auflösungszuordnung
        res_map = {"720p": "1280:720", "480p": "854:480"}
        size = res_map.get(resolution, res_map["480p"])

        dest_dir = BASE / "videos" / "movies" / str(movie_id) / resolution
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise PermissionError(f"Keine Berechtigung zum Erstellen des Verzeichnisses: {dest_dir}")
        except Exception as e:
            raise IOError(f"Fehler beim Erstellen des Verzeichnisses: {str(e)}")

        dest = dest_dir / filename
        cmd = [
            "ffmpeg",
            "-i", str(src),
            "-vf", f"scale={size}",
            "-c:a", "copy",
            str(dest)
        ]

        try:
            # Versuche, ffmpeg auszuführen
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return dest
        except subprocess.CalledProcessError as e:
            # ffmpeg-Fehler protokollieren
            logger.warning(f"Transkodierung fehlgeschlagen: {e.stderr}")
            logger.info("Versuche Fallback: Kopiere Original")
            try:
                # Fallback: Original kopieren
                shutil.copy2(src, dest)
                return dest
            except Exception as copy_error:
                # Wenn auch der Fallback fehlschlägt
                raise RuntimeError(f"Transkodierung und Fallback fehlgeschlagen: {str(copy_error)}")
        except FileNotFoundError:
            # ffmpeg nicht gefunden
            logger.warning("ffmpeg nicht gefunden, verwende Fallback")
            try:
                # Fallback: Original kopieren
                shutil.copy2(src, dest)
                return dest
            except Exception as copy_error:
                # Wenn auch der Fallback fehlschlägt
                raise RuntimeError(f"ffmpeg nicht gefunden und Fallback fehlgeschlagen: {str(copy_error)}")
    except (ValueError, FileNotFoundError, PermissionError, IOError, RuntimeError) as e:
        # Spezifische Fehler protokollieren und weiterleiten
        logger.error(f"Fehler bei transcode_video: {str(e)}")
        raise e
    except Exception as e:
        # Alle anderen Fehler protokollieren und weiterleiten
        logger.error(f"Unbehandelter Fehler bei transcode_video: {str(e)}")
        raise Exception(f"Fehler bei der Video-Transkodierung: {str(e)}")


def process_scene_media(szene_id: int, film_id: int, dateipfad: str, medientyp: Literal["audio", "video"]) -> Path:
    """
    Verarbeitet Mediendateien für Szenen:
    1. Für Audio: Kopiert die Datei in das entsprechende Verzeichnis
    2. Für Video: Transkodiert das Video mit ffmpeg

    Args:
        szene_id: ID der Szene
        film_id: ID des Films
        dateipfad: Pfad zur Mediendatei
        medientyp: Typ des Mediums (audio/video)

    Returns:
        Pfad zur verarbeiteten Mediendatei

    Raises:
        ValueError: Wenn Parameter ungültig sind oder Medientyp nicht unterstützt wird
        FileNotFoundError: Wenn die Quelldatei nicht existiert
        PermissionError: Wenn keine Schreibrechte für Verzeichnisse vorliegen
        IOError: Bei Problemen mit dem Dateizugriff
        RuntimeError: Wenn die Verarbeitung fehlschlägt
        Exception: Bei anderen unerwarteten Fehlern
    """
    if not szene_id or szene_id <= 0:
        raise ValueError(f"Ungültige Szenen-ID: {szene_id}")
    if not film_id or film_id <= 0:
        raise ValueError(f"Ungültige Film-ID: {film_id}")
    if not dateipfad or not dateipfad.strip():
        raise ValueError("Dateipfad darf nicht leer sein")
    if medientyp not in ["audio", "video"]:
        raise ValueError(f"Nicht unterstützter Medientyp: {medientyp}")

    try:
        src = Path(dateipfad)

        # Prüfen, ob die Quelldatei existiert
        if not src.exists():
            raise FileNotFoundError(f"Quelldatei nicht gefunden: {src}")
        if not src.is_file():
            raise FileNotFoundError(f"Pfad ist keine Datei: {src}")

        filename = src.name

        if medientyp == "audio":
            dest_dir = BASE / "audio" / "movies" / str(film_id) / str(szene_id)
            try:
                dest_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                raise PermissionError(f"Keine Berechtigung zum Erstellen des Verzeichnisses: {dest_dir}")
            except Exception as e:
                raise IOError(f"Fehler beim Erstellen des Verzeichnisses: {str(e)}")

            dest = dest_dir / filename
            try:
                shutil.copy2(src, dest)
                return dest
            except PermissionError:
                raise PermissionError(f"Keine Berechtigung zum Kopieren der Datei nach: {dest}")
            except Exception as e:
                raise IOError(f"Fehler beim Kopieren der Audiodatei: {str(e)}")

        elif medientyp == "video":
            try:
                # Für Videos verwenden wir die bestehende transcode_video-Funktion
                # Zuerst in das Quellverzeichnis kopieren
                temp_dir = BASE / "videos" / "movies" / str(film_id)
                try:
                    temp_dir.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    raise PermissionError(f"Keine Berechtigung zum Erstellen des Verzeichnisses: {temp_dir}")
                except Exception as e:
                    raise IOError(f"Fehler beim Erstellen des temporären Verzeichnisses: {str(e)}")

                temp_path = temp_dir / filename
                try:
                    shutil.copy2(src, temp_path)
                except Exception as e:
                    raise IOError(f"Fehler beim Kopieren der Videodatei ins temporäre Verzeichnis: {str(e)}")

                # Dann transkodieren
                try:
                    transcoded = transcode_video(film_id, filename)
                except Exception as e:
                    raise RuntimeError(f"Fehler bei der Transkodierung: {str(e)}")

                # Ein szenenspezifisches Verzeichnis erstellen und die transkodierte Datei dorthin kopieren
                scene_dir = BASE / "videos" / "movies" / str(film_id) / str(szene_id)
                try:
                    scene_dir.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    raise PermissionError(f"Keine Berechtigung zum Erstellen des Szenenverzeichnisses: {scene_dir}")
                except Exception as e:
                    raise IOError(f"Fehler beim Erstellen des Szenenverzeichnisses: {str(e)}")

                final_path = scene_dir / filename
                try:
                    shutil.copy2(transcoded, final_path)
                    return final_path
                except Exception as e:
                    raise IOError(f"Fehler beim Kopieren der transkodierten Datei ins Szenenverzeichnis: {str(e)}")
            except Exception as e:
                raise RuntimeError(f"Fehler bei der Videoverarbeitung: {str(e)}")
        else:
            # Diese Prüfung ist redundant, da wir bereits am Anfang prüfen, aber für die Vollständigkeit
            raise ValueError(f"Nicht unterstützter Medientyp: {medientyp}")
    except (ValueError, FileNotFoundError, PermissionError, IOError, RuntimeError) as e:
        # Spezifische Fehler protokollieren und weiterleiten
        logger.error(f"Fehler bei process_scene_media: {str(e)}")
        raise e
    except Exception as e:
        # Alle anderen Fehler protokollieren und weiterleiten
        logger.error(f"Unbehandelter Fehler bei process_scene_media: {str(e)}")
        raise Exception(f"Fehler bei der Medienverarbeitung für Szene: {str(e)}")
