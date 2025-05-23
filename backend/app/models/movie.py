# backend/app/models/movie.py
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from app.models.base import Base  # Die Basisklasse mit Meta-Informationen

class MovieORM(Base):
    """
    SQLAlchemy-ORM-Modell für die Tabelle 'movie'.

    Felder:
      - id            : Primärschlüssel
      - title         : Filmtitel (Pflichtfeld)
      - release_year  : Erscheinungsjahr
      - director      : Regisseur
      - author        : Drehbuchautor
      - main_cast     : Hauptdarsteller (kommagetrennt)
      - poster_url    : Link zum Filmplakat
      - description   : Kurzbeschreibung / Plot
      - review        : Flag, wenn bei Wiki-Import Fehler auftraten
      - created_at    : Erstellzeitpunkt (automatisch gesetzt)
      - updated_at    : Letztes Update (automatisch aktualisiert)
    """

    __tablename__ = "movie"
    __table_args__ = (
        # Stellt sicher, dass Kombination aus Titel + Jahr eindeutig bleibt
        UniqueConstraint("title", "release_year", name="uq_movie_title_year"),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Eindeutige ID des Films (Auto-Increment)"
    )
    title = Column(
        String(255),
        nullable=False,
        doc="Titel des Films"
    )
    release_year = Column(
        Integer,
        nullable=True,
        doc="Erscheinungsjahr"
    )
    wiki_url = Column(
        Text,
        nullable=True,
        doc="URL zum Wikipedia-Artikel"
    )
    director = Column(
        String(255),
        nullable=True,
        doc="Regisseur"
    )
    author = Column(
        String(255),
        nullable=True,
        doc="Drehbuchautor"
    )
    main_cast = Column(
        Text,
        nullable=True,
        doc="Hauptdarsteller, kommasepariert"
    )
    poster_url = Column(
        Text,
        nullable=True,
        doc="Link zum Filmplakat"
    )
    description = Column(
        Text,
        nullable=True,
        doc="Kurzbeschreibung / Plot"
    )
    review = Column(
        Boolean,
        nullable=False,
        default=False,
        doc="Flag, ob der Datensatz manuell geprüft werden muss (z.B. Import-Fehler)"
    )
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        doc="Zeitpunkt der Erstellung"
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        doc="Zeitpunkt der letzten Änderung"
    )