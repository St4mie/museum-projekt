# Museum-Projekt Dokumentation

## Inhaltsverzeichnis
1. [Projektübersicht](#projektübersicht)
2. [Systemarchitektur](#systemarchitektur)
3. [API-Endpunkte](#api-endpunkte)
4. [Datenmodelle](#datenmodelle)
5. [Authentifizierung und Sicherheit](#authentifizierung-und-sicherheit)
6. [Konfigurationsoptionen](#konfigurationsoptionen)
7. [Deployment-Anleitung](#deployment-anleitung)
8. [Tests](#tests)

## Projektübersicht
Das Museum-Projekt ist eine FastAPI-basierte Anwendung zur Verwaltung von Filmdaten und zugehörigen Medien (Bilder, Videos, Audio). Die Anwendung ermöglicht das Importieren von Filmdaten aus Wikipedia, das Verwalten von Filmen in einer Datenbank und das Bereitstellen von Medieninhalten über eine REST-API.

### Hauptfunktionen
- CRUD-Operationen für Filme
- Import von Filmdaten aus Wikipedia
- Verwaltung von Medieninhalten (Bilder, Videos, Audio)
- Verarbeitung von Medien (Thumbnails, Videotranscodierung)
- HTTP Basic Authentication für geschützte Endpunkte

## Systemarchitektur
Die Anwendung besteht aus mehreren Komponenten:

### Backend (FastAPI)
- **FastAPI-Anwendung**: Stellt die REST-API bereit
- **SQLAlchemy ORM**: Datenbankzugriff und Modellierung
- **Pydantic**: Datenvalidierung und Schemas
- **Wikipedia/Wikidata-Integration**: Import von Filmdaten

### Datenbank (MariaDB)
- **Hauptdatenbank**: `museum_db` für Produktionsdaten
- **Testdatenbank**: `museum_db_test` für automatisierte Tests

### Docker-Deployment
- **Docker Compose**: Orchestrierung der Dienste
- **Separate Container**: Backend, Datenbank, Seed-Daten

## API-Endpunkte

### Root-Endpunkte
- `GET /`: Willkommensnachricht
- `GET /media`: Liste aller Medientypen (Mock)
- `GET /media/{media_id}`: Details eines einzelnen Medienelements (Mock)

### Film-Endpunkte (Authentifizierung erforderlich)
- `GET /movies/`: Liste aller Filme
- `GET /movies/{movie_id}`: Details eines einzelnen Films
- `POST /movies/`: Neuen Film anlegen
- `POST /movies/import/{movie_id}`: Metadaten für einen Film aus Wikipedia importieren

### Wiki-Import-Endpunkte (Authentifizierung erforderlich)
- `POST /wiki/import`: Bulk-Import von Filmdaten aus Wikipedia
- `GET /wiki/import/status`: Status des Bulk-Imports

### Medien-Endpunkte
- `GET /media/images/movies/{movie_id}`: Liste aller Bilder für einen Film
- `GET /media/images/movies/{movie_id}/{filename}`: Einzelnes Bild für einen Film
- `GET /media/videos/movies/{movie_id}`: Liste aller Videos für einen Film
- `GET /media/videos/movies/{movie_id}/{filename}`: Einzelnes Video für einen Film
- `GET /media/audio/movies/{movie_id}`: Liste aller Audiodateien für einen Film
- `GET /media/audio/movies/{movie_id}/{filename}`: Einzelne Audiodatei für einen Film
- `POST /media/process/{movie_id}`: Verarbeitung von Medien für einen Film (Thumbnails, Transcoding)

## Datenmodelle

Die Datenbank des Museum-Projekts besteht aus mehreren miteinander verbundenen Tabellen. Eine vollständige grafische Darstellung der Datenbankstruktur ist in den folgenden ER-Diagrammen verfügbar:

- [Textbasiertes ER-Diagramm](../../backend/docs/database_er_diagram.md)
- [Mermaid ER-Diagramm](../../backend/docs/database_er_diagram_mermaid.md)
- [XML-Datenmodell Film](../diagrams/Datenmodell%20Film.xml)

### Film (MovieORM)
- `id`: Primärschlüssel
- `titel`: Filmtitel (nicht null, indiziert)
- `wiki_url`: Wikipedia-URL
- `erscheinungsjahr`: Erscheinungsjahr (nicht null)
- `regisseur`: Regisseur
- `autor`: Drehbuchautor
- `hauptdarsteller`: Hauptdarsteller
- `poster_url`: URL zum Filmplakat
- `beschreibung`: Kurzbeschreibung
- `pruefung`: Flag für manuelle Prüfung (Boolean, Standard: false)
- `erstellt_am`: Zeitstempel der Erstellung
- `aktualisiert_am`: Zeitstempel der letzten Aktualisierung

### Szene (SzeneORM)
- `id`: Primärschlüssel
- `film_id`: Fremdschlüssel zum Film
- `name`: Name der Szene
- `beschreibung`: Beschreibung der Szene
- `erstellt_am`: Zeitstempel der Erstellung
- `aktualisiert_am`: Zeitstempel der letzten Aktualisierung

### Medium (MediumORM)
- `id`: Primärschlüssel
- `szene_id`: Fremdschlüssel zur Szene
- `dateipfad`: Pfad zur Mediendatei
- `medientyp`: Typ des Mediums (audio, video)
- `erstellt_am`: Zeitstempel der Erstellung
- `aktualisiert_am`: Zeitstempel der letzten Aktualisierung

### Exponat (ExponatORM)
- `id`: Primärschlüssel
- `name`: Name des Exponats
- `beschreibung`: Beschreibung des Exponats
- `hersteller`: Hersteller des Exponats
- `baujahr`: Baujahr des Exponats
- `material`: Material des Exponats
- `wert`: Wert des Exponats
- `anzahl`: Anzahl der Exponate
- `erstellt_am`: Zeitstempel der Erstellung
- `aktualisiert_am`: Zeitstempel der letzten Aktualisierung

### Ausstellung (AusstellungORM)
- `id`: Primärschlüssel
- `name`: Name der Ausstellung
- `beschreibung`: Beschreibung der Ausstellung
- `erstellt_am`: Zeitstempel der Erstellung
- `aktualisiert_am`: Zeitstempel der letzten Aktualisierung

### Weitere Modelle
Weitere Modelle wie RaumORM, RegalORM, FachORM und StellplatzORM sind in den ER-Diagrammen dokumentiert.

## Authentifizierung und Sicherheit
Die Anwendung verwendet HTTP Basic Authentication für geschützte Endpunkte. Es gibt drei vordefinierte Benutzerrollen:

### Rollen
- **EDITOR**: Grundlegende Bearbeitungsrechte
- **SERVICE**: Dienst-/API-Zugriff
- **DEVELOPER**: Entwickler-/Admin-Zugriff

### Datenbank-Benutzer
- **entwickler**: Volle Rechte für Migrationen
- **museum**: CRUD-Operationen für Content-Management
- **service**: Import- und API-Benutzer mit Schema-Änderungsrechten
- **test_user**: Dedizierter Benutzer für Tests mit vollen Rechten auf der Testdatenbank
- **system**: Nur-Lese-Zugriff für Monitoring
- **benutzer**: Öffentlicher Nur-Lese-Zugriff

## Konfigurationsoptionen
Die Anwendung wird über Umgebungsvariablen und eine `.env`-Datei konfiguriert. Wichtige Konfigurationsoptionen sind:

### Umgebung
- `APP_ENV`: Umgebungsmodus ('dev', 'test', 'prod')

### Server
- `APP_HOST`: Host, auf dem der Server läuft
- `APP_PORT`: Port, auf dem der Server läuft

### Datenbank
- `DATABASE_URL`: URL für die Hauptdatenbank
- `DATABASE_URL_MIGRATE`: URL für Datenbankmigrationen
- `TEST_DATABASE_URL`: URL für die Testdatenbank

### Medien
- `APP_MEDIA_STATIC_PATH`: Pfad für statische Mediendateien
- `APP_MEDIA_URL`: URL-Präfix für Mediendateien

### Authentifizierung
- `APP_EDITOR_USER`, `APP_EDITOR_PASS`: Anmeldedaten für Editor
- `APP_SERVICE_USER`, `APP_SERVICE_PASS`: Anmeldedaten für Service
- `APP_DEV_USER`, `APP_DEV_PASS`: Anmeldedaten für Entwickler

### Wikipedia-Integration
- `APP_WIKIPEDIA_API_URL`: Basis-URL für die Wikipedia-API
- `APP_WIKIPEDIA_LANGUAGE`: Sprache für Wikipedia-Abfragen (ISO-Code)

## Deployment-Anleitung

### Voraussetzungen
- Docker und Docker Compose
- Git (für den Quellcode)

### Installation und Start
1. Repository klonen:
   ```bash
   git clone <repository-url>
   cd museum-projekt
   ```

2. `.env`-Datei erstellen oder anpassen:
   ```
   # Datenbank
   DB_ROOT_PASSWORD=root_password
   DB_NAME=museum_db
   DB_USER=service
   DB_PASSWORD=Starten2025!
   DB_HOST=db
   DB_PORT=3306

   # Verbindungs-URLs
   DATABASE_URL=mysql+pymysql://service:Starten2025!@db:3306/museum_db
   DATABASE_URL_MIGRATE=mysql+pymysql://entwickler:Starten2025!@db:3306/museum_db
   TEST_DATABASE_URL=mysql+pymysql://test_user:Test2025!@db:3306/museum_db_test

   # Anwendungseinstellungen
   APP_ENV=dev
   APP_HOST=0.0.0.0
   APP_PORT=8000
   ```

3. Docker-Container im Dev Mode starten:
   ```bash
   docker-compose --profile dev up -d
   ```

4. Anwendung testen:
   ```bash
   curl http://localhost:8000/
   ```

### Neustart und Rebuild
Für einen kompletten Neustart und Rebuild der Anwendung können die bereitgestellten Skripte verwendet werden:

- **Linux/macOS**:
  ```bash
  ./rebuild.sh
  ```

- **Windows**:
  ```powershell
  .\rebuild.ps1
  ```

## Tests
Die Anwendung enthält automatisierte Tests für verschiedene Komponenten:

### Testarten
- **API-Tests**: Testen der API-Endpunkte
- **Authentifizierungstests**: Testen der Authentifizierungsmechanismen
- **Medienverarbeitungstests**: Testen der Medienverarbeitungsfunktionen
- **Wiki-Importtests**: Testen des Wikipedia-Imports

### Testausführung
Tests können mit pytest ausgeführt werden:

```bash
# Im Backend-Container
docker-compose exec backend pytest

# Lokal (wenn Python-Umgebung eingerichtet ist)
cd backend
python -m pytest
```

### Test-Coverage
Die Anwendung unterstützt Test-Coverage-Berichte mit pytest-cov:

```bash
# Im Backend-Container
docker-compose exec backend pytest --cov=app

# Lokal (wenn Python-Umgebung eingerichtet ist)
cd backend
python -m pytest --cov=app
```

Unter Windows kann das bereitgestellte Batch-Skript verwendet werden:

```powershell
cd backend
.\run_tests_with_coverage.bat
```

Dieses Skript führt die Tests mit Coverage aus und generiert sowohl einen Terminal-Bericht als auch einen HTML-Bericht im Verzeichnis `htmlcov/`.

### Testumgebung
Die Tests verwenden eine separate Testdatenbank (`museum_db_test`), um die Produktionsdaten nicht zu beeinflussen. Die Testumgebung wird über die Umgebungsvariable `APP_ENV=test` konfiguriert.
