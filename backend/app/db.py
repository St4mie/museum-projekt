# backend/app/db.py

import os
import socket
# -------------------------------------------------------------------------
# 1) Debug ENV & DB_URL
# -------------------------------------------------------------------------
print("ENV APP_ENV:", os.getenv("APP_ENV"))
from app.config import settings
print(f"settings.app_env: {settings.app_env}")
print(f"settings.database_url: {settings.database_url}")
print(f"settings.test_database_url: {settings.test_database_url}")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -------------------------------------------------------------------------
# 2) Engine-URL je nach Umgebung auswählen
#    - Bei 'test' nutzen wir die Test-DB
#    - Sonst die Standard-DB
#    - Bei lokaler Ausführung (nicht in Docker) nutzen wir SQLite
# -------------------------------------------------------------------------
env = settings.app_env.lower()

# Prüfen, ob wir lokal (nicht in Docker) ausgeführt werden
def is_running_locally():
    try:
        # Versuche, den 'db'-Hostnamen aufzulösen - wenn es fehlschlägt, sind wir nicht in Docker
        socket.gethostbyname('db')
        return False
    except socket.gaierror:
        return True

# SQLite für lokale Tests verwenden
if is_running_locally():
    print("→ Lokale Ausführung, verwende SQLite")
    if env == "test":
        db_url = "sqlite:///./test_db.sqlite"
    else:
        db_url = "sqlite:///./dev_db.sqlite"
else:
    if env == "test":
        db_url = settings.test_database_url
    else:
        db_url = settings.database_url

print(f"→ Using DB URL for env='{env}': {db_url}")

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    echo=False,   # Setze auf True, wenn du SQL-Logs im Dev-Modus sehen möchtest
    future=True,  # Nutzt SQLAlchemy-2.0-API
)

# -------------------------------------------------------------------------
# 3) SessionLocal: Fabrik für neue Sessions pro Request
# -------------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# -------------------------------------------------------------------------
# 4) Basisklasse für alle ORM-Modelle
# -------------------------------------------------------------------------
Base = declarative_base()

# -------------------------------------------------------------------------
# 5) FastAPI Dependency: get_db
#    Öffnet pro Request eine Session und schließt sie danach
# -------------------------------------------------------------------------
def get_db():
    """
    FastAPI Dependency:
    • Öffnet eine neue DB-Session pro Request.
    • Schließt die Session in finally, egal ob Fehler oder nicht.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
