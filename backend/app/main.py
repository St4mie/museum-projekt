# backend/app/main.py

import time
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager

from app.db import engine, Base
from app.api.routes import (
    router        as root_router,    # Root-Router importieren (GET /, /media-mock)
    wiki_router,                     # Wiki-Router importieren (/wiki-Endpunkte)
    movie_router,                    # Movie-Router importieren (/movies-CRUD)
    media_router                     # Media-Router importieren (/media-Datei-Oberfläche)
)
from app.config import settings       # Settings für DB, Pfade, URLs, Logging, etc.

# -----------------------------------------------------------------------------
# LIFESPAN-HANDLER
# -----------------------------------------------------------------------------
# Wartet beim Start auf die DB, legt Tabellen an und führt bei Shutdown Cleanup aus.
@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Lifespan-Handler:
      1. Bis zu 5x auf DB-Verbindung versuchen (z.B. bei Docker-Start).
      2. ORM-Metadaten in der DB erzeugen (create_all).
      3. App-Lifecycle (yield).
      4. Optional: Aufräumarbeiten nach Shutdown.
    """
    for attempt in range(1, 6):
        try:
            with engine.connect():
                break
        except OperationalError:
            logging.warning(f"DB nicht bereit, versuche erneut ({attempt}/5)…")
            time.sleep(2)
    else:
        logging.error("Konnte nach 5 Versuchen keine Verbindung zur Datenbank herstellen")

    # Tabellen anlegen (bei Bedarf später auf Alembic-Migration umstellen!)
    Base.metadata.create_all(bind=engine)

    yield
    # Hier könnten z.B. offene Ressourcen geschlossen werden


# -----------------------------------------------------------------------------
# FASTAPI-APP INITIALISIEREN
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Museum API",
    version=settings.app_version,
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# -----------------------------------------------------------------------------
# OPTIONAL: LOGGING UND MIDDLEWARE KONFIGURIEREN
# -----------------------------------------------------------------------------
# Logging-Level aus settings
logging.basicConfig(level=settings.log_level)
# Beispiel für CORS, falls Frontend auf anderer Domain läuft:
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_origins,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# -----------------------------------------------------------------------------
# ROUTER EINBINDEN
# -----------------------------------------------------------------------------
# Reihenfolge spielt selten eine Rolle, aber sinnvoll:
# 1) root ("/")
# 2) movies ("/movies")
# 3) media  ("/media")
# 4) wiki   ("/wiki")
app.include_router(root_router)
app.include_router(movie_router)
app.include_router(media_router)
app.include_router(wiki_router)

# -----------------------------------------------------------------------------
# STATISCHE DATEIEN (MEDIEN) SERVEN
# -----------------------------------------------------------------------------
# Mount-Pfad und Verzeichnis kommen aus den Settings.
# Beispiel: settings.media_url = "/static", settings.media_static_path = Path("static")
app.mount(
    settings.media_url,
    StaticFiles(directory=str(settings.media_static_path)),
    name="static",
)

# -----------------------------------------------------------------------------
# HINWEISE FÜR ENTWICKLER
# -----------------------------------------------------------------------------
# 1) Starten mit Uvicorn:
#      uvicorn app.main:app --reload --host 0.0.0.0 --port ${PORT:-8000}
#    → PORT aus Umgebungsvariable setzen, z.B. in Docker.
#
# 2) DB-Migration:
#    Derzeit create_all(); für Produktionsumgebungen auf Alembic-Migration umstellen.
#
# 3) Settings:
#    - media_url, media_static_path
#    - log_level
#    - app_version
#    - ggf. CORS-URIs (cors_origins)
#
# 4) Auth:
#    Die Router movie_router und wiki_router nutzen get_current_user → Grundlegende HTTP-Basic-Auth.
#    Ggf. auf OAuth2 / JWT erweitern.
#
# 5) Testing:
#    - Nutzt settings.api_base_url in Tests.
#    - Für CI evtl. separate Test-DB über env var konfigurieren.
#
# 6) Monitoring & Healthcheck:
#    - Erwäge einen /health-Endpoint, um Readiness/Liveness zu prüfen.
#    - Logging und Metrics (Prometheus) integrieren.
