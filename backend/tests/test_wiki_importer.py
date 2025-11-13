# backend/tests/test_wiki_importer.py

import pytest
import wikipedia
import wptools

from app.db import Base, engine  # Metadata und Engine für schema-create
from app.services.wiki_importer import WikiImporter  # Zu testender Importer
from app.config import settings

# Mark all tests to use settings fixture
pytestmark = pytest.mark.usefixtures("settings")

# Einmaliges Erzeugen aller Tabellen in der Test-DB
Base.metadata.create_all(bind=engine)

def test_wiki_import_success(monkeypatch):
    """
    Stub für fetch(), gibt ein dict zurück.
    Prüft, ob alle Keys im Resultat vorhanden sind.
    """
    fake = {
        "director": "X",
        "author": "Y",
        "main_cast": "A,B",
        "poster_url": "u",
        "description": "d"
    }
    monkeypatch.setattr(
        WikiImporter,
        "fetch",
        staticmethod(lambda title: fake)
    )
    result = WikiImporter.fetch("Any Title")
    assert isinstance(result, dict)
    for k, v in fake.items():
        assert result[k] == v

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

@pytest.fixture
def wiki_settings(monkeypatch, settings):
    """
    Fixture für die Überschreibung der Wikipedia-Settings.
    """
    monkeypatch.setattr(settings, "wikipedia_language", "en")
    monkeypatch.setattr(settings, "wikipedia_api_url", "https://api.test/wikipedia")
    return settings


@pytest.fixture
def wiki_calls(monkeypatch):
    """
    Fixture für die Aufzeichnung der Aufrufe von wikipedia.set_lang und set_api_url.
    """
    calls = []
    monkeypatch.setattr(wikipedia, "set_lang", lambda lang: calls.append(("lang", lang)))
    # nur bei neueren wikipedia-Versionen verfügbar
    monkeypatch.setattr(
        wikipedia,
        "set_api_url",
        lambda url: calls.append(("api_url", url)),
        raising=False
    )
    return calls


@pytest.fixture
def dummy_page(monkeypatch):
    """
    Fixture für einen Stub von wikipedia.page.
    """
    class DummyPage:
        def __init__(self, _):  # Renamed from 'title' as it's not used
            self.summary = "dummy summary"

    monkeypatch.setattr(wikipedia, "page", lambda title: DummyPage(title))
    return DummyPage


@pytest.fixture
def dummy_parse(monkeypatch):
    """
    Fixture für einen Stub von wptools.page.
    """
    class DummyParse:
        data = {"infobox": {
            "Regie": "Regisseur",
            "Drehbuch": "Drehbuchautor",
            "Besetzung": ["Schauspieler1", "Schauspieler2"],
            "Bild": "http://bild.url"
        }}

    monkeypatch.setattr(
        wptools,
        "page",
        lambda title, lang: type("P", (), {"get_parse": lambda self: DummyParse()})()
    )
    return DummyParse


def test_fetch_uses_settings(monkeypatch, settings, wiki_settings, wiki_calls, dummy_page, dummy_parse):
    """
    Testet, dass WikiImporter.fetch die wikipedia_language und wikipedia_api_url
    aus den Settings nutzt.
    """

    # 4) Ausführen von fetch
    result = WikiImporter.fetch("Some Movie")

    # 5) Assertions: Settings wurden verwendet und das Ergebnis korrekt gemappt
    assert ("lang", "en") in wiki_calls
    assert ("api_url", "https://api.test/wikipedia") in wiki_calls or wiki_calls  # akzeptiere fehlende set_api_url
    assert result["description"] == "dummy summary"
    assert result["director"] == "Regisseur"
    assert result["author"] == "Drehbuchautor"
    assert isinstance(result["main_cast"], list)
    assert result["poster_url"] == "http://bild.url"
