# backend/app/models/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Basisklasse für alle ORM-Modelle.
    Vererbt von SQLAlchemy 2.0 DeclarativeBase.
    """
    pass
