# test/conftest.py

import pytest
from pydantic import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl, Field

class Settings(BaseSettings):
    # Environment
    app_env: str = Field("test", description="Environment mode: 'dev', 'test', or 'prod'")

    # API and Authentication
    api_base_url: HttpUrl = Field("http://localhost:8000", description="Base URL for API")
    test_user: str = Field("dev", description="Username for test authentication")
    test_pass: str = Field("devpass", description="Password for test authentication")

    model_config = SettingsConfigDict(
        env_file=".env",   # optional, loads additional environment variables
        env_file_path="../.env",  # look for .env in parent directory when running from backend/
        env_prefix="APP_",  # reads APP_TEST_USER → test_user
        case_sensitive=False,
        extra="ignore",     # ignores additional environment variables
    )

@pytest.fixture(scope="session")
def settings():
    return Settings()

@pytest.fixture(scope="session")
def auth_headers(settings):
    """
    Create HTTP Basic Auth headers for testing.
    Uses the test_user and test_pass from settings.
    """
    import base64
    credentials = f"{settings.test_user}:{settings.test_pass}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}
