# Projektstruktur

Dieses Dokument beschreibt die aktuelle Ordner- und Projektstruktur des Museum-Projekts. Es dient als Referenz für Entwickler und kann bei Änderungen dynamisch aktualisiert werden.

## Hauptverzeichnisse

- **backend/**: Enthält den FastAPI-basierten Backend-Code
- **database/**: Enthält Datenbankinitialisierungsskripte und -konfigurationen
- **docs/**: Enthält Dokumentation und Diagramme
  - **diagrams/**: XML-Diagrammdateien
  - **markdown/**: Markdown-Dokumentationsdateien
  - **presentations/**: Präsentationsdateien
- **venv/**: Python-Virtualenv (nicht im Repository enthalten)
- **.venv/**: Alternative Python-Virtualenv (nicht im Repository enthalten)

## Backend-Struktur

### Hauptmodule

- **app/**: Hauptanwendungscode
  - **api/**: API-Endpunkte und Routen
  - **models/**: Datenbankmodelle (ORM) und Schemas (Pydantic)
  - **services/**: Geschäftslogik und externe Dienste
  - **auth.py**: Authentifizierung und Autorisierung
  - **config.py**: Konfigurationseinstellungen
  - **db.py**: Datenbankverbindung und -session
  - **main.py**: Hauptanwendungseinstiegspunkt

### Tests

- **tests/**: Testcode
  - **conftest.py**: Gemeinsame Test-Fixtures
  - **test_integration.py**: Integrationstests
  - **test_media_endpoint.py**: Tests für Media-Endpunkte
  - **test_media_processor.py**: Tests für Medienverarbeitung
  - **test_api.py**: API-Tests (Redundanzen entfernt)
  - **test_auth.py**: Auth-Tests (Redundanzen entfernt)
  - **test_bulk_import.py**: Import-Tests (Redundanzen entfernt)
  - **test_smoke.py**: Einfache Smoke-Tests (Redundanzen entfernt)
  - **test_wiki_importer.py**: Tests für Wikipedia-Import

### Test-Konfiguration

- **.coveragerc**: Konfiguration für Test-Coverage
- **run_tests_with_coverage.bat**: Batch-Skript zum Ausführen von Tests mit Coverage-Bericht

### Statische Dateien

- **static/**: Statische Dateien für Medien
  - **audio/**: Audiodateien
  - **images/**: Bilddateien
  - **videos/**: Videodateien

## Datenbank-Struktur

- **database/init/**: Initialisierungsskripte für die Hauptdatenbank
- **database/dev-init/**: Entwicklungsdatenbank-Initialisierung

## Konfigurationsdateien

- **.env**: Umgebungsvariablen (nicht im Repository enthalten)
- **.env.example**: Beispiel für Umgebungsvariablen
- **.flake8**: Flake8-Konfiguration
- **.gitignore**: Git-Ignore-Konfiguration
- **.pre-commit-config.yaml**: Pre-Commit-Hook-Konfiguration
- **docker-compose.yml**: Docker-Compose-Konfiguration
- **mypy.ini**: MyPy-Konfiguration
- **pytest.ini**: PyTest-Konfiguration

## Dokumentation

- **README.md**: Hauptprojektdokumentation (im Root-Verzeichnis und in docs\markdown)
- **docs/markdown/**: Markdown-Dokumentationsdateien
  - **Documentation.md**: Ausführliche Projektdokumentation
  - **class overview.md**: Übersicht der Klassenstruktur
  - **Projektstruktur.md**: Dieses Dokument - Übersicht der Projektstruktur
  - **Datenmodell Film.md**: Dokumentation des Datenmodells für Filme
  - **usecase.md**: Anwendungsfälle des Projekts
  - **Museum-Projekt_Präsentation.md**: Präsentationsinhalte
  - **Museum-Projekt_Präsentation_mit_Notizen.md**: Präsentation mit Notizen
  - **Präsentation_README.md**: Anleitung zur Präsentation
- **docs/diagrams/**: XML-Diagrammdateien
  - **Projektmanagment.xml**: Diagramm zum Projektmanagement
  - **Sequenzdiagramm Film anlegen.xml**: Sequenzdiagramm für das Anlegen eines Films
  - **REST-API-Diagramm.xml**: Diagramm der REST-API
  - **Datenmodell Film.xml**: Diagramm des Datenmodells für Filme
  - **Codebeispielt Fast-Api.xml**: Codebeispiel für FastAPI
  - **ORM-Datenmodell.xml**: Diagramm des ORM-Datenmodells
- **docs/presentations/**: Präsentationsdateien
  - **Museum-Projekt_Präsentation.pptx**: PowerPoint-Präsentation

## Skripte

- **rebuild.ps1**: PowerShell-Skript zum Neuaufbau des Projekts
- **rebuild.sh**: Bash-Skript zum Neuaufbau des Projekts
- **rebuild2.ps1**: Alternatives PowerShell-Skript
- **rebuild2.sh**: Alternatives Bash-Skript

## Dynamische Aktualisierung

Um dieses Dokument zu aktualisieren, können folgende Befehle verwendet werden:

```bash
# Für eine vollständige Verzeichnisstruktur
find . -type d -not -path "*/\.*" | sort > directory_structure.txt

# Für eine Übersicht der Python-Dateien
find . -name "*.py" | sort > python_files.txt
```

Oder unter Windows:

```powershell
# Für eine vollständige Verzeichnisstruktur
Get-ChildItem -Directory -Recurse | Where-Object { $_.FullName -notmatch "\\\..*" } | Select-Object FullName | Sort-Object FullName | Out-File -FilePath directory_structure.txt

# Für eine Übersicht der Python-Dateien
Get-ChildItem -Recurse -Filter "*.py" | Select-Object FullName | Sort-Object FullName | Out-File -FilePath python_files.txt
```
