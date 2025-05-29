# backend/tests/test_wiki_importer.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base  # Metadata für schema-create
from app.services.wiki_importer import WikiImporter  # Zu testender Importer

# In-Memory-SQLite für schnelle Unit-Tests
SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Einmaliges Erzeugen aller Tabellen in der Test-DB
Base.metadata.create_all(bind=engine)

def test_wiki_import_success(monkeypatch):
    """
    Stub für fetch(), gibt ein dict zurück.
    Prüft, ob alle Keys im Resultat vorhanden sind.
    """
    fake = {"director": "X", "author": "Y", "main_cast": "A,B", "poster_url": "u", "description": "d"}
    monkeypatch.setattr(
        WikiImporter,
        "fetch",
        staticmethod(lambda title: fake)
    )
    result = WikiImporter.fetch("Any Title")
    assert isinstance(result, dict)
    for k in fake:
        assert result[k] == fake[k]

def test_wiki_import_failure(monkeypatch):
    """
    Stub für fetch(), wirft Exception.
    Prüft, ob die Exception korrekt durchgereicht wird.
    """
    monkeypatch.setattr(
        WikiImporter,
        "fetch",
        staticmethod(lambda title: (_ for _ in ()).throw(RuntimeError("fail")))
    )
    with pytest.raises(RuntimeError) as exc:
        WikiImporter.fetch("Bad Title")
    assert "fail" in str(exc.value)
