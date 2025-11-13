# Museum-Projekt: Benutzer- und Entwicklerhandbuch

<div align="center">
  <img src="https://via.placeholder.com/150?text=Museum+API" alt="Museum API Logo" width="150"/>
  <h3>Eine moderne API für Museumsanwendungen</h3>
  <p>Version 1.0 | Juni 2025</p>
</div>

## Inhaltsverzeichnis

1. [Einführung](#einführung)
   - [Über das Museum-Projekt](#über-das-museum-projekt)
   - [Hauptfunktionen](#hauptfunktionen)
   - [Zielgruppe](#zielgruppe)

2. [Systemarchitektur](#systemarchitektur)
   - [Überblick](#überblick)
   - [Komponenten](#komponenten)
   - [Technologie-Stack](#technologie-stack)
   - [Datenfluss](#datenfluss)

3. [Installation und Einrichtung](#installation-und-einrichtung)
   - [Voraussetzungen](#voraussetzungen)
   - [Installation](#installation)
   - [Konfiguration](#konfiguration)
   - [Starten der Anwendung](#starten-der-anwendung)

4. [Komponenten im Detail](#komponenten-im-detail)
   - [Backend (FastAPI)](#backend-fastapi)
   - [Datenbank (MariaDB)](#datenbank-mariadb)
   - [Medienverarbeitung](#medienverarbeitung)
   - [Wiki-Import](#wiki-import)

5. [API-Dokumentation](#api-dokumentation)
   - [Authentifizierung](#authentifizierung)
   - [Film-Endpunkte](#film-endpunkte)
   - [Medien-Endpunkte](#medien-endpunkte)
   - [Wiki-Import-Endpunkte](#wiki-import-endpunkte)

6. [Datenbankschema](#datenbankschema)
   - [Haupttabellen](#haupttabellen)
   - [Beziehungen](#beziehungen)
   - [Indizes und Constraints](#indizes-und-constraints)

7. [Entwicklungsrichtlinien](#entwicklungsrichtlinien)
   - [Codestruktur](#codestruktur)
   - [Coding Standards](#coding-standards)
   - [Tests schreiben](#tests-schreiben)
   - [Beitragen zum Projekt](#beitragen-zum-projekt)

8. [Fehlerbehebung](#fehlerbehebung)
   - [Häufige Probleme](#häufige-probleme)
   - [Logging](#logging)
   - [Debugging-Tipps](#debugging-tipps)

9. [Anhang](#anhang)
   - [Glossar](#glossar)
   - [Weiterführende Links](#weiterführende-links)
   - [Änderungshistorie](#änderungshistorie)

---

## Einführung

### Über das Museum-Projekt

Das Museum-Projekt ist eine moderne API-Lösung, die entwickelt wurde, um Museumsbesuchern einen interaktiven Zugang zu Filmdaten und Medieninhalten zu ermöglichen. Die Anwendung basiert auf einer FastAPI-Backend-Architektur mit einer MariaDB-Datenbank und bietet umfangreiche Funktionen zur Verwaltung von Filmen, Szenen, Exponaten und zugehörigen Medien.

Die API ermöglicht es Besuchern, über eine Web-App Filmdaten abzurufen sowie Bilder, Videos und Audiodateien anzusehen. Das System ist so konzipiert, dass es sowohl für kleine Museen als auch für größere Institutionen skalierbar ist.

### Hauptfunktionen

- **Filmverwaltung**: CRUD-Operationen für Filme mit Metadaten wie Titel, Regisseur, Autor, Hauptdarsteller und Beschreibung
- **Wiki-Import**: Automatischer Import von Filmdaten aus Wikipedia und Wikidata
- **Medienverwaltung**: Verwaltung von Bildern, Videos und Audiodateien zu Filmen
- **Medienverarbeitung**: Automatische Erstellung von Thumbnails und Videotranscodierung
- **Ausstellungsverwaltung**: Organisation von Ausstellungen, Räumen, Regalen und Exponaten
- **API-Zugriff**: RESTful API für den Zugriff auf alle Funktionen

### Zielgruppe

Dieses Handbuch richtet sich an zwei Hauptzielgruppen:

- **Benutzer**: Museumsmitarbeiter und Administratoren, die das System für die Verwaltung von Filmdaten und Medien nutzen
- **Entwickler**: Softwareentwickler, die das System erweitern, anpassen oder in andere Anwendungen integrieren möchten

---

## Systemarchitektur

### Überblick

Das Museum-Projekt folgt einer modernen, containerisierten Microservice-Architektur, die Skalierbarkeit, Wartbarkeit und einfache Bereitstellung ermöglicht.

<div align="center">
  <pre>
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │   Client    │────▶│   FastAPI   │────▶│   MariaDB   │
  │  (Browser)  │◀────│   Backend   │◀────│  Datenbank  │
  └─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                      ┌─────────────┐
                      │    Media    │
                      │  Processor  │
                      └─────────────┘
  </pre>
</div>

### Komponenten

1. **FastAPI Backend**:
   - Stellt die REST-API bereit
   - Verarbeitet Anfragen und Antworten
   - Implementiert Geschäftslogik und Datenvalidierung

2. **MariaDB Datenbank**:
   - Speichert alle strukturierten Daten
   - Verwaltet Beziehungen zwischen Entitäten
   - Unterstützt Volltextsuche und komplexe Abfragen

3. **Media Processor**:
   - Verarbeitet Medieninhalte (Bilder, Videos, Audio)
   - Erstellt Thumbnails für Bilder
   - Transkodiert Videos in verschiedene Auflösungen

4. **Wiki-Importer**:
   - Kommuniziert mit Wikipedia und Wikidata APIs
   - Extrahiert relevante Filmdaten
   - Aktualisiert die Datenbank mit importierten Informationen

### Technologie-Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy ORM
- **Datenbank**: MariaDB 10.6+
- **Medienverarbeitung**: Pillow (für Bilder), ffmpeg (für Videos)
- **Container**: Docker, Docker Compose
- **Authentifizierung**: HTTP Basic Auth, JWT Tokens
- **Externe APIs**: Wikipedia API, Wikidata API

### Datenfluss

1. Der Client sendet eine Anfrage an die FastAPI-Endpunkte
2. FastAPI validiert die Anfrage mit Pydantic-Modellen
3. Die Geschäftslogik verarbeitet die Anfrage und interagiert mit der Datenbank
4. Bei Medienanfragen werden Dateien verarbeitet und zurückgegeben
5. Bei Wiki-Importen werden externe APIs abgefragt und Daten importiert
6. Die Antwort wird an den Client zurückgegeben

---

## Installation und Einrichtung

### Voraussetzungen

Bevor Sie mit der Installation beginnen, stellen Sie sicher, dass folgende Komponenten auf Ihrem System installiert sind:

- **Docker & Docker Compose** (Version 1.29+ empfohlen)
- **Python 3.11+** (für lokale Entwicklung ohne Container)
- **ffmpeg** (für Videoverarbeitung)
- **Git** (für den Quellcode)

### Installation

1. **Repository klonen**:
   ```bash
   git clone https://github.com/St4mie/museum-projekt.git
   cd museum-projekt
   ```

2. **Entwicklungs-.env anlegen**:
   ```bash
   cp .env.example .env
   # .env nun mit lokalen Zugangsdaten füllen
   ```

3. **Docker Compose starten**:
   ```bash
   docker compose up --build --profile dev -d
   ```

4. **API prüfen**:
   ```bash
   curl http://localhost:8000/movies
   curl http://localhost:8000/media/images/movies/1
   ```

### Konfiguration

Alle konfigurierbaren Werte liegen in `backend/app/config.py` und werden über Umgebungsvariablen gesteuert. Die wichtigsten Einstellungen sind:

#### Datenbank

- **DATABASE_URL**: Connection-String für den Runtime-User
- **DATABASE_URL_MIGRATE**: Connection-String für Alembic-Migrationen
- **TEST_DATABASE_URL**: Connection-String für die Testdatenbank

#### Server

- **APP_HOST**: Host, auf dem der Server läuft
- **APP_PORT**: Port, auf dem der Server läuft

#### Medien

- **APP_MEDIA_STATIC_PATH**: Pfad im Container zum Ordner mit Bildern, Videos, Audio
- **APP_MEDIA_URL**: URL-Präfix für Mediendateien

#### Authentifizierung

- **APP_EDITOR_USER**, **APP_EDITOR_PASS**: Anmeldedaten für Editor
- **APP_SERVICE_USER**, **APP_SERVICE_PASS**: Anmeldedaten für Service
- **APP_DEV_USER**, **APP_DEV_PASS**: Anmeldedaten für Entwickler

#### Wikipedia-Integration

- **APP_WIKIPEDIA_API_URL**: Basis-URL für die Wikipedia-API
- **APP_WIKIPEDIA_LANGUAGE**: Sprache für Wikipedia-Abfragen (ISO-Code)

### Starten der Anwendung

#### Entwicklungsmodus

```bash
docker compose --profile dev up -d
```

#### Produktionsmodus

```bash
docker compose --profile prod up -d
```

#### Neustart und Rebuild

Für einen kompletten Neustart und Rebuild der Anwendung können die bereitgestellten Skripte verwendet werden:

- **Linux/macOS**:
  ```bash
  ./rebuild.sh
  ```

- **Windows**:
  ```powershell
  .\rebuild.ps1
  ```

---

## Komponenten im Detail

### Backend (FastAPI)

Das Backend ist das Herzstück der Anwendung und basiert auf dem FastAPI-Framework. Es bietet eine schnelle, moderne API mit automatischer Dokumentation und Typvalidierung.

#### Projektstruktur

```
backend/
├── app/
│   ├── api/            # API-Endpunkte
│   ├── models/         # Datenmodelle (ORM und Pydantic)
│   ├── services/       # Geschäftslogik
│   ├── templates/      # HTML-Templates
│   ├── config.py       # Konfiguration
│   └── main.py         # Hauptanwendung
├── tests/              # Automatisierte Tests
├── alembic/            # Datenbankmigrationen
└── requirements.txt    # Abhängigkeiten
```

#### Hauptmodule

- **api**: Enthält alle API-Endpunkte, gruppiert nach Funktionalität
- **models**: Definiert ORM-Modelle für SQLAlchemy und Pydantic-Schemas für API-Validierung
- **services**: Implementiert die Geschäftslogik, wie Wiki-Import und Medienverarbeitung

### Datenbank (MariaDB)

Die Datenbank speichert alle strukturierten Daten der Anwendung und ist in verschiedene Tabellen organisiert, die miteinander in Beziehung stehen.

#### Haupttabellen

- **movie**: Speichert Filmdaten wie Titel, Regisseur, Autor, etc.
- **szene**: Speichert Szenen zu Filmen
- **medium**: Speichert Medien (Audio/Video) zu Szenen
- **exponat**: Speichert Exponate, die in Szenen vorkommen können
- **ausstellung**, **raum**, **regal**, **fach**, **stellplatz**: Organisieren die physische Struktur des Museums

### Medienverarbeitung

Die Medienverarbeitung ist für die Verarbeitung von Bildern, Videos und Audiodateien zuständig. Sie bietet Funktionen zum Erstellen von Thumbnails und zum Transkodieren von Videos.

#### Hauptfunktionen

- **generate_image_thumbnail**: Erstellt Thumbnails für Bilder
- **transcode_video**: Transkodiert Videos in verschiedene Auflösungen
- **process_scene_media**: Verarbeitet Mediendateien für Szenen

#### Medientypen

- **Bilder**: JPEG, PNG
- **Videos**: MP4
- **Audio**: MP3

### Wiki-Import

Der Wiki-Import ermöglicht das automatische Abrufen von Filmdaten aus Wikipedia und Wikidata. Er nutzt die Wikipedia-API und die Wikidata-API, um relevante Informationen zu extrahieren.

#### Funktionsweise

1. Der Benutzer gibt einen Filmtitel ein
2. Der WikiImporter ruft die Wikipedia-API auf, um die Zusammenfassung des Films zu erhalten
3. Der WikiImporter ruft die Wikidata-API auf, um strukturierte Daten wie Regisseur, Autor, Hauptdarsteller und Poster-URL zu erhalten
4. Die extrahierten Daten werden in die Datenbank importiert

#### Importmodi

- **Einzelimport**: Importiert Daten für einen einzelnen Film
- **Bulk-Import**: Importiert Daten für mehrere Filme im Hintergrund

---

## API-Dokumentation

### Authentifizierung

Die API verwendet HTTP Basic Authentication für geschützte Endpunkte. Es gibt drei vordefinierte Benutzerrollen:

- **EDITOR**: Grundlegende Bearbeitungsrechte
- **SERVICE**: Dienst-/API-Zugriff
- **DEVELOPER**: Entwickler-/Admin-Zugriff

#### Authentifizierungsbeispiel

```bash
curl -u editor:password http://localhost:8000/movies
```

### Film-Endpunkte

#### GET /movies/

Listet alle Filme auf (paginierbar).

**Parameter**:
- `skip` (optional): Anzahl der zu überspringenden Einträge
- `limit` (optional): Maximale Anzahl der zurückzugebenden Einträge

**Beispiel**:
```bash
curl http://localhost:8000/movies?skip=0&limit=10
```

#### GET /movies/{movie_id}

Gibt Details zu einem einzelnen Film zurück.

**Parameter**:
- `movie_id`: ID des Films

**Beispiel**:
```bash
curl http://localhost:8000/movies/1
```

#### POST /movies/

Legt einen neuen Film an.

**Body**:
```json
{
  "titel": "Inception",
  "erscheinungsjahr": 2010,
  "regisseur": "Christopher Nolan",
  "autor": "Christopher Nolan",
  "hauptdarsteller": "Leonardo DiCaprio, Joseph Gordon-Levitt",
  "beschreibung": "Ein Dieb, der die Fähigkeit besitzt, in die Träume anderer einzudringen..."
}
```

**Beispiel**:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"titel":"Inception","erscheinungsjahr":2010}' http://localhost:8000/movies/
```

#### POST /movies/import/{movie_id}

Importiert Metadaten für einen Film aus Wikipedia.

**Parameter**:
- `movie_id`: ID des Films

**Beispiel**:
```bash
curl -X POST http://localhost:8000/movies/import/1
```

### Medien-Endpunkte

#### GET /media/images/movies/{movie_id}

Listet alle Bilder für einen Film auf.

**Parameter**:
- `movie_id`: ID des Films

**Beispiel**:
```bash
curl http://localhost:8000/media/images/movies/1
```

#### GET /media/images/movies/{movie_id}/{filename}

Gibt ein einzelnes Bild für einen Film zurück.

**Parameter**:
- `movie_id`: ID des Films
- `filename`: Name der Bilddatei

**Beispiel**:
```bash
curl http://localhost:8000/media/images/movies/1/poster.jpg
```

#### GET /media/videos/movies/{movie_id}

Listet alle Videos für einen Film auf.

**Parameter**:
- `movie_id`: ID des Films

**Beispiel**:
```bash
curl http://localhost:8000/media/videos/movies/1
```

#### GET /media/videos/movies/{movie_id}/{filename}

Gibt ein einzelnes Video für einen Film zurück.

**Parameter**:
- `movie_id`: ID des Films
- `filename`: Name der Videodatei

**Beispiel**:
```bash
curl http://localhost:8000/media/videos/movies/1/trailer.mp4
```

#### POST /media/process/{movie_id}

Verarbeitet Medien für einen Film (Thumbnails, Transcoding).

**Parameter**:
- `movie_id`: ID des Films

**Beispiel**:
```bash
curl -X POST http://localhost:8000/media/process/1
```

### Wiki-Import-Endpunkte

#### POST /wiki/import

Führt einen Bulk-Import von Filmdaten aus Wikipedia durch.

**Body**:
```json
{
  "titles": ["Inception", "The Dark Knight", "Interstellar"]
}
```

**Beispiel**:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"titles":["Inception","The Dark Knight"]}' http://localhost:8000/wiki/import
```

#### GET /wiki/import/status

Gibt den Status des Bulk-Imports zurück.

**Beispiel**:
```bash
curl http://localhost:8000/wiki/import/status
```

---

## Datenbankschema

### Haupttabellen

#### movie

| Spalte           | Typ                | Beschreibung                           |
|------------------|--------------------|-----------------------------------------|
| id               | INT UNSIGNED       | Primärschlüssel                        |
| titel            | VARCHAR(255)       | Filmtitel (nicht null, indiziert)      |
| wiki_url         | TEXT               | Wikipedia-URL                          |
| erscheinungsjahr | SMALLINT UNSIGNED  | Erscheinungsjahr                       |
| regisseur        | VARCHAR(255)       | Regisseur                              |
| autor            | VARCHAR(255)       | Drehbuchautor                          |
| hauptdarsteller  | TEXT               | Hauptdarsteller                        |
| poster_url       | TEXT               | URL zum Filmplakat                     |
| beschreibung     | TEXT               | Kurzbeschreibung                       |
| pruefung         | BOOLEAN            | Flag für manuelle Prüfung              |
| erstellt_am      | DATETIME           | Zeitstempel der Erstellung             |
| aktualisiert_am  | DATETIME           | Zeitstempel der letzten Aktualisierung |

#### szene

| Spalte           | Typ                | Beschreibung                           |
|------------------|--------------------|-----------------------------------------|
| id               | INT UNSIGNED       | Primärschlüssel                        |
| film_id          | INT UNSIGNED       | Fremdschlüssel zum Film                |
| name             | VARCHAR(255)       | Name der Szene                         |
| beschreibung     | TEXT               | Beschreibung der Szene                 |
| erstellt_am      | DATETIME           | Zeitstempel der Erstellung             |
| aktualisiert_am  | DATETIME           | Zeitstempel der letzten Aktualisierung |

#### medium

| Spalte           | Typ                | Beschreibung                           |
|------------------|--------------------|-----------------------------------------|
| id               | INT UNSIGNED       | Primärschlüssel                        |
| szene_id         | INT UNSIGNED       | Fremdschlüssel zur Szene               |
| dateipfad        | VARCHAR(1024)      | Pfad zur Mediendatei                   |
| medientyp        | ENUM('audio','video') | Typ des Mediums                     |
| erstellt_am      | DATETIME           | Zeitstempel der Erstellung             |
| aktualisiert_am  | DATETIME           | Zeitstempel der letzten Aktualisierung |

### Beziehungen

- **movie → szene**: Ein Film hat mehrere Szenen (1:n)
- **szene → medium**: Eine Szene hat mehrere Medien (1:n)
- **szene ↔ exponat**: Eine Szene kann mehrere Exponate haben, ein Exponat kann in mehreren Szenen vorkommen (m:n)
- **ausstellung → raum → regal → fach → stellplatz**: Hierarchische Beziehung der Museumsstruktur

### Indizes und Constraints

- **Primärschlüssel**: Jede Tabelle hat einen Primärschlüssel `id`
- **Fremdschlüssel**: Beziehungen zwischen Tabellen werden durch Fremdschlüssel definiert
- **Unique-Constraints**: Verhindern Duplikate in bestimmten Spalten
- **Indizes**: Beschleunigen Abfragen auf häufig verwendeten Spalten

---

## Entwicklungsrichtlinien

### Codestruktur

Das Projekt folgt einer klaren Struktur, die die Trennung von Zuständigkeiten fördert:

- **API-Endpunkte**: Definieren die HTTP-Schnittstelle und validieren Eingaben
- **Services**: Implementieren die Geschäftslogik
- **Models**: Definieren die Datenstruktur und -validierung
- **Config**: Zentralisiert die Konfiguration

### Coding Standards

- **PEP 8**: Befolgen Sie die Python-Stilrichtlinien
- **Typisierung**: Verwenden Sie Typhinweise für bessere IDE-Unterstützung und Dokumentation
- **Docstrings**: Dokumentieren Sie Funktionen und Klassen mit Docstrings
- **Kommentare**: Erklären Sie komplexe Logik mit Kommentaren

### Tests schreiben

Tests sind ein wichtiger Teil des Projekts und sollten für alle neuen Funktionen geschrieben werden:

- **Unit-Tests**: Testen einzelne Funktionen und Methoden
- **Integration-Tests**: Testen das Zusammenspiel mehrerer Komponenten
- **API-Tests**: Testen die API-Endpunkte

#### Beispiel für einen Test

```python
def test_create_movie():
    # Arrange
    test_movie = {"titel": "Test Movie", "erscheinungsjahr": 2025}
    
    # Act
    response = client.post("/movies/", json=test_movie)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["titel"] == "Test Movie"
```

### Beitragen zum Projekt

Wenn Sie zum Projekt beitragen möchten, befolgen Sie diese Schritte:

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch
3. Implementieren Sie Ihre Änderungen
4. Schreiben Sie Tests für Ihre Änderungen
5. Stellen Sie sicher, dass alle Tests bestehen
6. Erstellen Sie einen Pull Request

---

## Fehlerbehebung

### Häufige Probleme

#### 404 bei Medien

**Problem**: Mediendateien werden nicht gefunden.

**Lösung**:
- Überprüfen Sie den Wert von `MEDIA_STATIC_PATH` in der Konfiguration
- Stellen Sie sicher, dass die Dateinamen korrekt sind
- Überprüfen Sie die Berechtigungen der Dateien

#### ffmpeg-Fehler

**Problem**: Videotranscodierung schlägt fehl.

**Lösung**:
- Stellen Sie sicher, dass ffmpeg im Container installiert ist
- Überprüfen Sie die ffmpeg-Version
- Prüfen Sie die Logs auf spezifische Fehlermeldungen

#### Datenbank-Verbindungsfehler

**Problem**: Die Anwendung kann keine Verbindung zur Datenbank herstellen.

**Lösung**:
- Überprüfen Sie die Datenbank-URL in der Konfiguration
- Stellen Sie sicher, dass die Datenbank läuft
- Überprüfen Sie die Netzwerkverbindung zwischen Backend und Datenbank

### Logging

Die Anwendung verwendet das Python-Logging-System, um Informationen, Warnungen und Fehler zu protokollieren. Die Logs können auf verschiedene Arten eingesehen werden:

#### Docker-Logs

```bash
docker compose logs -f backend
```

#### Anwendungslogs

Die Anwendungslogs befinden sich im Container unter `/app/logs/app.log`.

### Debugging-Tipps

- **FastAPI Debug-Modus**: Aktivieren Sie den Debug-Modus in der Entwicklungsumgebung
- **SQLAlchemy Echo**: Aktivieren Sie `echo=True` in der SQLAlchemy-Engine, um SQL-Abfragen zu sehen
- **Pydantic Validation**: Nutzen Sie die Validierungsfehler von Pydantic, um Probleme mit Eingabedaten zu identifizieren

---

## Anhang

### Glossar

- **API**: Application Programming Interface
- **CRUD**: Create, Read, Update, Delete
- **FastAPI**: Python-Framework für schnelle API-Entwicklung
- **MariaDB**: Relationales Datenbankmanagementsystem
- **ORM**: Object-Relational Mapping
- **Pydantic**: Datenvalidierungs- und Einstellungsverwaltungsbibliothek
- **SQLAlchemy**: SQL-Toolkit und ORM für Python
- **Uvicorn**: ASGI-Server für Python

### Weiterführende Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Docker Compose Reference](https://docs.docker.com/compose/reference/)
- [Pillow (PIL) Documentation](https://pillow.readthedocs.io/en/stable/)
- [ffmpeg Documentation](https://ffmpeg.org/documentation.html)

### Änderungshistorie

- **Version 1.0** (Juni 2025): Erste Version des Benutzer- und Entwicklerhandbuchs