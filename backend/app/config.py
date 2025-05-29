# backend/app/config.py

import os
from pathlib import Path
from typing import List

# -----------------------------------------------------------------------------
# 1) Environment / Mode
# -----------------------------------------------------------------------------
# “dev” or “prod” – steuert, ob z. B. Static-Files von FastAPI oder Nginx/CDN
APP_ENV: str = os.getenv("APP_ENV", "dev")

# -----------------------------------------------------------------------------
# 2) Server / Host Settings
# -----------------------------------------------------------------------------
# Host und Port, auf denen Uvicorn (oder ein anderer ASGI-Server) lauscht
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))

# -----------------------------------------------------------------------------
# 3) Database Configuration
# -----------------------------------------------------------------------------
# URL für SQLAlchemy (MySQL/MariaDB via PyMySQL oder SQLite als Fallback)
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./test.db"
)
# Separate URL für Schema-Migrationen (Alembic), kann gleich bleiben
DATABASE_URL_MIGRATE: str = os.getenv("DATABASE_URL_MIGRATE", DATABASE_URL)

# -----------------------------------------------------------------------------
# 4) CORS & Security
# -----------------------------------------------------------------------------
# Erlaubte Origins für Browser-Clients (um CORS-Fehler zu vermeiden)
CORS_ALLOWED_ORIGINS: List[str] = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
# JWT & Auth
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# -----------------------------------------------------------------------------
# 5) Logging
# -----------------------------------------------------------------------------
# Standard-Logging-Level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
# Format für Log-Ausgaben
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(levelname)s:%(name)s:%(message)s")

# -----------------------------------------------------------------------------
# 6) Media / Static Files
# -----------------------------------------------------------------------------
# Dateisystem-Pfad für statische Medien (Bilder, Videos, Audio)
MEDIA_STATIC_PATH: Path = Path(os.getenv("MEDIA_STATIC_PATH", "static"))
# URL-Prefix, unter dem Medien ausgeliefert werden
MEDIA_URL: str = os.getenv("MEDIA_URL", "/static")

# -----------------------------------------------------------------------------
# 7) Externe Integrationen & Feature-Flags
# -----------------------------------------------------------------------------
# Basis-URL für Wikipedia API (falls ihr die REST-API nutzt)
WIKIPEDIA_API_URL: str = os.getenv(
    "WIKIPEDIA_API_URL",
    "https://de.wikipedia.org/api/rest_v1"
)
# Feature-Flag, um Thumbnail-Erzeugung optional zu aktivieren
FEATURE_THUMBNAILS: bool = os.getenv("FEATURE_THUMBNAILS", "true").lower() == "true"
from pydantic import BaseSettings, SettingsConfigDict, Field, field_validator
from pathlib import Path
from typing import List, Optional

# -----------------------------------------------------------------------------
# Application Settings via Pydantic BaseSettings
# -----------------------------------------------------------------------------
class Settings(BaseSettings):
    # 1) Environment / Mode
    app_env: str = Field(
        "dev",
        description="Umgebungsmodus: 'dev' oder 'prod'"
    )

    # 2) Server / Host Settings
    host: str = Field(
        "0.0.0.0",
        description="Host, auf dem der Server lauscht"
    )
    port: int = Field(
        8000,
        description="Port, auf dem der Server lauscht"
    )

    # 3) Database Configuration
    database_url: str = Field(
        "sqlite+aiosqlite:///./test.db",
        description="URL für Datenbankverbindung"
    )
    database_url_migrate: Optional[str] = Field(
        None,
        description="URL für Schema-Migrationen; falls None, wird database_url verwendet"
    )

    # 4) CORS & Security
    cors_allowed_origins: List[str] = Field(
        ["*"],
        description="Liste erlaubter Origins für CORS"
    )
    secret_key: str = Field(
        "change-me",
        description="Secret Key für JWT-Authentifizierung"
    )
    access_token_expire_minutes: int = Field(
        30,
        description="Gültigkeit des Access-Tokens in Minuten"
    )

    # 5) Logging
    log_level: str = Field(
        "INFO",
        description="Standard-Logging-Level"
    )
    log_format: str = Field(
        "%(levelname)s:%(name)s:%(message)s",
        description="Format für Log-Ausgaben"
    )

    # 6) Media / Static Files
    media_static_path: Path = Field(
        Path("static"),
        description="Pfad für statische Medien"
    )
    media_url: str = Field(
        "/static",
        description="URL-Prefix für Medien"
    )

    # 7) Externe Integrationen & Feature-Flags
    wikipedia_api_url: str = Field(
        "https://de.wikipedia.org/api/rest_v1",
        description="Basis-URL für Wikipedia-API"
    )
    feature_thumbnails: bool = Field(
        True,
        description="Feature-Flag zur Steuerung der Thumbnail-Erzeugung"
    )

    # Pydantic SettingsConfig
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_prefix = "APP_",
        case_sensitive = False,
    )

    # Fallback-Logik: Wenn keine migrate-URL gesetzt ist, nutze database_url
    @field_validator("database_url_migrate", mode="before")
    def _set_migrate_default(cls, v, info):
        return v or info.data.get("database_url")


# Instanz der Settings-Klasse
settings = Settings()
