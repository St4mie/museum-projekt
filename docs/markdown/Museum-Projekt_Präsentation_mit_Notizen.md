# Museum-Projekt: Digitales Besucher-Informationssystem

## Abschlusspräsentation | Michel Stange, dSign-Systems GmbH | Sommer 2025

### Redenotizen:
Herzlich willkommen zu meiner Abschlusspräsentation. Mein Name ist Michel Stange, Auszubildender bei dSign-Systems GmbH. Thema: Entwicklung eines digitalen Informationssystems für das Museum Schmalkalden.

---

## Agenda

- Vorstellung dSign-Systems
- Zeitplanung
- Ist-Analyse
- Soll-Konzept
- Projektkosten
- Umsetzung/Architektur
- Wichtige Codebestandteile
- Soll-Ist-Vergleich
- Übergabe/Abnahme
- Fazit & Ausblick

### Redenotizen:
Sie erhalten einen Überblick von der Analyse bis zur Umsetzung und zu den Lessons Learned.

---

## Unternehmensvorstellung dSign-Systems

- **Sitz**: Schmalkalden
- **Tätigkeitsfeld**: IT-Systemhaus, Digitalisierungslösungen, Softwareentwicklung
- **Schwerpunkt**: Projekte in Museums-/Ausstellungsumfeld
- **Expertise**: Individuelle IT-Lösungen für digitale Museumsbegleitung

### Redenotizen:
dSign-Systems bietet individuelle IT-Lösungen, unter anderem für Museen, um Ausstellungen digital zu begleiten.

---

## Projektüberblick & Zeitplanung

| Phase | Aufgaben | Zeit |
|-------|----------|------|
| Ist-Analyse | Bedarf, Termin vor Ort | 10h |
| Entwurf | Architektur, Datenmodell | 16h |
| Implementierung | Entwicklung, Testing | 30h |
| Deployment | Setup, Healthcheck, Test | 14h |
| Dokumentation | Anleitung, Doku, Review | 10h |
| **Gesamt** | | **80h** |

### Redenotizen:
Die Planung umfasste fünf Phasen mit Fokus auf einen stabilen Prototypen für das Backend.

---

## Ist-Analyse

- Keine digitale Infrastruktur vorhanden
- Informationen nur per Beschilderung
- Kein interaktives Nutzererlebnis
- Bedarf: 
  - Flexiblere Besucherinformation
  - Geringerer Personalaufwand
  - Modernisierung des Museumserlebnisses

### Redenotizen:
Der Startpunkt: alles analog, keine Software, keine Hardware vorinstalliert.

---

## Soll-Konzept

- Modulares, lokal betriebenes Backend
- Verwaltung von Medien, Exponaten, Ausstellungen (MariaDB)
- REST-API mit FastAPI, Frontend/CMS nachrüstbar
- Automatisierte Medienverarbeitung (Thumbnails, Transcoding)
- Wartungsarm, Open-Source, Docker-basiert

### Redenotizen:
Das System sollte flexibel, wartungsarm und offline-fähig werden. Die Schnittstellen sind offen für Erweiterungen.

---

## Projektkosten

- **Gesamtkosten**: ca. 4.200 €
  - Hardware: 240 €
  - Personal: 3.960 €
  - Software: Open Source (keine Lizenzkosten)
- **Wirtschaftlichkeit**: 
  - Einsparung Personalkosten
  - Wiederverwendbarkeit der Lösung
  - Keine laufenden Lizenzkosten

### Redenotizen:
Eigenentwicklung spart Lizenzkosten, langfristige Einsparungen durch weniger Personalbedarf.

---

## Umsetzung & Systemarchitektur

- **Backend**: FastAPI, Python, SQLAlchemy, Pydantic, MariaDB
- **Containerisierung**: Docker Compose (Backend, DB, Test)
- **Architektur**: REST-API, BackgroundTasks für Medienverarbeitung
- **Teststrategie**: Pytest, Testdatenbank, CI-artige Checks

![Systemarchitektur](https://via.placeholder.com/800x400?text=Systemarchitektur)

### Redenotizen:
Die Containerstruktur sorgt für konsistente Entwicklung und einfachen Rollout.

---

## Codebeispiel – Datenmodell Film

```python
class MovieORM(Base):
    __tablename__ = "movie"
    __table_args__ = (UniqueConstraint("titel", "erscheinungsjahr"),)
    
    id = Column(Integer, primary_key=True, index=True)
    titel = Column(String, nullable=False, index=True)
    wiki_url = Column(String, nullable=True)
    erscheinungsjahr = Column(Integer, nullable=False)
    regisseur = Column(String, nullable=True)
    # ...
```

### Redenotizen:
Zentrale Datenstruktur: Filme, mit Validierung und Integrität für eindeutige Titel + Jahr.

---

## Codebeispiel – Medienverarbeitung

```python
def transcode_video(movie_id: int, filename: str, resolution="720p") -> Path:
    """
    Transkodiert ein Video mit ffmpeg:
    1. Quelle: BASE/videos/movies/{movie_id}/{filename}
    2. Ziel: BASE/videos/movies/{movie_id}/{resolution}/{filename}
    """
    # ffmpeg-Aufruf, Fallback auf Original
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        logger.warning(f"Transkodierung fehlgeschlagen, kopiere Original als Fallback")
        shutil.copy2(src, dest)
    return dest
```

### Redenotizen:
Hintergrundprozesse wie Transcoding und Thumbnail-Erstellung laufen nach Uploads automatisch.

---

## Soll-Ist-Vergleich

- **Erreicht**: 
  - Stabiles, lokales Backend
  - REST-API
  - Automatisierte Medienverarbeitung
  - Datenbankmodell für Filme und Medien

- **Abweichung**: 
  - Frontend nicht umgesetzt
  - Einige Komfortfunktionen verschoben

- **Fazit**: Logik, Datenmodell und Schnittstellen-Ziele erfüllt

### Redenotizen:
Die Hauptfunktionen sind produktiv. Komfortfeatures und Frontend folgen in der nächsten Entwicklungsphase.

---

## Übergabe/Abnahme

- Dokumentation vollständig
  - Benutzerhandbuch
  - Entwicklerdokumentation
  - API-Dokumentation
- Abgabe von Code, Docker, Datenbank und Doku
- Abnahme durch Fachbetreuer

### Redenotizen:
Alle Komponenten und die Doku sind übergeben und von den Betreuern abgenommen.

---

## Fazit & Lessons Learned

- **Stärken**:
  - Wartbare, lokal lauffähige Backend-Lösung geschaffen
  - Dokumentation und Trennung der Komponenten gelungen
  - Automatisierte Tests implementiert

- **Lessons Learned**: 
  - Zeitmanagement
  - Testplanung
  - Schnittstellendefinition

### Redenotizen:
Stärken: Architektur und Wartbarkeit. Lernfelder: Zeitplanung und noch mehr Tests im Vorfeld.

---

## Ausblick

- **Geplante Erweiterungen**: 
  - Frontend
  - CMS
  - GPIO-Trigger für interaktive Exponate
- **Wiederverwendbarkeit** in weiteren Museen
- **Skalierbarkeit** für größere Ausstellungen

### Redenotizen:
Das System ist offen für spätere Frontends und kann leicht auf andere Museen übertragen werden.

---

## Abschluss & Fragen

# Vielen Dank für Ihre Aufmerksamkeit!

**Kontakt**:  
Michel Stange  
dSign-Systems GmbH  
michel.stange@dsign-systems.de

### Redenotizen:
Ich freue mich auf Ihre Fragen und das anschließende Fachgespräch.