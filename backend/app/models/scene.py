# backend/app/models/scene.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    DECIMAL,
    UniqueConstraint,
    Table,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db import Base

# Junction table for m:n relationship between scenes and exhibits
szene_exponat = Table(
    "szene_exponat",
    Base.metadata,
    Column("szene_id", Integer, ForeignKey("szene.id"), primary_key=True),
    Column("exponat_id", Integer, ForeignKey("exponat.id"), primary_key=True),
)

class SzeneORM(Base):
    """
    ORM-Klasse für Szenen.
    - __tablename__: Name der DB-Tabelle
    - __table_args__: Composite-Unique-Constraint auf film_id+name
    """
    __tablename__ = "szene"
    __table_args__ = (UniqueConstraint("film_id", "name"),)

    id = Column(Integer, primary_key=True, index=True)
    film_id = Column(Integer, ForeignKey("movie.id"), nullable=False)
    name = Column(String, nullable=False)
    beschreibung = Column(String, nullable=True)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    aktualisiert_am = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    film = relationship("MovieORM", back_populates="szenen")
    medien = relationship("MediumORM", back_populates="szene", cascade="all, delete-orphan")
    exponate = relationship("ExponatORM", secondary=szene_exponat, back_populates="szenen")
    stellplatz = relationship("StellplatzORM", back_populates="szene", uselist=False)

class MediumORM(Base):
    """
    ORM-Klasse für Medien (Audio/Video).
    """
    __tablename__ = "medium"

    id = Column(Integer, primary_key=True, index=True)
    szene_id = Column(Integer, ForeignKey("szene.id"), nullable=False)
    dateipfad = Column(String, nullable=False)
    medientyp = Column(Enum("audio", "video", name="medientyp"), nullable=False)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    aktualisiert_am = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    szene = relationship("SzeneORM", back_populates="medien")

class ExponatORM(Base):
    """
    ORM-Klasse für Exponate.
    """
    __tablename__ = "exponat"
    __table_args__ = (UniqueConstraint("name"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    beschreibung = Column(String, nullable=True)
    hersteller = Column(String, nullable=True)
    baujahr = Column(Integer, nullable=True)
    material = Column(String, nullable=True)
    wert = Column(DECIMAL(12, 2), nullable=True)
    anzahl = Column(Integer, default=1)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    aktualisiert_am = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    szenen = relationship("SzeneORM", secondary=szene_exponat, back_populates="exponate")

# Add relationship to MovieORM
from app.models.movie import MovieORM
MovieORM.szenen = relationship("SzeneORM", back_populates="film", cascade="all, delete-orphan")