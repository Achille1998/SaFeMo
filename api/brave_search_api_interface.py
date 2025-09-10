import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

# Carica le variabili d'ambiente da un file .env
load_dotenv()
api_key = os.getenv("BRAVE_SEARCH_API_KEY")
if not api_key:
    raise ValueError("La variabile d'ambiente BRAVE_SEARCH_API_KEY non è stata trovata.")


def cerca_instagram(nome: str, indirizzo: str):
    """
    Cerca su Instagram usando la Brave Search API, filtrando per URL che
    corrispondono a un profilo utente O a una pagina di una location.
    """
    query = f"site:instagram.com {nome} {indirizzo}"
    endpoint = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    params = {
        "q": query,
        "count": 10
    }

    try:
        r = requests.get(endpoint, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()

        for item in data.get("web", {}).get("results", []):
            url = item.get("url", "")
            if not url:
                continue

            parsed_url = urlparse(url)

            if "instagram.com" not in parsed_url.netloc:
                continue

            path_segments = [segment for segment in parsed_url.path.split('/') if segment]

            # --- NUOVA LOGICA DI FILTRAGGIO ---

            # CONDIZIONE 1: L'URL è un profilo utente?
            # es: /nomeutente/ -> path_segments: ['nomeutente']
            is_user_profile = (len(path_segments) == 1 and
                               path_segments[0] not in ["explore", "accounts", "reels", "p"])

            # CONDIZIONE 2: L'URL è una pagina di una location?
            # es: /explore/locations/123/nome-luogo/ -> path_segments: ['explore', 'locations', ...]
            is_location_page = (len(path_segments) >= 2 and
                                path_segments[0] == 'explore' and
                                path_segments[1] == 'locations')

            # Se una delle due condizioni è vera, abbiamo trovato un risultato valido
            if is_user_profile or is_location_page:
                return url

    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta API: {e}")
        return None

    return None


if __name__ == "__main__":
    profilo = cerca_instagram(nome := "re di fiandra", indirizzo := "montecchia di crosara")
    print(f"Profilo trovato per nome {nome} e indirizzo {indirizzo}:", profilo or "Nessun profilo trovato")
