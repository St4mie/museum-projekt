# backend/app/api/endpoints.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.movie_schema import Movie, MovieCreate
from app.models.movie import MovieORM
from app.services.wiki_importer import WikiImporter

router = APIRouter(prefix="/movies", tags=["movies"])

def get_db():
    """
    Liefert pro Request eine Datenbank-Session und schließt sie im Finally-Block.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[Movie])
def read_movies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Gibt eine paginierte Liste aller Filme zurück.
    """
    return db.query(MovieORM).offset(skip).limit(limit).all()


@router.post("/", response_model=Movie, status_code=201)
def create_movie(movie_in: MovieCreate, db: Session = Depends(get_db)):
    """
    Legt einen neuen Film an.
    """
    # Pydantic V2: .model_dump() statt .dict()
    db_movie = MovieORM(**movie_in.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


@router.post("/import/{movie_id}", response_model=Movie)
def import_from_wiki(movie_id: int, db: Session = Depends(get_db)):
    """
    Holt fehlende Felder per WikiImporter; im Fehlerfall review-Flag setzen.
    """
    movie = db.get(MovieORM, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    try:
        data = WikiImporter.fetch(movie.title)
        for field, value in data.items():
            if getattr(movie, field, None) is None:
                setattr(movie, field, value)
        db.commit()
        db.refresh(movie)
        return movie
    except Exception as e:
        movie.review = True
        db.commit()
        raise HTTPException(status_code=502, detail=str(e))
