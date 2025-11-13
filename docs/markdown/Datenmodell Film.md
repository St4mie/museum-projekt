# Datenmodell Film

## Übersicht
Das Datenmodell "Film" repräsentiert Filme in der Museumsdatenbank. Es speichert grundlegende Informationen über Filme wie Titel, Erscheinungsjahr, Regisseur, Autor, Hauptdarsteller sowie zusätzliche Metadaten wie Beschreibungen und Poster-URLs.

## Datenbankschema

Die Filme werden in der Tabelle `movie` gespeichert:

```sql
CREATE TABLE IF NOT EXISTS `movie` (
  `id`              INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `titel`           VARCHAR(255) NOT NULL,
  `wiki_url`        TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `erscheinungsjahr` SMALLINT UNSIGNED,
  `regisseur`       VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `autor`           VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `hauptdarsteller` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `poster_url`      TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `beschreibung`    TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `pruefung`        BOOLEAN NOT NULL DEFAULT FALSE,
  `erstellt_am`     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `aktualisiert_am` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                     ON UPDATE CURRENT_TIMESTAMP,
  INDEX (`titel`),
  INDEX (`erscheinungsjahr`),
  FULLTEXT INDEX `ft_titel_beschreibung` (`titel`, `beschreibung`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Tabelle für Filme (Import aus Wikipedia)';
```

## Attribute

| Attribut | Datentyp | Beschreibung | Constraints |
|----------|----------|--------------|------------|
| id | INT UNSIGNED | Eindeutige ID des Films | PRIMARY KEY, AUTO_INCREMENT |
| titel | VARCHAR(255) | Titel des Films | NOT NULL, INDEX |
| wiki_url | TEXT | URL zur Wikipedia-Seite des Films | Optional |
| erscheinungsjahr | SMALLINT UNSIGNED | Jahr der Veröffentlichung | Optional, INDEX |
| regisseur | VARCHAR(255) | Name des Regisseurs | Optional |
| autor | VARCHAR(255) | Name des Drehbuchautors | Optional |
| hauptdarsteller | TEXT | Liste der Hauptdarsteller | Optional |
| poster_url | TEXT | URL zum Filmposter | Optional |
| beschreibung | TEXT | Kurzbeschreibung des Films | Optional |
| pruefung | BOOLEAN | Flag für manuelle Prüfung | NOT NULL, DEFAULT FALSE |
| erstellt_am | DATETIME | Zeitstempel der Erstellung | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| aktualisiert_am | DATETIME | Zeitstempel der letzten Aktualisierung | NOT NULL, DEFAULT CURRENT_TIMESTAMP, ON UPDATE CURRENT_TIMESTAMP |

## Indizes
- Primärschlüssel: `id`
- Index auf `titel` für schnelle Suche nach Filmtiteln
- Index auf `erscheinungsjahr` für schnelle Filterung nach Erscheinungsjahr
- Volltext-Index auf `titel` und `beschreibung` für Volltextsuche

## ORM-Modell

Das Film-Datenmodell wird in der Anwendung durch die `MovieORM`-Klasse repräsentiert:

```python
# backend/app/models/movie.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.sql import func                     # für automatische Timestamp-Defaults

from app.db import Base                            # Basisklasse für deklaratives ORM

class MovieORM(Base):
    """
    ORM-Klasse für Filme.
    - __tablename__: Name der DB-Tabelle
    - __table_args__: Composite-Unique-Constraint auf titel+erscheinungsjahr
    """
    __tablename__ = "movie"
    __table_args__ = (UniqueConstraint("titel", "erscheinungsjahr"),)

    id = Column(Integer, primary_key=True, index=True)
    titel = Column(String, nullable=False, index=True)
    wiki_url = Column(String, nullable=True)
    erscheinungsjahr = Column(Integer, nullable=False)
    regisseur = Column(String, nullable=True)
    autor = Column(String, nullable=True)
    hauptdarsteller = Column(String, nullable=True)
    poster_url = Column(String, nullable=True)
    beschreibung = Column(String, nullable=True)
    pruefung = Column(Boolean, default=False, nullable=False)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    aktualisiert_am = Column(DateTime(timezone=True), onupdate=func.now())
```

## API-Schemas (Pydantic-Modelle)

Für die API-Kommunikation werden Pydantic-Modelle verwendet:

```python
# backend/app/models/movie_schema.py

from pydantic import BaseModel, Field

class MovieBase(BaseModel):
    """
    Gemeinsame Felder für Input und Output.
    """
    titel: str = Field(..., description="Filmtitel")
    erscheinungsjahr: int | None = Field(None, description="Erscheinungsjahr")
    wiki_url: str | None = Field(None, description="Wikipedia-URL")
    regisseur: str | None = Field(None, description="Regisseur")
    autor: str | None = Field(None, description="Drehbuchautor")
    hauptdarsteller: str | None = Field(None, description="Hauptdarsteller")
    poster_url: str | None = Field(None, description="Poster-URL")
    beschreibung: str | None = Field(None, description="Kurzbeschreibung")
    pruefung: bool = Field(False, description="Flag für manuelle Prüfung")

    # Pydantic v2: damit wir ORM-Instanzen direkt serialisieren können
    model_config = {
        "from_attributes": True
    }


class MovieCreate(MovieBase):
    """
    Schema für neues Movie (POST /movies).
    Erbt alles von MovieBase – kein eigenes Feld nötig.
    """
    pass


class Movie(MovieBase):
    """
    Schema für Movie-Antwort (GET/POST);
    enthält zusätzlich das Primärschlüssel-Feld.
    """
    id: int

    model_config = {
        "from_attributes": True
    }
```

## API-Endpunkte

Das Film-Datenmodell wird über folgende API-Endpunkte zugänglich gemacht:

- `GET /movies/`: Liste aller Filme abrufen (paginiert)
- `GET /movies/{movie_id}`: Einzelnen Film nach ID abrufen
- `POST /movies/`: Neuen Film anlegen
- `POST /movies/import/{movie_id}`: Metadaten für einen Film aus Wikipedia/Wikidata importieren

## Beziehungen zu anderen Modellen

Das Film-Modell steht in Beziehung zu anderen Modellen im System:

- Szenen: Eine Szene gehört zu genau einem Film (über `film_id` → `movie.id`)
- Medien: Medien wie Bilder, Videos oder Audiodateien können mit Filmen verknüpft sein
- Exponate: Physische Ausstellungsstücke können mit Filmen in Verbindung stehen

## Verwendung im Code

Beispiel für das Erstellen eines neuen Films:

```python
# Beispiel: Neuen Film anlegen
movie_data = MovieCreate(
    titel="Der Pate",
    erscheinungsjahr=1972,
    regisseur="Francis Ford Coppola",
    autor="Mario Puzo, Francis Ford Coppola",
    hauptdarsteller="Marlon Brando, Al Pacino, James Caan",
    beschreibung="Ein Mafia-Epos über die Familie Corleone in New York."
)

# In der Datenbank speichern
movie_orm = MovieORM(**movie_data.model_dump())
db_session.add(movie_orm)
db_session.commit()
db_session.refresh(movie_orm)
```

Beispiel für das Abrufen eines Films:

```python
# Beispiel: Film nach ID abrufen
movie = db_session.query(MovieORM).filter(MovieORM.id == movie_id).first()
if movie:
    # Film gefunden
    print(f"Titel: {movie.titel}, Jahr: {movie.erscheinungsjahr}")
else:
    # Film nicht gefunden
    print("Film nicht gefunden")
```