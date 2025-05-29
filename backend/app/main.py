# backend/app/main.py

import time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager

from app.db import engine, Base
from app.api.endpoints import router as movie_router       # Movie-Router importieren
from app.api.media import router as media_router          # Media-Router importieren
from app.config import MEDIA_STATIC_PATH, MEDIA_URL       # Zentrale Config-Werte importieren


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan-Handler:
    1. Wartet bis zu fünfmal auf eine erfolgreiche DB-Verbindung.
    2. Legt dann über die ORM-Metadaten alle Tabellen an.
    3. Yield für den normalen FastAPI-Lifecycle.
    """
    for _ in range(5):
        try:
            with engine.connect():
                break
        except OperationalError:
            time.sleep(2)

    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup-Aufgaben könnten hier eingefügt werden


# FastAPI-App mit Lifespan und Titel
app = FastAPI(lifespan=lifespan, title="Museum API")

# Movie-Router einbinden (Prefix: /movies)
app.include_router(movie_router)

# Media-Router einbinden (Prefix: /media)
app.include_router(media_router)

# Statisches Verzeichnis für Medien bereitstellen
# → Basis-URL (MEDIA_URL) und Pfad (MEDIA_STATIC_PATH) kommen aus config.py
app.mount(
    MEDIA_URL,                                     # z.B. "/static"
    StaticFiles(directory=str(MEDIA_STATIC_PATH)), # z.B. Path("static")
    name="static"
)
