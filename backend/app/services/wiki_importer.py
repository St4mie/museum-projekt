"""
Service zum Nachladen fehlender Filminfos von Wikipedia/Wikidata.
"""
try:
    import wikipedia
    import wptools
except ImportError as e:
    raise RuntimeError(f"Fehlende Abhängigkeit: {e.name}")

class WikiImporter:
    """
    Statische Helferklasse, die per wikipedia + wptools
    Zusammenfassung und Infobox-Felder holt.
    """
    @staticmethod
    def fetch(title: str) -> dict:
        """
        Lädt die Seite zum `title` (z.B. "Blade Runner")
        und extrahiert:
          - description, director, author, main_cast, poster_url
        """
        wikipedia.set_lang("de")
        page = wikipedia.page(title)
        summary = page.summary or None

        wp = wptools.page(title, silent=True)
        wp.get_parse()
        infobox = wp.data.get("infobox", {})

        result: dict[str, str | None] = {
            "description": summary,
            "director": None,
            "author": None,
            "main_cast": None,
            "poster_url": None
        }

        if "director" in infobox:
            result["director"] = infobox["director"]
        if "writer" in infobox:
            result["author"] = infobox["writer"]
        if "starring" in infobox:
            result["main_cast"] = infobox["starring"]

        # wptools stellt das Vorschaubild als Attribut image_thumb zur Verfügung
        poster = getattr(wp, "image_thumb", None)
        if poster:
            result["poster_url"] = poster

        return result
