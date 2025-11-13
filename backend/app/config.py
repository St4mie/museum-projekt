# backend/app/config.py

import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic import BaseSettings
from pydantic_settings import SettingsConfigDict


# Determine the location of the .env file
# Try multiple possible locations to make it more robust
def find_env_file():
    """Find the .env file by checking multiple possible locations."""
    # List of possible locations to check
    possible_locations = [
        ".env",                  # Current directory
        "../.env",               # One level up (when running from backend)
        "../../.env",            # Project root (when running from backend/app)
        "backend/.env",          # Backend directory (when running from project root)
        "backend/app/.env",      # Backend/app directory (when running from project root)
    ]

    # Check each location
    for location in possible_locations:
        path = Path(location)
        if path.exists():
            if path.is_file():
                try:
                    # Check if file is readable
                    with open(path, 'r', encoding='utf-8') as f:
                        # Just read a bit to check if it's readable
                        f.read(1)
                    return str(path)
                except Exception as e:
                    print(f"⚠️ Warning: Found .env file at {path} but couldn't read it: {e}")
            else:
                print(f"⚠️ Warning: Found {path} but it's not a file")

    # If we get here, no valid .env file was found
    print("⚠️ Warning: No valid .env file found in common locations")
    return ".env"  # Default to .env in current directory

ENV_FILE_PATH = find_env_file()
print(f"→ Using .env file at: {ENV_FILE_PATH} (absolute: {Path(ENV_FILE_PATH).absolute()})")

# Debug: ausgegebene, geladene ENV-Variablen
try:
    app_vars = {k: os.environ[k] for k in os.environ if k.startswith("APP_")}
    print("→ all APP_ vars:", app_vars)
except Exception as e:
    print(f"→ Error reading environment variables: {e}")

class Settings(BaseSettings):
    # 1) Environment / Mode
    app_env: str = Field("dev", description="Umgebungsmodus: 'dev'|'test'|'prod'")
    app_version: str = Field("0.1.0", description="Version der App")

    # 2) Server / Host
    host: str = Field("0.0.0.0", description="Server-Host")
    port: int = Field(8000, description="Server-Port")

    # 3) Datenbank
    database_url: str = Field("sqlite:///./test.db", description="DB-URL")
    database_url_migrate: Optional[str] = Field(
        None,
        description="Migration-DB-URL; standardmäßig database_url"
    )
    test_database_url: Optional[str] = Field(
        None,
        description="Test-DB-URL bei APP_ENV=test"
    )

    # 4) CORS & Security
    cors_allowed_origins: List[str] = Field(
        ["*"], description="Erlaubte Origins für CORS"
    )
    secret_key: str = Field("dev-secret-key-change-in-production", description="JWT Secret Key")
    access_token_expire_minutes: int = Field(
        30, description="Token-Gültigkeit in Minuten"
    )

    # 5) Logging
    log_level: str = Field("INFO", description="Logging Level")
    log_format: str = Field(
        "%(levelname)s:%(name)s:%(message)s", description="Log-Format"
    )

    # 6) Medien / Static
    media_static_path: Path = Field(Path("static"), description="Static Path")
    media_url: str = Field("/static", description="Static URL Prefix")

    # 7) Externe Integrationen & Flags
    wikipedia_api_url: str = Field(
        "https://de.wikipedia.org/api/rest_v1",
        description="Wikipedia API URL"
    )
    wikipedia_language: str = Field("de", description="Wikipedia Sprache")
    feature_thumbnails: bool = Field(True, description="Thumbnail-Feature aktiv?")

    # 8) Basic-Auth Credentials
    editor_user: str = Field("editor", description="Editor-User")
    editor_pass: str = Field("editorpass", description="Editor-Passwort")
    editor_role: str = Field("editor", description="Editor-Rolle")

    service_user: str = Field("service", description="Service-User")
    service_pass: str = Field("servicepass", description="Service-Passwort")
    service_role: str = Field("service", description="Service-Rolle")

    dev_user: str = Field("dev", description="Dev-User")
    dev_pass: str = Field("devpass", description="Dev-Passwort")
    dev_role: str = Field("developer", description="Dev-Rolle")

    # 9) ENV-Prefix und .env-Datei
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP",
        case_sensitive=False,
        extra="ignore",
        # Don't use env_file_path here as we're manually loading with dotenv
    )

    @field_validator("database_url", "database_url_migrate", "test_database_url", mode="before")
    def _validate_database_url(cls, v, info):
        """Validate and normalize database URLs"""
        if not v:
            # For database_url_migrate, use database_url as fallback
            if info.field_name == "database_url_migrate":
                return info.data.get("database_url")
            return v

        # Normalize the URL if it contains environment variables
        if "${" in v and "}" in v:
            try:
                # Simple environment variable substitution
                import re
                def replace_env_var(match):
                    var_name = match.group(1)
                    env_value = os.environ.get(var_name, "")
                    if not env_value:
                        print(f"⚠️ Warning: Environment variable ${{{var_name}}} not found for {info.field_name}")
                    return env_value

                v = re.sub(r'\${([^}]+)}', replace_env_var, v)

                # Check if all variables were substituted
                if "${" in v and "}" in v:
                    print(f"⚠️ Warning: Some environment variables in {info.field_name} were not substituted: {v}")
            except Exception as e:
                print(f"⚠️ Warning: Could not substitute environment variables in {info.field_name}: {e}")

        return v

    @field_validator("cors_allowed_origins", mode="before")
    def _parse_cors(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                import json
                return json.loads(v)
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

# Instantiate settings with better error handling
try:
    # Force environment variables to be loaded from .env file
    from dotenv import load_dotenv

    # Use the enhanced find_env_file function to locate the .env file
    env_file = ENV_FILE_PATH

    # Try to load the .env file
    if Path(env_file).exists() and Path(env_file).is_file():
        try:
            # Load the .env file with override=True to ensure values are set
            load_dotenv(env_file, override=True)
            print(f"✅ Loaded environment variables from {env_file}")

            # Verify that environment variables were loaded
            app_vars = {k: v for k, v in os.environ.items() if k.startswith("APP_")}
            if app_vars:
                print(f"✅ Found {len(app_vars)} APP_* environment variables")
            else:
                print(f"⚠️ Warning: No APP_* environment variables found after loading {env_file}")

                # Try to read the file directly to check its content
                try:
                    with open(env_file, 'r', encoding='utf-8') as f:
                        env_content = f.read()
                    if env_content.strip():
                        print(f"⚠️ .env file has content but no APP_* variables were loaded. Check format.")
                    else:
                        print(f"⚠️ .env file is empty.")
                except Exception as e:
                    print(f"⚠️ Could not read .env file: {e}")
        except Exception as e:
            print(f"⚠️ Error loading .env file: {e}")
    else:
        print(f"⚠️ Warning: .env file not found at {env_file}. Using environment variables only.")

    # Print all APP_ environment variables for debugging
    app_vars = {k: v for k, v in os.environ.items() if k.startswith("APP_")}
    print(f"→ Environment variables (APP_*): {app_vars}")

    # Create settings with explicit environment variables
    settings = Settings()
    print("✅ Settings loaded successfully")

    # Verify critical settings were loaded correctly
    if settings.secret_key == "dev-secret-key-change-in-production" and os.environ.get("APP_SECRET_KEY"):
        print("⚠️ Warning: Using default secret_key despite APP_SECRET_KEY being set in environment")

    # Check database URLs for common issues
    for db_url_name in ["database_url", "database_url_migrate", "test_database_url"]:
        db_url = getattr(settings, db_url_name)
        if db_url and "${" in db_url:
            print(f"⚠️ Warning: {db_url_name} contains unresolved variables: {db_url}")

    # Print loaded settings for debugging
    print("→ Loaded settings:")
    for key, value in settings.model_dump().items():
        print(f"  - {key}: {value}")

except Exception as e:
    print(f"❌ Error instantiating Settings: {e}")
    print(f"❌ Make sure the .env file exists and is properly formatted")
    print(f"❌ Current working directory: {os.getcwd()}")
    print(f"❌ Attempted to load .env from: {ENV_FILE_PATH}")

    # List all environment variables for debugging
    print("❌ Environment variables:")
    for key, value in os.environ.items():
        if key.startswith("APP_"):
            print(f"  - {key}: {value}")

    # Try to create a minimal settings object with explicit values
    try:
        # Create a dictionary with all the required settings
        settings_dict = {
            "app_env": os.environ.get("APP_ENV", "dev"),
            "app_version": os.environ.get("APP_APP_VERSION", "0.1.0"),
            "host": os.environ.get("APP_HOST", "0.0.0.0"),
            "port": int(os.environ.get("APP_PORT", "8000")),
            "database_url": os.environ.get("APP_DATABASE_URL", "sqlite:///./test.db"),
            "database_url_migrate": os.environ.get("APP_DATABASE_URL_MIGRATE", None),
            "test_database_url": os.environ.get("APP_TEST_DATABASE_URL", None),
            "cors_allowed_origins": os.environ.get("APP_CORS_ALLOWED_ORIGINS", '["*"]'),
            "secret_key": os.environ.get("APP_SECRET_KEY", "dev-secret-key-change-in-production"),
            "access_token_expire_minutes": int(os.environ.get("APP_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            "log_level": os.environ.get("APP_LOG_LEVEL", "INFO"),
            "log_format": os.environ.get("APP_LOG_FORMAT", "%(levelname)s:%(name)s:%(message)s"),
            "media_static_path": os.environ.get("APP_MEDIA_STATIC_PATH", "static"),
            "media_url": os.environ.get("APP_MEDIA_URL", "/static"),
            "wikipedia_api_url": os.environ.get("APP_WIKIPEDIA_API_URL", "https://de.wikipedia.org/api/rest_v1"),
            "wikipedia_language": os.environ.get("APP_WIKIPEDIA_LANGUAGE", "de"),
            "feature_thumbnails": os.environ.get("APP_FEATURE_THUMBNAILS", "true").lower() == "true",
            "editor_user": os.environ.get("APP_EDITOR_USER", "editor"),
            "editor_pass": os.environ.get("APP_EDITOR_PASS", "editorpass"),
            "editor_role": os.environ.get("APP_EDITOR_ROLE", "editor"),
            "service_user": os.environ.get("APP_SERVICE_USER", "service"),
            "service_pass": os.environ.get("APP_SERVICE_PASS", "servicepass"),
            "service_role": os.environ.get("APP_SERVICE_ROLE", "service"),
            "dev_user": os.environ.get("APP_DEV_USER", "dev"),
            "dev_pass": os.environ.get("APP_DEV_PASS", "devpass"),
            "dev_role": os.environ.get("APP_DEV_ROLE", "developer"),
        }

        # Convert media_static_path to Path object if it's a string
        if isinstance(settings_dict["media_static_path"], str):
            settings_dict["media_static_path"] = Path(settings_dict["media_static_path"])

        # Parse cors_allowed_origins if it's a string
        if isinstance(settings_dict["cors_allowed_origins"], str):
            if settings_dict["cors_allowed_origins"].startswith("["):
                import json
                settings_dict["cors_allowed_origins"] = json.loads(settings_dict["cors_allowed_origins"])
            else:
                settings_dict["cors_allowed_origins"] = [item.strip() for item in settings_dict["cors_allowed_origins"].split(",") if item.strip()]

        # Create settings with explicit values
        settings = Settings(**settings_dict)
        print("✅ Created settings with explicit values")
    except Exception as inner_e:
        print(f"❌ Error creating settings with explicit values: {inner_e}")
        # Last resort: create settings with default values
        settings = Settings()
        print("⚠️ Using default settings")

# Für ältere Importe
MEDIA_STATIC_PATH = settings.media_static_path
