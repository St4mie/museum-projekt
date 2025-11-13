# Datenbankstruktur - ER-Diagramm (Mermaid)

Dieses Dokument stellt die Struktur der Datenbank des Museum-Projekts in Form eines Entity-Relationship-Diagramms dar, erstellt mit Mermaid.

## ER-Diagramm

```mermaid
erDiagram
    MovieORM ||--o{ SzeneORM : "hat"
    SzeneORM ||--o{ MediumORM : "hat"
    SzeneORM }o--o{ ExponatORM : "hat"
    SzeneORM ||--o| StellplatzORM : "hat"
    
    AusstellungORM ||--o{ RaumORM : "enthält"
    RaumORM ||--o{ RegalORM : "enthält"
    RegalORM ||--o{ FachORM : "enthält"
    FachORM ||--o{ StellplatzORM : "enthält"
    
    MovieORM {
        int id PK
        string titel
        string wiki_url
        int erscheinungsjahr
        string regisseur
        string autor
        string hauptdarsteller
        string poster_url
        string beschreibung
        boolean pruefung
        datetime erstellt_am
        datetime aktualisiert_am
    }
    
    SzeneORM {
        int id PK
        int film_id FK
        string name
        string beschreibung
        datetime erstellt_am
        datetime aktualisiert_am
    }
    
    MediumORM {
        int id PK
        int szene_id FK
        string dateipfad
        enum medientyp
        datetime erstellt_am
        datetime aktualisiert_am
    }
    
    ExponatORM {
        int id PK
        string name
        string beschreibung
        string hersteller
        int baujahr
        string material
        decimal wert
        int anzahl
        datetime erstellt_am
        datetime aktualisiert_am
    }
    
    AusstellungORM {
        int id PK
        string name
        string beschreibung
        datetime erstellt_am
        datetime aktualisiert_am
    }
    
    RaumORM {
        int id PK
        int ausstellung_id FK
        string name
        string beschreibung
        datetime erstellt_am
        datetime aktualisiert_am
    }
    
    RegalORM {
        int id PK
        int raum_id FK
        string bezeichnung
        string beschreibung
        datetime erstellt_am
        datetime aktualisiert_am
    }
    
    FachORM {
        int id PK
        int regal_id FK
        string bezeichnung
        string beschreibung
        datetime erstellt_am
        datetime aktualisiert_am
    }
    
    StellplatzORM {
        int id PK
        int fach_id FK
        int position
        int szene_id FK
        datetime erstellt_am
        datetime aktualisiert_am
    }
```

## Hinweise zur Darstellung

- Die Pfeile zeigen die Beziehungen zwischen den Entitäten an:
  - `||--o{` bedeutet eine 1:n-Beziehung (ein Objekt hat viele andere Objekte)
  - `}o--o{` bedeutet eine m:n-Beziehung (viele zu vielen)
  - `||--o|` bedeutet eine 1:1-Beziehung (ein Objekt hat genau ein anderes Objekt)

- PK = Primärschlüssel
- FK = Fremdschlüssel

## Verwendung

Dieses Diagramm kann in Markdown-Viewern angezeigt werden, die Mermaid unterstützen, wie z.B. GitHub, GitLab oder VS Code mit entsprechenden Erweiterungen.