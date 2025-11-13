from pydantic import BaseModel, Field

class MovieBase(BaseModel):
    """
    Gemeinsame Felder für Input und Output.
    """
    titel: str = Field(..., description="Filmtitel")
    erscheinungsjahr: int | None = Field(None, description="Erscheinungsjahr")
    wiki_url: str | None = Field(None, description="Wikipedia-URL")
    regisseur: str | None = Field(None, description="Regisseur")
    autor: str | None = Field(None, description="Drehbuchautor")
    hauptdarsteller: str | None = Field(None, description="Hauptdarsteller")
    poster_url: str | None = Field(None, description="Poster-URL")
    beschreibung: str | None = Field(None, description="Kurzbeschreibung")
    pruefung: bool = Field(False, description="Flag für manuelle Prüfung")

    # Pydantic v2: damit wir ORM-Instanzen direkt serialisieren können
    model_config = {
        "from_attributes": True
    }


class MovieCreate(MovieBase):
    """
    Schema für neues Movie (POST /movies).
    Erbt alles von MovieBase – kein eigenes Feld nötig.
    """
    pass


class Movie(MovieBase):
    """
    Schema für Movie-Antwort (GET/POST);
    enthält zusätzlich das Primärschlüssel-Feld.
    """
    id: int

    model_config = {
        "from_attributes": True
    }
