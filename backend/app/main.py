# backend/app/main.py

import time
from fastapi import FastAPI
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager

from app.api.endpoints import router
from app.db import engine
from app.models.base import Base  # Dort definierst Du `Base = declarative_base()`

@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Startup/Lifespan-Event:
      1. Wartet, bis die DB erreichbar ist (max. 5 Versuche),
      2. erstellt dann alle Tabellen via SQLAlchemy.
    """
    retries = 5
    for _ in range(retries):
        try:
            with engine.connect():
                break
        except OperationalError:
            time.sleep(2)
    Base.metadata.create_all(bind=engine)
    yield
    # optional: Cleanup-Code hier

# FastAPI-App mit Lifespan-Handler und Router
app = FastAPI(lifespan=lifespan, title="Museum API")
app.include_router(router)
