"""
This module provides test setup utilities for API tests.
The actual tests have been moved to test_integration.py.
This file is kept for backward compatibility and to provide
common test fixtures and utilities.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine, get_db
from app.models.movie import MovieORM
from app.api.endpoints import router

# -----------------------------------------------------------------------------
# Database setup for tests (MariaDB instead of SQLite)
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------------------------------------------------------
# Test app & client with auth header update
# -----------------------------------------------------------------------------
test_app = FastAPI()
test_app.include_router(router)
# Initialize dependency_overrides as a dictionary if it doesn't exist
if not hasattr(test_app, "dependency_overrides"):
    test_app.dependency_overrides = {}
test_app.dependency_overrides[get_db] = override_get_db

# Import default credentials from conftest
from .conftest import Settings        # Settings.test_user = "dev", test_pass = "devpass"
import base64

settings = Settings()                # Instantiated with default values
creds = f"{settings.test_user}:{settings.test_pass}"
token = base64.b64encode(creds.encode()).decode()

client = TestClient(test_app)
client.headers.update({              # <-- Here we set the auth header globally
    "Authorization": f"Basic {token}"
})

# -----------------------------------------------------------------------------
# Fixture: Clear DB before each test
# -----------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def clear_db():
    session = SessionLocal()
    session.query(MovieORM).delete()
    session.commit()
    session.close()
    yield

# -----------------------------------------------------------------------------
# Integration tests against /movies/
# -----------------------------------------------------------------------------
# These tests have been moved to test_integration.py
# and are executed there with the TestClient
# 
# - test_read_empty_movies
# - test_create_and_read_movie
# - test_prevent_duplicate_movie
# - test_import_from_wiki_success
# - test_import_from_wiki_failure
