# backend/app/main.py

import time
from fastapi import FastAPI
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager

# Korrigierter Import: engine und Base kommen aus dem app-Package, nicht 'backend.app'
from app.db import engine, Base

# API-Router mit allen Movie-Endpunkten
from app.api.endpoints import router


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

    # Alle Tabellen gemäß Base.metadata erzeugen
    Base.metadata.create_all(bind=engine)
    yield
    # Hier könnten später Release- oder Cleanup-Tasks stehen


# FastAPI-App mit dem Lifespan-Context und einem sprechenden Titel
app = FastAPI(lifespan=lifespan, title="Museum API")

# Inkludiere alle Routen des Routers (prefix "/movies")
app.include_router(router)
