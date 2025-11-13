# Museum-Projekt Class Overview

## Table of Contents
1. [Models](#models)
   1. [ORM Models](#orm-models)
   2. [Pydantic Models](#pydantic-models)
2. [Services](#services)
3. [Configuration](#configuration)
4. [Authentication](#authentication)
5. [API Models](#api-models)

## Models

### ORM Models

#### `MovieORM` (app/models/movie.py)
**Inheritance**: `Base` (SQLAlchemy declarative base)

**Description**: ORM class for movies stored in the database.

**Table Configuration**:
- `__tablename__` = "movie"
- `__table_args__` = (UniqueConstraint("titel", "erscheinungsjahr"),)

**Attributes**:
- `id`: Column(Integer, primary_key=True, index=True)
- `titel`: Column(String, nullable=False, index=True)
- `wiki_url`: Column(String, nullable=True)
- `erscheinungsjahr`: Column(Integer, nullable=False)
- `regisseur`: Column(String, nullable=True)
- `autor`: Column(String, nullable=True)
- `hauptdarsteller`: Column(String, nullable=True)
- `poster_url`: Column(String, nullable=True)
- `beschreibung`: Column(String, nullable=True)
- `pruefung`: Column(Boolean, default=False, nullable=False)
- `erstellt_am`: Column(DateTime(timezone=True), server_default=func.now())
- `aktualisiert_am`: Column(DateTime(timezone=True), onupdate=func.now())

### Pydantic Models

#### `MovieBase` (app/models/movie_schema.py)
**Inheritance**: `pydantic.BaseModel`

**Description**: Base model with common fields for movie input and output.

**Attributes**:
- `titel`: str = Field(..., description="Filmtitel")
- `erscheinungsjahr`: int | None = Field(None, description="Erscheinungsjahr")
- `wiki_url`: str | None = Field(None, description="Wikipedia-URL")
- `regisseur`: str | None = Field(None, description="Regisseur")
- `autor`: str | None = Field(None, description="Drehbuchautor")
- `hauptdarsteller`: str | None = Field(None, description="Hauptdarsteller")
- `poster_url`: str | None = Field(None, description="Poster-URL")
- `beschreibung`: str | None = Field(None, description="Kurzbeschreibung")
- `pruefung`: bool = Field(False, description="Flag für manuelle Prüfung")

**Configuration**:
```python
model_config = {
    "from_attributes": True
}
```

#### `MovieCreate` (app/models/movie_schema.py)
**Inheritance**: `MovieBase`

**Description**: Schema for creating new movies (POST /movies).

#### `Movie` (app/models/movie_schema.py)
**Inheritance**: `MovieBase`

**Description**: Schema for movie responses (GET/POST), includes primary key field.

**Additional Attributes**:
- `id`: int

**Configuration**:
```python
model_config = {
    "from_attributes": True
}
```

## Services

### `WikiImporter` (app/services/wiki_importer.py)
**Description**: Imports metadata for movies from Wikipedia/Wikidata.

**Static Methods**:
- `fetch(title: str) -> Dict[str, str]`: Retrieves field data for the given movie title.
  - **Parameters**:
    - `title`: Movie title (e.g., "Inception")
  - **Returns**: Dictionary with keys:
    - `director`
    - `author`
    - `main_cast`
    - `poster_url`
    - `description`

### Media Processing Functions (app/services/media_processor.py)

#### `generate_image_thumbnail`
**Signature**: `generate_image_thumbnail(movie_id: int, filename: str, size=(200, 200)) -> Path`

**Description**: Generates a thumbnail for an image.

**Parameters**:
- `movie_id`: ID of the movie
- `filename`: Name of the image file
- `size`: Tuple of (width, height) for the thumbnail, default is (200, 200)

**Returns**: Path to the generated thumbnail

**Behavior**:
1. Source: BASE/images/movies/{movie_id}/{filename}
2. Destination: BASE/images/movies/{movie_id}/thumbs/{filename}

#### `transcode_video`
**Signature**: `transcode_video(movie_id: int, filename: str, resolution="720p") -> Path`

**Description**: Transcodes a video using ffmpeg.

**Parameters**:
- `movie_id`: ID of the movie
- `filename`: Name of the video file
- `resolution`: Target resolution, default is "720p"

**Returns**: Path to the transcoded video

**Behavior**:
1. Source: BASE/videos/movies/{movie_id}/{filename}
2. Destination: BASE/videos/movies/{movie_id}/{resolution}/{filename}
3. If ffmpeg is missing or fails, the source file is copied as a fallback

## Configuration

### `Settings` (app/config.py)
**Inheritance**: `pydantic_settings.BaseSettings`

**Description**: Configuration settings for the application.

**Attributes**:
- **Environment / Mode**:
  - `app_env`: str = Field("dev", description="Umgebungsmodus: 'dev' oder 'prod'")

- **Server / Host Settings**:
  - `host`: str = Field("0.0.0.0", description="Host, auf dem der Server lauscht")
  - `port`: int = Field(8000, description="Port, auf dem der Server lauscht")

- **Database Configuration**:
  - `database_url`: str = Field("sqlite:///./test.db", description="URL für Datenbankverbindung")
  - `database_url_migrate`: Optional[str] = Field(None, description="URL für Schema-Migrationen; falls None, wird database_url verwendet")
  - `test_database_url`: Optional[str] = Field(None, description="URL für Test-Datenbank, z.B. bei APP_ENV=test", validation_alias="TEST_DATABASE_URL")

- **CORS & Security**:
  - `cors_allowed_origins`: List[str] = Field(["*"], description="Liste erlaubter Origins für CORS")
  - `secret_key`: str = Field("change-me", description="Secret Key für JWT-Authentifizierung")
  - `access_token_expire_minutes`: int = Field(30, description="Gültigkeit des Access-Tokens in Minuten")

- **Logging**:
  - `log_level`: str = Field("INFO", description="Standard-Logging-Level")
  - `log_format`: str = Field("%(levelname)s:%(name)s:%(message)s", description="Format für Log-Ausgaben")

- **Media / Static Files**:
  - `media_static_path`: Path = Field(Path("static"), description="Pfad für statische Medien")
  - `media_url`: str = Field("/static", description="URL-Prefix für Medien")

- **External Integrations & Feature Flags**:
  - `wikipedia_api_url`: str = Field("https://de.wikipedia.org/api/rest_v1", description="Basis-URL für Wikipedia-API")
  - `wikipedia_language`: str = Field("de", description="Sprache für Wikipedia-Abfragen (ISO-Code)")
  - `feature_thumbnails`: bool = Field(True, description="Feature-Flag zur Steuerung der Thumbnail-Erzeugung")

- **HTTP Basic Credentials**:
  - `editor_user`: str = Field("editor", description="Username für Editor")
  - `editor_pass`: str = Field("editorpass", description="Passwort für Editor")
  - `editor_role`: str = Field("editor", description="Rollen-Name für Editor")
  - `service_user`: str = Field("service", description="Username für Service/CRUD-User")
  - `service_pass`: str = Field("servicepass", description="Passwort für Service-User")
  - `service_role`: str = Field("service", description="Rollen-Name für Service-User")
  - `dev_user`: str = Field("dev", description="Username für Entwickler/Admin")
  - `dev_pass`: str = Field("devpass", description="Passwort für Entwickler/Admin")
  - `dev_role`: str = Field("developer", description="Rollen-Name für Entwickler/Admin")

**Configuration**:
```python
model_config = SettingsConfigDict(
    env_file=".env",
    env_prefix="APP_",
    case_sensitive=False,
    extra="ignore",
)
```

**Methods**:
- `_set_migrate_default(cls, v, info)`: Validator that sets database_url_migrate to database_url if not provided.
- `_parse_cors(cls, v)`: Validator that parses CORS origins from string to list.

## Authentication

### `Role` (app/auth.py)
**Inheritance**: `str, Enum`

**Description**: Enum defining user roles.

**Values**:
- `EDITOR` = "editor"
- `SERVICE` = "service"
- `DEVELOPER` = "developer"

## API Models

### `WikiImportRequest` (app/api/routes.py)
**Inheritance**: `pydantic.BaseModel`

**Description**: Request model for bulk import of movie data from Wikipedia.

**Attributes**:
- `titles`: List[str]

### `WikiImportStatus` (app/api/routes.py)
**Inheritance**: `pydantic.BaseModel`

**Description**: Response model for the progress of a wiki import.

**Attributes**:
- `status`: str
- `processed`: int
- `errors`: int

### `MediaItem` (app/api/routes.py)
**Inheritance**: `pydantic.BaseModel`

**Description**: Response model for a single media resource.

**Attributes**:
- `id`: int
- `url`: str
- `type`: str
- `title`: Optional[str] = None
