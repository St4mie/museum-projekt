


## Projektübersicht

Dieses Repository implementiert eine **Museum API**, mit der Besucher über eine Web-App Filmdaten abrufen sowie Bilder, Videos und Audiodateien ansehen können. Das Backend basiert auf **FastAPI**, **SQLAlchemy** und **MariaDB**, die Medienverarbeitung nutzt **Pillow** (für Thumbnails) und **ffmpeg** (für Video-Transcoding). Eine zentrale `config.py` steuert alle Umgebungsvariablen, sodass Entwicklungs- und Produktionsumgebungen sich nur durch ihre `.env`-Dateien unterscheiden.

---

## Inhaltsverzeichnis

1. [Voraussetzungen](#voraussetzungen)  
2. [Installation & Start](#installation--start)  
3. [Konfiguration](#konfiguration)  
4. [API Endpunkte](#api-endpunkte)  
5. [Tests](#tests)  
6. [Tipps & Tricks](#tipps--tricks)  
7. [Dokumentation](#dokumentation)  
8. [Weiterführende Links](#weiterführende-links)  

---

## Voraussetzungen

- **Docker & Docker Compose** (Version 1.29+ empfohlen)  
- **Python 3.11+** (lokal für Dev ohne Container)  
- **ffmpeg** (entweder im Container via `apt-get install -y ffmpeg` oder lokal installiert)  
- Ein moderner Browser im Kiosk-Modus (z. B. auf einem Raspberry Pi mit Touchscreen)

---

## Installation & Start

1. **Repo klonen**  
   ```bash
   git clone https://github.com/St4mie/museum-projekt.git
   cd museum-projekt
   ```

2. **Entwicklungs-.env anlegen**
   ```bash
   cp .env.example .env
   # .env nun mit lokalen Zugangsdaten füllen
   ```

3. **Docker Compose starten**
   ```bash
   docker compose up --build --profile dev -d
   ```

4. **API prüfen**
   ```bash
   curl http://localhost:8000/movies
   curl http://localhost:8000/media/images/movies/1
   ```

5. **Container-Logs ansehen**
   ```bash
   docker compose logs -f backend
   ```
## Konfiguration

Alle konfigurierbaren Werte liegen in `backend/app/config.py` und werden über Umgebungsvariablen gesteuert. Wichtige Einstellungen:

### Datenbank

- **DATABASE_URL**: Connection-String für den Runtime-User
- **DATABASE_URL_MIGRATE**: für Alembic-Migrationen

### Server

- **HOST & PORT**: Bind-Adresse und Port für Uvicorn

### Media

- **MEDIA_STATIC_PATH**: Pfad im Container zum Ordner mit Bildern, Videos, Audio
- **MEDIA_URL**: URL-Prefix zum Ausliefern der statischen Dateien

### CORS & Sicherheit

- **CORS_ALLOWED_ORIGINS**, **SECRET_KEY**, **ACCESS_TOKEN_EXPIRE_MINUTES**

### Feature-Flags

- **FEATURE_THUMBNAILS**: Thumbnail-Pipeline ein-/ausschalten

Änderungen an dieser Datei oder an der `.env` erfordern keinen Code-Rebuild, nur einen Neustart des Containers.

## API Endpunkte

### Filme (/movies)

- **GET /movies**  
  Listet alle Filme (paginierbar via ?skip=…&limit=…).

- **GET /movies/{id}**  
  Liefert ein einzelnes Film-Objekt.

- **POST /movies**  
  Legt einen neuen Film an.

- **POST /movies/import/{id}**  
  Importiert zusätzliche Metadaten aus Wikipedia.

### Medien (/media)

#### Bilder

- **GET /media/images/movies/{id}**  
  Listet alle Bilder des Films.

- **GET /media/images/movies/{id}/{datei}**  
  Gibt die Datei mit korrektem MIME-Type (image/jpeg/image/png).

#### Videos

- **GET /media/videos/movies/{id}**  
  Listet alle Videos des Films.

- **GET /media/videos/movies/{id}/{datei}**  
  Gibt die Videodatei zurück (video/mp4).

#### Audio

- **GET /media/audio/movies/{id}**  
  Listet alle Audiodateien des Films.

- **GET /media/audio/movies/{id}/{datei}**  
  Gibt die Audiodatei zurück (audio/mpeg).

#### Processing

- **POST /media/process/{id}**  
  Löst im Hintergrund das Erstellen von Thumbnails und Video-Transcoding (720p) aus.

## Tests

Unit-Tests im Ordner `backend/tests/`:

- **test_api.py**: CRUD-Tests für /movies
- **test_media_endpoints.py**: Endpunkt-Tests für /media
- **test_media_processor.py**: Generierung von Thumbnails & ffmpeg-Stubs

### Ausführung

```bash
# Im Container
docker compose exec backend pytest -q

# Watch-Mode (lokal ohne Container)
pytest --maxfail=1 --disable-warnings -q
```
## Tipps & Tricks

- **Hot-Reload**: Im Dev-Profil läuft Uvicorn mit --reload, Pycharm-Breakpoints funktionieren per Remote-Interpreter.
- **Datenbank-Migrations**: Alembic-Skripte liegen im Ordner `backend/alembic/`.
- **Media-Ordner**: Lege `.gitkeep` in jeden leeren Unterordner, damit Git die Struktur behält.

### Fehleranalyse:

- **404 bei Medien**: prüfe MEDIA_STATIC_PATH und Dateinamen.
- **ffmpeg-Fehler im Log**: kontrolliere, ob ffmpeg im Container installiert ist.

## Dokumentation

Die Projektdokumentation wurde in den `docs` Ordner verschoben und ist wie folgt strukturiert:

### Markdown-Dokumentation (`docs/markdown/`)

- **Documentation.md**: Ausführliche Projektdokumentation
- **Projektstruktur.md**: Übersicht der Projektstruktur
- **class overview.md**: Übersicht der Klassenstruktur
- **Datenmodell Film.md**: Dokumentation des Datenmodells für Filme
- **usecase.md**: Anwendungsfälle des Projekts
- **Museum-Projekt_Präsentation.md**: Präsentationsinhalte
- **Museum-Projekt_Präsentation_mit_Notizen.md**: Präsentation mit Notizen
- **Präsentation_README.md**: Anleitung zur Präsentation

### Diagramme (`docs/diagrams/`)

- **Projektmanagment.xml**: Diagramm zum Projektmanagement
- **Sequenzdiagramm Film anlegen.xml**: Sequenzdiagramm für das Anlegen eines Films
- **REST-API-Diagramm.xml**: Diagramm der REST-API
- **Datenmodell Film.xml**: Diagramm des Datenmodells für Filme
- **Codebeispielt Fast-Api.xml**: Codebeispiel für FastAPI
- **ORM-Datenmodell.xml**: Diagramm des ORM-Datenmodells

### Präsentationen (`docs/presentations/`)

- **Museum-Projekt_Präsentation.pptx**: PowerPoint-Präsentation

## Weiterführende Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Docker Compose Reference](https://docs.docker.com/compose/reference/)
- [Pillow (PIL) Documentation](https://pillow.readthedocs.io/en/stable/)
- [ffmpeg Documentation](https://ffmpeg.org/documentation.html)

---

Stand: Juni 2025 – erstellt im Rahmen des Museum Projekt Prototyps
