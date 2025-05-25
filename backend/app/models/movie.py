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
    - __table_args__: Composite-Unique-Constraint auf title+release_year
    """
    __tablename__ = "movie"
    __table_args__ = (UniqueConstraint("title", "release_year"),)

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    wiki_url = Column(String, nullable=True)
    release_year = Column(Integer, nullable=False)
    director = Column(String, nullable=True)
    author = Column(String, nullable=True)
    main_cast = Column(String, nullable=True)
    poster_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    review = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
