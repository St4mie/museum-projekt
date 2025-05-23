# backend/app/models/movie_schema.py

from pydantic import BaseModel, Field

class MovieBase(BaseModel):
    """
    Gemeinsame Felder für Ein- und Ausgabe.
    """
    title: str = Field(..., description="Filmtitel")
    wiki_url: str | None = Field(None, description="URL zum Wikipedia-Artikel")
    release_year: int | None = Field(None, description="Erscheinungsjahr")
    director: str | None = Field(None, description="Regisseur")
    author: str | None = Field(None, description="Drehbuchautor")
    main_cast: str | None = Field(None, description="Hauptdarsteller")
    poster_url: str | None = Field(None, description="Poster-URL")
    description: str | None = Field(None, description="Kurzbeschreibung")
    review: bool = Field(False, description="Flag für manuelle Prüfung")

class MovieCreate(MovieBase):
    """
    Schema für die Movie-Anlage (Input).
    Erbt alle Felder aus MovieBase.
    """

class Movie(MovieBase):
    """
    Schema für die Movie-Ausgabe (Response).
    Enthält zusätzlich das DB-PK-Feld.
    """
    id: int

    class Config:
        from_attributes = True  # Pydantic V2: statt orm_mode
