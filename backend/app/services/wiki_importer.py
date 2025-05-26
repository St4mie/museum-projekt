# backend/app/services/wiki_importer.py

import wikipedia
import wptools
from typing import Dict


class WikiImporter:
    """
    Importiert Metadaten für Filme aus Wikipedia/Wikidata.
    Nutzt deutsche Wikipedia (de.wikipedia.org) für Summary und Infobox.
    """

    @staticmethod
    def fetch(title: str) -> Dict[str, str]:
        """
        Holt die Felddaten für den gegebenen Filmtitel.
        - title: Film-Titel (z. B. "Inception")
        - nutzt deutsche Wikipedia
        Gibt ein Dict mit Keys:
          - director
          - author
          - main_cast
          - poster_url
          - description
        """
        # DEUTSCHE WIKIPEDIA erzwingen
        wikipedia.set_lang("de")

        # 1. Kurzzusammenfassung aus deutscher WP
        summary = wikipedia.page(title).summary

        # 2. Infobox-Daten aus deutscher WP parsen
        page = wptools.page(title, lang="de").get_parse()
        infobox = page.data.get("infobox", {})

        # Felder extrahieren (je nach Infobox-Schlüssel)
        director = infobox.get("Regie") or infobox.get("regie") or infobox.get("director")
        author = infobox.get("Drehbuch") or infobox.get("drehbuch") or infobox.get("writer")
        main_cast = infobox.get("Besetzung") or infobox.get("besetzung") or infobox.get("starring")
        poster_url = infobox.get("Bild") or infobox.get("bild") or infobox.get("image") or infobox.get("poster")

        return {
            "description": summary,
            "director": director,
            "author": author,
            "main_cast": main_cast,
            "poster_url": poster_url,
        }
