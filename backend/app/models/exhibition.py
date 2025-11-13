# backend/app/models/exhibition.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db import Base

class AusstellungORM(Base):
    """
    ORM-Klasse für Ausstellungen.
    """
    __tablename__ = "ausstellung"
    __table_args__ = (UniqueConstraint("name"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    beschreibung = Column(String, nullable=True)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    aktualisiert_am = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    raeume = relationship("RaumORM", back_populates="ausstellung", cascade="all, delete-orphan")

class RaumORM(Base):
    """
    ORM-Klasse für Räume.
    """
    __tablename__ = "raum"
    __table_args__ = (UniqueConstraint("ausstellung_id", "name"),)

    id = Column(Integer, primary_key=True, index=True)
    ausstellung_id = Column(Integer, ForeignKey("ausstellung.id"), nullable=False)
    name = Column(String, nullable=False)
    beschreibung = Column(String, nullable=True)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    aktualisiert_am = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ausstellung = relationship("AusstellungORM", back_populates="raeume")
    regale = relationship("RegalORM", back_populates="raum", cascade="all, delete-orphan")

class RegalORM(Base):
    """
    ORM-Klasse für Regale.
    """
    __tablename__ = "regal"
    __table_args__ = (UniqueConstraint("raum_id", "bezeichnung"),)

    id = Column(Integer, primary_key=True, index=True)
    raum_id = Column(Integer, ForeignKey("raum.id"), nullable=False)
    bezeichnung = Column(String, nullable=False)
    beschreibung = Column(String, nullable=True)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    aktualisiert_am = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    raum = relationship("RaumORM", back_populates="regale")
    faecher = relationship("FachORM", back_populates="regal", cascade="all, delete-orphan")

class FachORM(Base):
    """
    ORM-Klasse für Fächer.
    """
    __tablename__ = "fach"
    __table_args__ = (UniqueConstraint("regal_id", "bezeichnung"),)

    id = Column(Integer, primary_key=True, index=True)
    regal_id = Column(Integer, ForeignKey("regal.id"), nullable=False)
    bezeichnung = Column(String, nullable=False)
    beschreibung = Column(String, nullable=True)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    aktualisiert_am = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    regal = relationship("RegalORM", back_populates="faecher")
    stellplaetze = relationship("StellplatzORM", back_populates="fach", cascade="all, delete-orphan")

class StellplatzORM(Base):
    """
    ORM-Klasse für Stellplätze.
    """
    __tablename__ = "stellplatz"
    __table_args__ = (UniqueConstraint("fach_id", "position"),)

    id = Column(Integer, primary_key=True, index=True)
    fach_id = Column(Integer, ForeignKey("fach.id"), nullable=False)
    position = Column(Integer, nullable=False)
    szene_id = Column(Integer, ForeignKey("szene.id"), nullable=True)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    aktualisiert_am = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    fach = relationship("FachORM", back_populates="stellplaetze")
    szene = relationship("SzeneORM", back_populates="stellplatz")