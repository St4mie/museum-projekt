# backend/app/services/wiki_importer.py

"""
Service, der Missing-Fields aus Wikipedia/Wikidata zieht.
"""

try:
    import wikipedia
    import wptools
except ImportError as e:
    raise RuntimeError(f"Fehlende Abhängigkeit: {e.name}")

class WikiImporter:
    """
    Liest Summary und Infobox-Daten via wikipedia & wptools aus.
    """

    @staticmethod
    def fetch(title: str) -> dict:
        """
        Sucht den Wikipedia-Artikel zum `title`,
        liest Summary und Infobox-Felder (Regisseur, Autor, Cast, Bild)
        und liefert ein Dict, das zu unseren ORM-Feldern passt.
        """
        wikipedia.set_lang("de")
        page = wikipedia.page(title)
        summary = page.summary or None

        wp = wptools.page(title, silent=True)
        wp.get_parse()
        infobox = wp.data.get("infobox", {})

        result = {"description": summary}

        if "director" in infobox:
            result["director"] = infobox["director"]
        if "writer" in infobox:
            result["author"] = infobox["writer"]
        if "starring" in infobox:
            result["main_cast"] = infobox["starring"]
        # wptools liefert thumb-URL in .image_thumb
        poster = getattr(wp, "image_thumb", None)
        if poster:
            result["poster_url"] = poster

        return result
