# backend/app/models/scene_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

# Szene (Scene) schemas
class SzeneBase(BaseModel):
    """
    Gemeinsame Felder für Input und Output.
    """
    film_id: int = Field(..., description="ID des Films")
    name: str = Field(..., description="Name der Szene")
    beschreibung: Optional[str] = Field(None, description="Beschreibung der Szene")

    model_config = {
        "from_attributes": True
    }

class SzeneCreate(SzeneBase):
    """
    Schema für neue Szene (POST /scenes).
    """
    pass

class Szene(SzeneBase):
    """
    Schema für Szene-Antwort (GET/POST);
    enthält zusätzlich das Primärschlüssel-Feld.
    """
    id: int

    model_config = {
        "from_attributes": True
    }

# Medium (Media) schemas
class MediumBase(BaseModel):
    """
    Gemeinsame Felder für Input und Output.
    """
    szene_id: int = Field(..., description="ID der Szene")
    dateipfad: str = Field(..., description="Pfad zur Mediendatei")
    medientyp: str = Field(..., description="Typ des Mediums (audio/video)")

    model_config = {
        "from_attributes": True
    }

class MediumCreate(MediumBase):
    """
    Schema für neues Medium (POST /media).
    """
    pass

class Medium(MediumBase):
    """
    Schema für Medium-Antwort (GET/POST);
    enthält zusätzlich das Primärschlüssel-Feld.
    """
    id: int

    model_config = {
        "from_attributes": True
    }

# Exponat (Exhibit) schemas
class ExponatBase(BaseModel):
    """
    Gemeinsame Felder für Input und Output.
    """
    name: str = Field(..., description="Name des Exponats")
    beschreibung: Optional[str] = Field(None, description="Beschreibung des Exponats")
    hersteller: Optional[str] = Field(None, description="Hersteller des Exponats")
    baujahr: Optional[int] = Field(None, description="Baujahr des Exponats")
    material: Optional[str] = Field(None, description="Material des Exponats")
    wert: Optional[Decimal] = Field(None, description="Wert des Exponats")
    anzahl: int = Field(1, description="Anzahl der Exponate")

    model_config = {
        "from_attributes": True
    }

class ExponatCreate(ExponatBase):
    """
    Schema für neues Exponat (POST /exhibits).
    """
    pass

class Exponat(ExponatBase):
    """
    Schema für Exponat-Antwort (GET/POST);
    enthält zusätzlich das Primärschlüssel-Feld.
    """
    id: int

    model_config = {
        "from_attributes": True
    }

# Szene with relationships
class SzeneWithRelations(Szene):
    """
    Erweiterte Szene mit Beziehungen.
    """
    medien: List[Medium] = []
    exponate: List[Exponat] = []

    model_config = {
        "from_attributes": True
    }