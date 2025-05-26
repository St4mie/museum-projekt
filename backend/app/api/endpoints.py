# backend/app/api/endpoints.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.movie import MovieORM
from app.models.movie_schema import (
    MovieCreate,
    Movie as MovieSchema,
)
from app.services.wiki_importer import WikiImporter

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=List[MovieSchema])
def read_movies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    GET /movies/
    Liefert eine paginierte Liste aller Filme.
    """
    return db.query(MovieORM).offset(skip).limit(limit).all()


@router.get("/{movie_id}", response_model=MovieSchema)
def read_movie(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    GET /movies/{movie_id}
    Liefert ein einzelnes Movie-Objekt nach ID.
    Wirft 404, wenn nicht gefunden.
    """
    movie = db.get(MovieORM, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.post("/", response_model=MovieSchema, status_code=201)
def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
):
    """
    POST /movies/
    Legt einen neuen Film an.
    """
    exists = (
        db.query(MovieORM)
        .filter_by(title=movie.title, release_year=movie.release_year)
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="Movie already exists")
    movie_orm = MovieORM(**movie.model_dump())
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
    """
    film = db.get(MovieORM, movie_id)
    if not film:
        raise HTTPException(status_code=404, detail="Movie not found")
    try:
        data = WikiImporter.fetch(film.title)
        # Nur leere Felder überschreiben
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
