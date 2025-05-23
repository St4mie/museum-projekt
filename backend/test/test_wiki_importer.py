# backend/tests/test_wiki_importer.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db import Base
from app.main import app
from app.models.movie import MovieORM

# In-Memory SQLite für Tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def test_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def client(test_db, monkeypatch):
    # Override get_db dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides = {"get_db": override_get_db}
    return TestClient(app)

def test_import_sets_review_on_error(client, test_db, monkeypatch):
    # Füge einen Film hinzu, der den Import-Error provoziert
    movie = MovieORM(title="Nonexistent Film")
    test_db.add(movie)
    test_db.commit()

    # Simuliere, dass wptools.page einen Fehler wirft
    import wptools
    monkeypatch.setattr(wptools, "page", lambda title: (_ for _ in ()).throw(Exception("Not found")))

    response = client.post("/import/wikipedia")
    assert response.status_code == 200
    results = response.json()["results"]
    assert results == [{"id": movie.id, "error": "Not found"}]

    # Prüfe, dass das review-Flag gesetzt wurde
    updated = test_db.query(MovieORM).first()
    assert updated.review is True
