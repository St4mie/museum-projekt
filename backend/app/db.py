# backend/app/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -------------------------------------------------------------------------
# 1) Zentrale Konfiguration importieren
# -------------------------------------------------------------------------
# DATABASE_URL: Haupt-Connection-String für den Service-User (lesen/schreiben)
# DATABASE_URL_MIGRATE: Full-privilege-URL für Migrationen (Alembic)
from app.config import DATABASE_URL, DATABASE_URL_MIGRATE

# -------------------------------------------------------------------------
# 2) SQLAlchemy Engine & SessionFactory
# -------------------------------------------------------------------------
# Engine für reguläre DB-Zugriffe (ohne Migrations-Rechte)
# pool_pre_ping sorgt für automatische Verbindungsprüfung
# echo=False deaktiviert SQL-Logging; in DEBUG-Modus ggf. True setzen
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    future=True,  # nutzt SQLAlchemy-2.0-Style
)

# SessionLocal: Fabrik zum Erzeugen neuer Session-Instanzen pro Request
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# -------------------------------------------------------------------------
# 3) Basisklasse für ORM-Modelle
# -------------------------------------------------------------------------
# Alle ORM-Klassen erben von dieser Base, sodass Base.metadata
# alle Tabellen sammeln kann (für create_all oder Alembic)
Base = declarative_base()

# -------------------------------------------------------------------------
# 4) FastAPI Dependency: get_db
# -------------------------------------------------------------------------
def get_db():
    """
    FastAPI Dependency:
    • Öffnet eine neue DB-Session für jeden Request.
    • Sorgt mit 'finally' dafür, dass die Session nach dem Request geschlossen wird.
    Verwendung in Endpoints:
        def endpoint(..., db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
