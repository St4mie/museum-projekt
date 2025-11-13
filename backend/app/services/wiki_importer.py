# backend/app/services/wiki_importer.py

import wikipedia
import wptools
from typing import Dict

from app.config import settings

class WikiImporter:
    """
    Importiert Metadaten für Filme aus Wikipedia/Wikidata.
    Sprache und Basis-URL kommen aus den Pydantic-Settings.
    """

    @staticmethod
    def fetch(title: str) -> Dict[str, str]:
        """
        Holt Felddaten für den gegebenen Filmtitel:
        - title: Film-Titel (z. B. "Inception")
        - nutzt settings.wikipedia_language und settings.wikipedia_api_url
        Gibt ein Dict mit Keys:
          - regisseur
          - autor
          - hauptdarsteller
          - poster_url
          - beschreibung

        Raises:
            ValueError: Wenn der Titel leer ist
            wikipedia.exceptions.PageError: Wenn die Seite nicht existiert
            wikipedia.exceptions.DisambiguationError: Wenn der Titel mehrdeutig ist
            ConnectionError: Bei Netzwerkproblemen
            Exception: Bei anderen Fehlern
        """
        if not title or not title.strip():
            raise ValueError("Film-Titel darf nicht leer sein")

        try:
            # 1) Sprache für Wikipedia aus Settings setzen
            wikipedia.set_lang(settings.wikipedia_language)
            # 2) (Optional) spezifische API-URL setzen, falls unterstützt
            if hasattr(wikipedia, 'set_api_url'):
                try:
                    wikipedia.set_api_url(settings.wikipedia_api_url)
                except Exception as e:
                    # Fehler beim Setzen der API-URL abfangen
                    print(f"Warnung: Konnte Wikipedia API-URL nicht setzen: {e}")
            else:
                # älteres wikipedia-Paket kennt set_api_url nicht
                pass

            # 3) Kurzzusammenfassung über die Wikipedia-Bibliothek
            try:
                summary = wikipedia.page(title).summary
            except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError) as e:
                # Spezifische Wikipedia-Fehler weiterleiten
                raise e
            except Exception as e:
                # Andere Fehler in ConnectionError umwandeln
                raise ConnectionError(f"Fehler beim Abrufen der Wikipedia-Seite: {str(e)}")

            # 4) Infobox-Daten über wptools parsen
            try:
                page = wptools.page(title, lang=settings.wikipedia_language).get_parse()
                infobox = page.data.get("infobox", {})
            except Exception as e:
                # Fehler beim Parsen der Infobox
                raise ConnectionError(f"Fehler beim Parsen der Infobox-Daten: {str(e)}")

            # 5) Relevante Felder herausziehen
            director   = infobox.get("Regie")     or infobox.get("regie")     or infobox.get("director")
            author     = infobox.get("Drehbuch")  or infobox.get("drehbuch")  or infobox.get("writer")
            main_cast  = infobox.get("Besetzung") or infobox.get("besetzung") or infobox.get("starring")
            poster_url = infobox.get("Bild")      or infobox.get("bild")      or infobox.get("image")    or infobox.get("poster")

            return {
                "beschreibung":    summary,
                "regisseur":       director,
                "autor":           author,
                "hauptdarsteller": main_cast,
                "poster_url":      poster_url,
            }
        except (ValueError, wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError, ConnectionError) as e:
            # Diese spezifischen Fehler weiterleiten
            raise e
        except Exception as e:
            # Alle anderen Fehler in einen allgemeinen Fehler umwandeln
            raise Exception(f"Unerwarteter Fehler beim Wiki-Import: {str(e)}")
