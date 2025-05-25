# backend/app/db.py

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -----------------------------------------------------------------------------
# 1. Umgebungs­variablen laden
# -----------------------------------------------------------------------------
# Wir gehen davon aus, dass sich die .env eine Ebene oberhalb von /app befindet
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_USER = os.getenv("DB_USER", "service")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "museum_db")

# -----------------------------------------------------------------------------
# 2. SQLAlchemy Engine & SessionFactory
# -----------------------------------------------------------------------------
# Baue die vollständige Connection-URL für MariaDB/MySQL
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Engine mit Pool-Pre-Ping, um Broken connections zu vermeiden
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,       # SQL-Logging: auf True setzen, wenn gewünscht
    future=True,      # nutze SQLAlchemy-2.0-Style
)

# SessionLocal: Factory, um in jedem Request eine neue Session zu öffnen
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# -----------------------------------------------------------------------------
# 3. Basisklasse für ORM-Modelle
# -----------------------------------------------------------------------------
# Deklarative Basis, von der alle Models erben
Base = declarative_base()

# -----------------------------------------------------------------------------
# 4. FastAPI Dependency: get_db
# -----------------------------------------------------------------------------
# Diese Funktion liefert pro Request eine Session und schließt sie danach.
def get_db():
    """
    FastAPI Dependency: Öffnet eine neue DB-Session und sorgt dafür,
    dass sie am Ende des Requests wieder geschlossen wird.
    Verwendung in Endpoints via Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
