# backend/app/api/endpoints.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.auth import get_current_user
from app.models.movie import MovieORM
from app.models.movie_schema import (
    MovieCreate,
    Movie as MovieSchema,
)

router = APIRouter(prefix="/movies", tags=["movies"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[MovieSchema])
def read_movies(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_db),
):
    """
    GET /movies/
    Liefert eine paginierte Liste aller Filme.
    """
    return db_session.query(MovieORM).offset(skip).limit(limit).all()


@router.get("/{movie_id}", response_model=MovieSchema)
def read_movie(
    movie_id: int,
    db_session: Session = Depends(get_db),
):
    """
    GET /movies/{movie_id}
    Liefert ein einzelnes Movie-Objekt nach ID.
    Wirft 404, wenn nicht gefunden.
    """
    movie = db_session.query(MovieORM).filter(MovieORM.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.post("/", response_model=MovieSchema, status_code=201)
def create_movie(
    movie: MovieCreate,
    db_session: Session = Depends(get_db),
):
    """
    POST /movies/
    Legt einen neuen Film an.
    """
    exists = (
        db_session.query(MovieORM)
        .filter_by(titel=movie.titel, erscheinungsjahr=movie.erscheinungsjahr)
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="Movie already exists")
    movie_orm = MovieORM(**movie.model_dump())
    db_session.add(movie_orm)
    db_session.commit()
    db_session.refresh(movie_orm)
    return movie_orm


@router.post("/import/{movie_id}", response_model=MovieSchema)
def import_from_wiki(
    movie_id: int,
    db_session: Session = Depends(get_db),
):
    """
    POST /movies/import/{movie_id}
    Importiert Metadaten aus Wikipedia/Wikidata für den Film.
    """
    film = db_session.query(MovieORM).filter(MovieORM.id == movie_id).first()
    if not film:
        raise HTTPException(status_code=404, detail="Movie not found")
