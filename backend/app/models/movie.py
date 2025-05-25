# backend/app/models/movie.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    TIMESTAMP,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.models.base import Base  # Basisklasse mit declarative_base()


class MovieORM(Base):
    """
    SQLAlchemy-ORM-Modell für Filme.
    Sorgt über __table_args__ dafür, dass title+release_year eindeutig bleibt.
    """

    # Annotiere __tablename__ als Klassen-Variable vom Typ str
    __tablename__= "movie"
    __table_args__ = (
        UniqueConstraint("title", "release_year", name="uq_movie_title_year"),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Auto-Increment-Primärschlüssel",
    )
    title = Column(
        String(255),
        nullable=False,
        doc="Filmtitel",
    )
    release_year = Column(
        Integer,
        nullable=True,
        doc="Erscheinungsjahr",
    )
    wiki_url = Column(
        Text,
        nullable=True,
        doc="Wikipedia-URL",
    )
    director = Column(
        String(255),
        nullable=True,
        doc="Regisseur",
    )
    author = Column(
        String(255),
        nullable=True,
        doc="Drehbuchautor",
    )
    main_cast = Column(
        Text,
        nullable=True,
        doc="Hauptdarsteller (kommagetrennt)",
    )
    poster_url = Column(
        Text,
        nullable=True,
        doc="URL des Posters",
    )
    description = Column(
        Text,
        nullable=True,
        doc="Kurzbeschreibung / Plot",
    )
    review = Column(
        Boolean,
        nullable=False,
        default=False,
        doc="Flag für manuelle Nachbearbeitung (Import-Fehler)",
    )
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        doc="Erstellungszeitpunkt",
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        doc="Zeitpunkt der letzten Änderung",
    )
