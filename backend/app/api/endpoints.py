# backend/app/api/endpoints.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db                            # Holen der DB-Session
from app.models.movie import MovieORM                 # ORM-Klasse für DB-Operationen
from app.models.movie_schema import (                 # Pydantic-Schemas für Request/Response
    MovieCreate,
    Movie as MovieSchema,
)
from app.services.wiki_importer import WikiImporter   # Service für Wikipedia-Import

router = APIRouter(prefix="/movies", tags=["movies"])  # Alle Routen unter /movies

@router.get("/", response_model=List[MovieSchema])
def read_movies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    GET /movies/
    Liefert eine paginierte Liste aller Filme.
    - skip: Datensätze überspringen
    - limit: maximale Anzahl zurückgegebener Datensätze
    """
    movies = db.query(MovieORM).offset(skip).limit(limit).all()
    return movies

@router.post("/", response_model=MovieSchema, status_code=201)
def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
):
    """
    POST /movies/
    Legt einen neuen Film an.
    - movie: Payload mit title und release_year (siehe MovieCreate)
    Gibt bei Duplikat 409 Conflict zurück.
    """
    exists = (
        db.query(MovieORM)
        .filter_by(title=movie.title, release_year=movie.release_year)
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="Movie already exists")
    movie_orm = MovieORM(**movie.dict())  # DTO → ORM
    db.add(movie_orm)
    db.commit()
    db.refresh(movie_orm)
    return movie_orm

@router.post("/import/{movie_id}", response_model=MovieSchema)
def import_from_wiki(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    POST /movies/import/{movie_id}
    Importiert Metadaten aus Wikipedia/Wikidata für den Film.
    - movie_id: ID des angelegten Films (nur title+release_year)
    Bei Fehler: setzt review=True, wirft 502 Bad Gateway.
    """
    film = db.get(MovieORM, movie_id)
    if not film:
        raise HTTPException(status_code=404, detail="Movie not found")
    try:
        data = WikiImporter.fetch(film.title)
        # Nur Felder befüllen, die noch leer oder None sind
        for key, value in data.items():
            if getattr(film, key, None) in (None, "", []):
                setattr(film, key, value)
        db.commit()
        db.refresh(film)
        return film
    except Exception as e:
        film.review = True
        db.commit()
        raise HTTPException(status_code=502, detail=str(e))
