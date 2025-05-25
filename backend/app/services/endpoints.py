from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from app.db import Base  # Basisklasse mit Meta-Infos

class MovieORM(Base):
    """
    SQLAlchemy-ORM-Modell für die Tabelle 'movie'.
    """
    __tablename__ = "movie"
    __table_args__ = (
        UniqueConstraint("title", "release_year", name="uq_movie_title_year"),
    )

    # Hier kommt je ein PEP-484-Hint vor das Column-Objekt:
    id:                int     = Column(Integer, primary_key=True, index=True)
    title:             str     = Column(String(255), nullable=False)
    release_year:      Optional[int] = Column(Integer, nullable=True)
    wiki_url:          Optional[str] = Column(Text, nullable=True)
    director:          Optional[str] = Column(String(255), nullable=True)
    author:            Optional[str] = Column(String(255), nullable=True)
    main_cast:         Optional[str] = Column(Text, nullable=True)
    poster_url:        Optional[str] = Column(Text, nullable=True)
    description:       Optional[str] = Column(Text, nullable=True)
    review:            bool    = Column(Boolean, nullable=False, default=False)
    created_at:        object  = Column(  # SQL-Alchemy liefert hier einen datetime-ähnlichen Typ
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False
    )
    updated_at:        object  = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
