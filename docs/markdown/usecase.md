# Museum-Projekt: Anwendungsfälle (Use Cases)

```
+------------------+                +------------------+                +------------------+
|                  |                |                  |                |                  |
|   Entwickler     |                |     Museum       |                |     Service      |
|                  |                |                  |                |                  |
+------------------+                +------------------+                +------------------+
        |                                   |                                   |
        | Volle Rechte                      | Content-Management                | Import & API
        | für Migrationen                   | (CRUD)                            | Funktionen
        |                                   |                                   |
        v                                   v                                   v
+------------------+                +------------------+                +------------------+
|                  |                |                  |                |                  |
| - Datenbank-     |                | - Filme          |                | - Daten          |
|   Migrationen    |                |   verwalten      |                |   importieren    |
| - Schema-        |                | - Ausstellungen  |                | - API-Endpunkte  |
|   Änderungen     |                |   verwalten      |                |   bereitstellen  |
| - Entwicklung    |                | - Medien         |                | - Tabellen       |
|                  |                |   verwalten      |                |   anlegen/ändern |
+------------------+                +------------------+                +------------------+
```

## 1. Einführung

Das Museum-Projekt ist ein Verwaltungssystem für ein Filmmuseum, das die Organisation von Filmen, Szenen, Exponaten und Ausstellungen ermöglicht. Die Anwendung unterstützt die Verwaltung von Medieninhalten (Audio/Video), die Katalogisierung von Exponaten und die räumliche Organisation von Ausstellungen.

## 2. Benutzerrollen und Berechtigungen

### 2.1 Entwickler
- **Berechtigungen**: Volle Rechte für Migrationen und Datenbankänderungen
- **Hauptaufgaben**: Datenbankmigrationen, Schemaänderungen, Entwicklung neuer Funktionen

### 2.2 Museum (Content-Manager)
- **Berechtigungen**: CRUD-Operationen (Create, Read, Update, Delete) für alle Inhalte
- **Hauptaufgaben**: Verwaltung von Filmen, Szenen, Exponaten, Ausstellungen und Medien

### 2.3 Service (Import und API)
- **Berechtigungen**: Lese- und Schreibzugriff, Tabellen anlegen/ändern
- **Hauptaufgaben**: Datenimport (z.B. aus Wikipedia), Bereitstellung von API-Endpunkten

### 2.4 System (Monitoring)
- **Berechtigungen**: Nur Lesezugriff
- **Hauptaufgaben**: Überwachung und Monitoring des Systems

### 2.5 Benutzer (Öffentlich)
- **Berechtigungen**: Nur Lesezugriff
- **Hauptaufgaben**: Anzeigen von Informationen zu Filmen, Szenen und Ausstellungen

## 3. Hauptanwendungsfälle

### 3.1 Filmverwaltung

```
+------------------+                +------------------+                +------------------+
|                  |                |                  |                |                  |
|     Benutzer     |                |     Museum       |                |     Service      |
|                  |                |                  |                |                  |
+------------------+                +------------------+                +------------------+
        |                                   |                                   |
        | Filme anzeigen                    | Filme verwalten                   | Metadaten importieren
        |                                   |                                   |
        v                                   v                                   v
+------------------+                +------------------+                +------------------+
|                  |                |                  |                |                  |
| - Filmliste      |                | - Filme          |                | - Wikipedia-     |
|   ansehen        |                |   hinzufügen     |                |   Import         |
| - Filmdetails    |                | - Filme          |                | - Metadaten      |
|   ansehen        |                |   bearbeiten     |                |   aktualisieren  |
|                  |                | - Filme          |                |                  |
|                  |                |   löschen        |                |                  |
+------------------+                +------------------+                +------------------+
```

#### 3.1.1 Filme anzeigen (Benutzer)
- Filmliste mit Paginierung ansehen
- Filmdetails ansehen (Titel, Jahr, Regisseur, Beschreibung, etc.)

#### 3.1.2 Filme verwalten (Museum)
- Neue Filme hinzufügen
- Filmdetails bearbeiten
- Filme löschen

#### 3.1.3 Metadaten importieren (Service)
- Metadaten aus Wikipedia/Wikidata importieren
- Filminformationen aktualisieren

### 3.2 Szenenverwaltung

```
+------------------+                +------------------+
|                  |                |                  |
|     Benutzer     |                |     Museum       |
|                  |                |                  |
+------------------+                +------------------+
        |                                   |
        | Szenen anzeigen                   | Szenen verwalten
        |                                   |
        v                                   v
+------------------+                +------------------+
|                  |                |                  |
| - Szenen eines   |                | - Szenen         |
|   Films ansehen  |                |   hinzufügen     |
| - Szenendetails  |                | - Szenen         |
|   ansehen        |                |   bearbeiten     |
|                  |                | - Szenen         |
|                  |                |   löschen        |
+------------------+                +------------------+
```

#### 3.2.1 Szenen anzeigen (Benutzer)
- Szenen eines Films ansehen
- Szenendetails ansehen (Name, Beschreibung, zugehörige Medien und Exponate)

#### 3.2.2 Szenen verwalten (Museum)
- Neue Szenen zu einem Film hinzufügen
- Szenendetails bearbeiten
- Szenen löschen
- Szenen mit Exponaten verknüpfen

### 3.3 Medienverwaltung

```
+------------------+                +------------------+
|                  |                |                  |
|     Benutzer     |                |     Museum       |
|                  |                |                  |
+------------------+                +------------------+
        |                                   |
        | Medien anzeigen                   | Medien verwalten
        |                                   |
        v                                   v
+------------------+                +------------------+
|                  |                |                  |
| - Bilder         |                | - Medien         |
|   ansehen        |                |   hochladen      |
| - Videos         |                | - Medien         |
|   ansehen        |                |   verarbeiten    |
| - Audio          |                | - Medien         |
|   anhören        |                |   löschen        |
+------------------+                +------------------+
```

#### 3.3.1 Medien anzeigen (Benutzer)
- Bilder zu Filmen ansehen
- Videos zu Filmen ansehen
- Audio zu Filmen anhören
- Medien zu Szenen ansehen

#### 3.3.2 Medien verwalten (Museum)
- Bilder, Videos und Audio hochladen
- Medien verarbeiten (Thumbnails generieren, Videos transcodieren)
- Medien zu Szenen zuordnen
- Medien löschen

### 3.4 Exponatverwaltung

```
+------------------+                +------------------+
|                  |                |                  |
|     Benutzer     |                |     Museum       |
|                  |                |                  |
+------------------+                +------------------+
        |                                   |
        | Exponate anzeigen                 | Exponate verwalten
        |                                   |
        v                                   v
+------------------+                +------------------+
|                  |                |                  |
| - Exponatliste   |                | - Exponate       |
|   ansehen        |                |   hinzufügen     |
| - Exponatdetails |                | - Exponate       |
|   ansehen        |                |   bearbeiten     |
|                  |                | - Exponate       |
|                  |                |   löschen        |
+------------------+                +------------------+
```

#### 3.4.1 Exponate anzeigen (Benutzer)
- Exponatliste ansehen
- Exponatdetails ansehen (Name, Beschreibung, Hersteller, Baujahr, Material, Wert)
- Zugehörige Szenen zu einem Exponat ansehen

#### 3.4.2 Exponate verwalten (Museum)
- Neue Exponate hinzufügen
- Exponatdetails bearbeiten
- Exponate löschen
- Exponate mit Szenen verknüpfen

### 3.5 Ausstellungsverwaltung

```
+------------------+                +------------------+
|                  |                |                  |
|     Benutzer     |                |     Museum       |
|                  |                |                  |
+------------------+                +------------------+
        |                                   |
        | Ausstellungen anzeigen            | Ausstellungen verwalten
        |                                   |
        v                                   v
+------------------+                +------------------+
|                  |                |                  |
| - Ausstellungen  |                | - Ausstellungen  |
|   ansehen        |                |   erstellen      |
| - Räume          |                | - Räume          |
|   ansehen        |                |   hinzufügen     |
| - Regale         |                | - Regale         |
|   ansehen        |                |   einrichten     |
|                  |                | - Stellplätze    |
|                  |                |   zuweisen       |
+------------------+                +------------------+
```

#### 3.5.1 Ausstellungen anzeigen (Benutzer)
- Ausstellungsliste ansehen
- Ausstellungsdetails ansehen
- Räume, Regale und Fächer einer Ausstellung ansehen
- Szenen an Stellplätzen ansehen

#### 3.5.2 Ausstellungen verwalten (Museum)
- Neue Ausstellungen erstellen
- Räume zu Ausstellungen hinzufügen
- Regale in Räumen einrichten
- Fächer in Regalen anlegen
- Stellplätze in Fächern definieren
- Szenen Stellplätzen zuweisen

## 4. Workflow-Beispiele

### 4.1 Film- und Szenenverwaltung

```
+-------------------+     +-------------------+     +-------------------+
| Film hinzufügen   | --> | Metadaten         | --> | Szenen            |
| oder importieren  |     | importieren       |     | hinzufügen        |
+-------------------+     +-------------------+     +-------------------+
                                                            |
                                                            v
+-------------------+     +-------------------+     +-------------------+
| Exponate mit      | <-- | Medien zu         | <-- | Medien            |
| Szenen verknüpfen |     | Szenen zuordnen   |     | hochladen         |
+-------------------+     +-------------------+     +-------------------+
```

### 4.2 Ausstellungsorganisation

```
+-------------------+     +-------------------+     +-------------------+
| Ausstellung       | --> | Räume             | --> | Regale            |
| erstellen         |     | hinzufügen        |     | einrichten        |
+-------------------+     +-------------------+     +-------------------+
         |
         |                +-------------------+     +-------------------+
         +--------------> | Fächer            | --> | Stellplätze       |
                          | anlegen           |     | definieren        |
                          +-------------------+     +-------------------+
                                                            |
                                                            v
                                                    +-------------------+
                                                    | Szenen            |
                                                    | zuweisen          |
                                                    +-------------------+
```

## 5. Zusammenfassung

Das Museum-Projekt bietet eine umfassende Lösung für die Verwaltung eines Filmmuseums mit verschiedenen Benutzerrollen und Anwendungsfällen. Die Hauptfunktionen umfassen:

1. Verwaltung von Filmen und deren Metadaten
2. Organisation von Szenen und zugehörigen Medien
3. Katalogisierung von Exponaten
4. Strukturierung von Ausstellungen mit Räumen, Regalen und Stellplätzen
5. Zuordnung von Szenen zu physischen Stellplätzen

Die verschiedenen Benutzerrollen (Entwickler, Museum, Service, System, Benutzer) haben unterschiedliche Berechtigungen und Aufgaben, die auf ihre spezifischen Bedürfnisse zugeschnitten sind.