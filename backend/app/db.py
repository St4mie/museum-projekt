# backend/app/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ----------------------------------------------------------------------------
# 1. Environment variables are injected by Docker Compose via env_file –
#    no need to load .env manually inside the container.
# ----------------------------------------------------------------------------
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# ----------------------------------------------------------------------------
# 2. SQLAlchemy Engine & SessionFactory
# ----------------------------------------------------------------------------
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,      # SQL-Logging: auf True setzen, wenn gewünscht
    future=True,     # nutze SQLAlchemy-2.0-Style
)

# SessionLocal: Factory, um in jedem Request eine neue Session zu öffnen
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ----------------------------------------------------------------------------
# 3. Basisklasse für ORM-Modelle
# ----------------------------------------------------------------------------
Base = declarative_base()

# ----------------------------------------------------------------------------
# 4. FastAPI Dependency: get_db
# ----------------------------------------------------------------------------
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