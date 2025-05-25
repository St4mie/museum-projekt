# backend/test/test_wiki_importer.py

import pytest
from sqlalchemy import create_engine

from app.models.base import Base
from app.services.wiki_importer import WikiImporter

# In-Memory-SQLite für Tests (Konstante großgeschrieben erlaubt)
TEST_ENGINE = create_engine("sqlite:///:memory:", echo=False, future=True)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """
    Legt das Schema in der In-Memory-DB an und löscht es nach den Tests wieder.
    """
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)

def test_wiki_importer_fetch_basic():
    """
    Stellt sicher, dass WikiImporter die erwarteten Keys liefert.
    """
    importer = WikiImporter()
    data = importer.fetch("Blade Runner")
    for key in ("description", "director", "author", "main_cast", "poster_url"):
        assert key in data
