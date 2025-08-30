from typing import List

import googlemaps
import time
import os

from db.models import Place

# --- PARAMETRI DI RICERCA (MODIFICA QUESTI VALORI) ---
# Inserisci qui la tua chiave API di Google Cloud
API_KEY = os.getenv('GOOGLE_API_KEY')

# Coordinate del centro della tua ricerca (es. Duomo di Milano)
LATITUDE = 45.4918144
LONGITUDE = 11.2492544
# Raggio della ricerca in metri (massimo 50000)
RADIUS = 2  # 2 km


class GoogleApi:
    def __init__(self):
        try:
            self.gmaps = googlemaps.Client(key=API_KEY)
        except Exception as e:
            print(f"❌ Errore nell'inizializzazione del client: {e}")
            exit()

    def find_bars(self, latitude=LATITUDE, longitude=LONGITUDE, radius=RADIUS):
        return self.find_places("bar", latitude, longitude, radius)

    def find_villages(self, latitude=LATITUDE, longitude=LONGITUDE, radius=RADIUS):
        villages = self.find_places("locality", latitude, longitude, radius)
        return [v.name for v in villages]

    def find_places(self, place_type, latitude, longitude, radius) -> List[Place]:
        print(f"🛰️  Sto cercando i {place_type} entro {radius} km da ({latitude}, {longitude})...")
        # Esegui la ricerca "Nearby Search"
        try:
            # La prima chiamata ottiene i primi 20 risultati
            places_result = self.gmaps.places_nearby(
                location=(latitude, longitude),
                radius=radius*1000,  # Converti km in metri
                type=place_type,
            )
        except Exception as e:
            print(f"❌ Errore durante la richiesta all'API: {e}")
            exit()

        all_places = places_result.get('results', [])
        next_page_token = places_result.get('next_page_token')

        while next_page_token:
            print("...carico altri risultati...")
            time.sleep(2)  # È richiesto un breve ritardo prima di chiedere la pagina successiva
            try:
                places_result = self.gmaps.places_nearby(page_token=next_page_token)
                all_places.extend(places_result.get('results', []))
                next_page_token = places_result.get('next_page_token')
            except Exception as e:
                print(f"❌ Errore durante il caricamento della pagina successiva: {e}")
                next_page_token = None  # Interrompi il ciclo in caso di errore

        print(f"\n✅ Ricerca completata! Ho trovato {len(all_places)} {place_type}.\n---")
        return [Place.load_from_google_place(p) for p in all_places]

# Esempio di utilizzo
if __name__ == "__main__":
    g = GoogleApi()
    v = g.find_villages(radius=1)
    print(v)