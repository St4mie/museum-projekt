# backend/app/api/endpoints.py
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.movie import MovieORM
from app.models.movie_schema import Movie
from app.services.wiki_importer import WikiImporter

router = APIRouter(prefix="/movies", tags=["movies"], responses={404: {"description": "Not found"}})


@router.post("/import/{movie_id}", response_model=Movie, summary="Import fehlender Felddaten aus Wikipedia")
def import_from_wiki(
    movie_id: int,
    db: Session = Depends(get_db),
) -> type[MovieORM]:
    movie = db.query(MovieORM).get(movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    try:
        # Hier den Cast verwenden, damit der Type-Checker weiß, dass wir ein str haben:
        movie_title: str = cast(str, movie.title)
        data = WikiImporter.fetch(movie_title)

        for field, value in data.items():
            if getattr(movie, field, None) is None:
                setattr(movie, field, value)

        db.commit()
        db.refresh(movie)
        return movie

    except Exception as e:
        movie.review = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Wiki-Import failed: {e}"
        )
