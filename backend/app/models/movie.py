# backend/app/models/movie.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.sql import func                     # für automatische Timestamp-Defaults

from app.db import Base                            # Basisklasse für deklaratives ORM

class MovieORM(Base):
    """
    ORM-Klasse für Filme.
    - __tablename__: Name der DB-Tabelle
    - __table_args__: Composite-Unique-Constraint auf titel+erscheinungsjahr
    """
    __tablename__ = "movie"
    __table_args__ = (UniqueConstraint("titel", "erscheinungsjahr"),)

    id = Column(Integer, primary_key=True, index=True)
    titel = Column(String, nullable=False, index=True)
    wiki_url = Column(String, nullable=True)
    erscheinungsjahr = Column(Integer, nullable=False)
    regisseur = Column(String, nullable=True)
    autor = Column(String, nullable=True)
    hauptdarsteller = Column(String, nullable=True)
    poster_url = Column(String, nullable=True)
    beschreibung = Column(String, nullable=True)
    pruefung = Column(Boolean, default=False, nullable=False)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    aktualisiert_am = Column(DateTime(timezone=True), onupdate=func.now())
