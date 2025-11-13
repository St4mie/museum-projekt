# Dokumentation der Datenbankstruktur

Dieses Verzeichnis enthält Dokumentation zur Datenbankstruktur des Museum-Projekts.

## ER-Diagramme

Die folgenden ER-Diagramme stellen die Struktur der Datenbank grafisch dar:

1. [Textbasiertes ER-Diagramm](database_er_diagram.md) - Eine ASCII-Art-Darstellung der Datenbankstruktur, die in jedem Texteditor lesbar ist.

2. [Mermaid ER-Diagramm](database_er_diagram_mermaid.md) - Eine Darstellung der Datenbankstruktur mit Mermaid-Syntax, die in Markdown-Viewern wie GitHub, GitLab oder VS Code mit entsprechenden Erweiterungen als grafisches Diagramm gerendert werden kann.

## Verwendung

Die ER-Diagramme dienen als Referenz für Entwickler, um die Struktur der Datenbank und die Beziehungen zwischen den verschiedenen Tabellen zu verstehen. Sie sind besonders nützlich für:

- Neue Teammitglieder, die sich mit der Datenbankstruktur vertraut machen müssen
- Entwickler, die neue Features implementieren und verstehen müssen, wie die Daten organisiert sind
- Dokumentationszwecke und Architekturüberblick

## Aktualisierung

Wenn sich die Datenbankstruktur ändert, sollten diese Diagramme entsprechend aktualisiert werden, um die aktuelle Struktur korrekt widerzuspiegeln.

## Modelle

Die Hauptmodelle der Datenbank sind:

- **MovieORM**: Filme
- **SzeneORM**: Szenen aus Filmen
- **MediumORM**: Medien (Audio/Video) zu Szenen
- **ExponatORM**: Ausstellungsstücke
- **AusstellungORM**: Ausstellungen
- **RaumORM**: Räume in Ausstellungen
- **RegalORM**: Regale in Räumen
- **FachORM**: Fächer in Regalen
- **StellplatzORM**: Stellplätze in Fächern

Detaillierte Informationen zu jedem Modell und ihren Beziehungen finden Sie in den ER-Diagrammen.