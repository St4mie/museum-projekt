# backend/app/models/exhibition_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional

# Ausstellung (Exhibition) schemas
class AusstellungBase(BaseModel):
    """
    Gemeinsame Felder für Input und Output.
    """
    name: str = Field(..., description="Name der Ausstellung")
    beschreibung: Optional[str] = Field(None, description="Beschreibung der Ausstellung")

    model_config = {
        "from_attributes": True
    }

class AusstellungCreate(AusstellungBase):
    """
    Schema für neue Ausstellung (POST /exhibitions).
    """
    pass

class Ausstellung(AusstellungBase):
    """
    Schema für Ausstellung-Antwort (GET/POST);
    enthält zusätzlich das Primärschlüssel-Feld.
    """
    id: int

    model_config = {
        "from_attributes": True
    }

# Raum (Room) schemas
class RaumBase(BaseModel):
    """
    Gemeinsame Felder für Input und Output.
    """
    ausstellung_id: int = Field(..., description="ID der Ausstellung")
    name: str = Field(..., description="Name des Raums")
    beschreibung: Optional[str] = Field(None, description="Beschreibung des Raums")

    model_config = {
        "from_attributes": True
    }

class RaumCreate(RaumBase):
    """
    Schema für neuen Raum (POST /rooms).
    """
    pass

class Raum(RaumBase):
    """
    Schema für Raum-Antwort (GET/POST);
    enthält zusätzlich das Primärschlüssel-Feld.
    """
    id: int

    model_config = {
        "from_attributes": True
    }

# Regal (Shelf) schemas
class RegalBase(BaseModel):
    """
    Gemeinsame Felder für Input und Output.
    """
    raum_id: int = Field(..., description="ID des Raums")
    bezeichnung: str = Field(..., description="Bezeichnung des Regals")
    beschreibung: Optional[str] = Field(None, description="Beschreibung des Regals")

    model_config = {
        "from_attributes": True
    }

class RegalCreate(RegalBase):
    """
    Schema für neues Regal (POST /shelves).
    """
    pass

class Regal(RegalBase):
    """
    Schema für Regal-Antwort (GET/POST);
    enthält zusätzlich das Primärschlüssel-Feld.
    """
    id: int

    model_config = {
        "from_attributes": True
    }

# Fach (Compartment) schemas
class FachBase(BaseModel):
    """
    Gemeinsame Felder für Input und Output.
    """
    regal_id: int = Field(..., description="ID des Regals")
    bezeichnung: str = Field(..., description="Bezeichnung des Fachs")
    beschreibung: Optional[str] = Field(None, description="Beschreibung des Fachs")

    model_config = {
        "from_attributes": True
    }

class FachCreate(FachBase):
    """
    Schema für neues Fach (POST /compartments).
    """
    pass

class Fach(FachBase):
    """
    Schema für Fach-Antwort (GET/POST);
    enthält zusätzlich das Primärschlüssel-Feld.
    """
    id: int

    model_config = {
        "from_attributes": True
    }

# Stellplatz (Position) schemas
class StellplatzBase(BaseModel):
    """
    Gemeinsame Felder für Input und Output.
    """
    fach_id: int = Field(..., description="ID des Fachs")
    position: int = Field(..., description="Position im Fach")
    szene_id: Optional[int] = Field(None, description="ID der Szene (optional)")

    model_config = {
        "from_attributes": True
    }

class StellplatzCreate(StellplatzBase):
    """
    Schema für neuen Stellplatz (POST /positions).
    """
    pass

class Stellplatz(StellplatzBase):
    """
    Schema für Stellplatz-Antwort (GET/POST);
    enthält zusätzlich das Primärschlüssel-Feld.
    """
    id: int

    model_config = {
        "from_attributes": True
    }

# Nested schemas for hierarchical responses
class AusstellungWithRaeume(Ausstellung):
    """
    Erweiterte Ausstellung mit Räumen.
    """
    raeume: List[Raum] = []

    model_config = {
        "from_attributes": True
    }