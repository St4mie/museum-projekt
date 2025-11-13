# Museum-Projekt Präsentationsdateien

Dieses Verzeichnis enthält die Präsentationsdateien für das Museum-Projekt "Digitales Besucher-Informationssystem".

## Enthaltene Dateien

1. `Museum-Projekt_Präsentation.md` - Grundlegende Präsentationsfolien im Markdown-Format
2. `Museum-Projekt_Präsentation_mit_Notizen.md` - Präsentationsfolien mit Redenotizen im Markdown-Format

## Verwendung der Präsentationsdateien

### Option 1: Konvertierung zu PowerPoint

Sie können die Markdown-Dateien in PowerPoint-Präsentationen konvertieren:

1. **Mit Pandoc** (empfohlen):
   - Installieren Sie [Pandoc](https://pandoc.org/installing.html)
   - Führen Sie folgenden Befehl aus:
     ```
     pandoc -t pptx Museum-Projekt_Präsentation.md -o Museum-Projekt_Präsentation.pptx
     ```
   - Für die Version mit Redenotizen:
     ```
     pandoc -t pptx Museum-Projekt_Präsentation_mit_Notizen.md -o Museum-Projekt_Präsentation_mit_Notizen.pptx
     ```

2. **Manuell**:
   - Öffnen Sie PowerPoint
   - Erstellen Sie für jeden Abschnitt (getrennt durch `---`) eine neue Folie
   - Kopieren Sie den Inhalt jedes Abschnitts in die entsprechende Folie
   - Für die Version mit Redenotizen: Fügen Sie den Text unter "Redenotizen:" in die Notizensektion der jeweiligen Folie ein

### Option 2: Verwendung als Markdown-Präsentation

Sie können die Markdown-Dateien auch direkt als Präsentation verwenden:

1. **Mit VS Code**:
   - Installieren Sie die Erweiterung "Markdown Preview Enhanced"
   - Öffnen Sie die Markdown-Datei
   - Drücken Sie `Ctrl+K V` für eine Vorschau
   - Klicken Sie auf das Präsentationssymbol in der Vorschau

2. **Mit Marp**:
   - Installieren Sie [Marp CLI](https://github.com/marp-team/marp-cli)
   - Konvertieren Sie die Datei:
     ```
     marp Museum-Projekt_Präsentation.md --pdf
     ```

3. **Mit Reveal.js**:
   - Installieren Sie [reveal-md](https://github.com/webpro/reveal-md)
   - Starten Sie die Präsentation:
     ```
     reveal-md Museum-Projekt_Präsentation.md
     ```

## Anpassung der Präsentation

- **Bilder**: Ersetzen Sie den Platzhalter `https://via.placeholder.com/800x400?text=Systemarchitektur` durch einen tatsächlichen Link zu einem Bild oder einer lokalen Bilddatei.
- **Design**: Nach der Konvertierung zu PowerPoint können Sie ein Design-Template anwenden und die Formatierung anpassen.
- **Redenotizen**: Die Redenotizen können nach Bedarf erweitert oder angepasst werden.

## Präsentationsdauer

Die Präsentation ist für eine Dauer von etwa 15 Minuten konzipiert, mit zusätzlicher Zeit für Fragen am Ende.