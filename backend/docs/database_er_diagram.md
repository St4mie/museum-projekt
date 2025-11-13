# Datenbankstruktur - ER-Diagramm

Dieses Dokument stellt die Struktur der Datenbank des Museum-Projekts in Form eines Entity-Relationship-Diagramms dar.

## ER-Diagramm (Textbasiert)

```
+---------------+       +---------------+       +---------------+
|    MovieORM   |       |   SzeneORM    |       |   MediumORM   |
+---------------+       +---------------+       +---------------+
| id (PK)       |       | id (PK)       |       | id (PK)       |
| titel         |<----->| film_id (FK)  |<----->| szene_id (FK) |
| wiki_url      |  1:n  | name          |  1:n  | dateipfad     |
| erscheinungsjahr      | beschreibung  |       | medientyp     |
| regisseur     |       | erstellt_am   |       | erstellt_am   |
| autor         |       | aktualisiert_am       | aktualisiert_am
| hauptdarsteller       +---------------+       +---------------+
| poster_url    |             |
| beschreibung  |             |
| pruefung      |             |
| erstellt_am   |             |
| aktualisiert_am            |
+---------------+             |
                              |
                              v
+---------------+       +---------------+
|  ExponatORM   |       | szene_exponat |
+---------------+       +---------------+
| id (PK)       |<----->| szene_id (PK) |
| name          |  m:n  | exponat_id (PK)
| beschreibung  |       +---------------+
| hersteller    |
| baujahr       |
| material      |
| wert          |
| anzahl        |
| erstellt_am   |
| aktualisiert_am
+---------------+

+---------------+       +---------------+       +---------------+
| AusstellungORM|       |    RaumORM    |       |   RegalORM    |
+---------------+       +---------------+       +---------------+
| id (PK)       |       | id (PK)       |       | id (PK)       |
| name          |<----->| ausstellung_id|<----->| raum_id (FK)  |
| beschreibung  |  1:n  | name          |  1:n  | bezeichnung   |
| erstellt_am   |       | beschreibung  |       | beschreibung  |
| aktualisiert_am       | erstellt_am   |       | erstellt_am   |
+---------------+       | aktualisiert_am       | aktualisiert_am
                        +---------------+       +---------------+
                                                       |
                                                       |
                                                       v
+---------------+       +---------------+       +---------------+
|  StellplatzORM|       |    FachORM    |       |               |
+---------------+       +---------------+       |               |
| id (PK)       |       | id (PK)       |       |               |
| fach_id (FK)  |<------| regal_id (FK) |       |               |
| position      |  1:n  | bezeichnung   |       |               |
| szene_id (FK) |       | beschreibung  |       |               |
| erstellt_am   |       | erstellt_am   |       |               |
| aktualisiert_am       | aktualisiert_am       |               |
+---------------+       +---------------+       +---------------+
        |
        |
        v
+---------------+
|   SzeneORM    |
+---------------+
```

## Tabellenbeschreibungen

### MovieORM (movie)
- Repräsentiert einen Film im Museum
- Primärschlüssel: id
- Unique Constraint: (titel, erscheinungsjahr)
- Beziehungen:
  - 1:n zu SzeneORM (szenen)

### SzeneORM (szene)
- Repräsentiert eine Szene aus einem Film
- Primärschlüssel: id
- Unique Constraint: (film_id, name)
- Beziehungen:
  - n:1 zu MovieORM (film)
  - 1:n zu MediumORM (medien)
  - m:n zu ExponatORM (exponate)
  - 1:1 zu StellplatzORM (stellplatz)

### MediumORM (medium)
- Repräsentiert Audio- oder Videodateien zu einer Szene
- Primärschlüssel: id
- Beziehungen:
  - n:1 zu SzeneORM (szene)

### ExponatORM (exponat)
- Repräsentiert ein Ausstellungsstück im Museum
- Primärschlüssel: id
- Unique Constraint: (name)
- Beziehungen:
  - m:n zu SzeneORM (szenen)

### AusstellungORM (ausstellung)
- Repräsentiert eine Ausstellung im Museum
- Primärschlüssel: id
- Unique Constraint: (name)
- Beziehungen:
  - 1:n zu RaumORM (raeume)

### RaumORM (raum)
- Repräsentiert einen Raum in einer Ausstellung
- Primärschlüssel: id
- Unique Constraint: (ausstellung_id, name)
- Beziehungen:
  - n:1 zu AusstellungORM (ausstellung)
  - 1:n zu RegalORM (regale)

### RegalORM (regal)
- Repräsentiert ein Regal in einem Raum
- Primärschlüssel: id
- Unique Constraint: (raum_id, bezeichnung)
- Beziehungen:
  - n:1 zu RaumORM (raum)
  - 1:n zu FachORM (faecher)

### FachORM (fach)
- Repräsentiert ein Fach in einem Regal
- Primärschlüssel: id
- Unique Constraint: (regal_id, bezeichnung)
- Beziehungen:
  - n:1 zu RegalORM (regal)
  - 1:n zu StellplatzORM (stellplaetze)

### StellplatzORM (stellplatz)
- Repräsentiert einen Stellplatz in einem Fach
- Primärschlüssel: id
- Unique Constraint: (fach_id, position)
- Beziehungen:
  - n:1 zu FachORM (fach)
  - 1:1 zu SzeneORM (szene)

### szene_exponat (Junction Table)
- Verbindungstabelle für die m:n-Beziehung zwischen SzeneORM und ExponatORM
- Zusammengesetzter Primärschlüssel: (szene_id, exponat_id)