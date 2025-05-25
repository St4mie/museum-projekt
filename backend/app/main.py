# backend/app/main.py

import time
from fastapi import FastAPI

app = FastAPI()

from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager

from app.db import engine, Base
from app.api.endpoints import router

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Wartet auf DB-Verfügbarkeit und erstellt das Schema.
    """
    for _ in range(5):
        try:
            with engine.connect():
                break
        except OperationalError:
            time.sleep(2)
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan, title="Museum API")
app.include_router(router)
