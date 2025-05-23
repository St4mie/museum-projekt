# backend/app/api/endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal        # DB-Session-Factory
from app.models.movie_schema import Movie, MovieCreate  # Pydantic-Schemata
from app.models.movie import MovieORM               # ORM-Modell
from app.services.wiki_importer import WikiImporter

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
    responses={404: {"description": "Not found"}}
)

def get_db():
    """
    FastAPI-Dependency: Öffnet für jeden Request eine neue DB-Session
    und schließt sie nach Gebrauch wieder.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/",
    response_model=list[Movie],
    summary="Liste aller Filme",
    description="Gibt bis zu `limit` Filme zurück, beginnend ab Offset `skip`."
)
def read_movies(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Lese-Funktion: Gibt eine paginierte Liste von Filmen zurück.
    """
    return db.query(MovieORM).offset(skip).limit(limit).all()

@router.post(
    "/",
    response_model=Movie,
    status_code=status.HTTP_201_CREATED,
    summary="Neuen Film anlegen",
    description="Legt einen neuen Film an. Titel+Jahr müssen eindeutig sein."
)
def create_movie(
    movie_in: MovieCreate,
    db: Session = Depends(get_db)
):
    """
    Legt einen neuen Film an. Prüft vorher, ob bereits ein Film
    mit demselben Titel und Jahr existiert, um Duplikate zu vermeiden.
    """
    # 1. Vorab-Check auf bestehende Kombination
    exists = (
        db.query(MovieORM)
          .filter(
              MovieORM.title == movie_in.title,
              MovieORM.release_year == movie_in.release_year
          )
          .first()
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Movie with this title and year already exists"
        )

    # 2. Anlegen und Commit, IntegrityError als Fallback
    db_movie = MovieORM(**movie_in.model_dump())  # Pydantic V2: model_dump()
    db.add(db_movie)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Movie already exists (DB constraint)"
        )
    db.refresh(db_movie)
    return db_movie

@router.post(
    "/import/{movie_id}",
    response_model=Movie,
    summary="Import fehlender Felddaten aus Wikipedia",
    description=(
        "Ergänzt per WikiImporter fehlende Felder und setzt im Fehlerfall "
        "`review=True`, um manuelle Nachbearbeitung anzustoßen."
    )
)
def import_from_wiki(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """
    Für den Film mit `movie_id` werden via WikiImporter:
      - description, director, author, main_cast, poster_url
    nachgeladen, **nur**, wenn das Feld aktuell `None` ist.
    Im Fehlerfall wird `review=True` gesetzt und ein 502-Error geworfen.
    """
    movie = db.get(MovieORM, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    try:
        importer = WikiImporter()
        data = importer.fetch(movie.title)
        # Nur vorhandene, bisher NULL-Felder überschreiben
        for field, value in data.items():
            if getattr(movie, field, None) is None:
                setattr(movie, field, value)
        db.commit()
        return movie

    except Exception as e:
        movie.review = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Wiki-Import failed: {e}"
        )
