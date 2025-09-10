import requests
import json
from datetime import datetime
from typing import List, Dict
import os
from db.models import Place
from dotenv import load_dotenv
import uuid

load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY')


class GoogleMapsApiInterface:
    """
    Interfaccia per la nuova Google Places API (v1) che utilizza `requests`.
    Non richiede la libreria 'googlemaps'.
    """

    def __init__(self):
        if not API_KEY:
            raise ValueError("Chiave API non trovata. Imposta la variabile d'ambiente GOOGLE_API_KEY")
        self.api_key = API_KEY
        self.base_url = "https://places.googleapis.com/v1/places:searchNearby"

    def _make_request(self, field_mask: str, place_type: str, latitude: float, longitude: float, radius_km: int) -> Dict[str, Place]:
        """
        Helper privato per eseguire le chiamate POST alla nuova API.
        """
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": field_mask
        }
        payload = {
            "includedTypes": [place_type],
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": radius_km * 1000
                }
            }
        }
        try:
            response = requests.post(self.base_url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()  # Lancia un errore per status non 2xx
            return {p.get("id", str(uuid.uuid4())): Place.load_from_google_place(p) for p in response.json().get('places', [])}
        except requests.exceptions.RequestException as e:
            print(f"❌ Errore durante la chiamata API: {e}")
            if 'response' in locals():
                print(f"   Dettagli errore: {response.text}")
            return {}

    def find_places(self, place_type: str, latitude: float, longitude: float, radius_km: int) -> Dict[str, Place]:
        """
        Trova luoghi di un tipo specifico con una singola chiamata efficiente.
        Nota: la nuova API restituisce massimo 20 risultati per `searchNearby`.
        """
        print(f"🛰️  Sto cercando i '{place_type}' entro {radius_km} km con la nuova API...")

        # Chiediamo solo i campi base per una ricerca generica
        field_mask = "places.id,places.displayName,places.formattedAddress,places.types"

        places_data = self._make_request(field_mask, place_type, latitude, longitude, radius_km)
        print(f"✅ Ricerca completata! Trovati {len(places_data)} '{place_type}'.")
        return places_data

    def find_villages(self, latitude: float, longitude: float, radius_km: int) -> List[str]:
        """
        Trova luoghi di un tipo specifico con una singola chiamata efficiente.
        Nota: la nuova API restituisce massimo 20 risultati per `searchNearby`.
        """
        print(f"🛰️  Sto cercando i paesi entro {radius_km} km con la nuova API...")

        # Chiediamo solo i campi base per una ricerca generica
        field_mask = "places.id,places.displayName,places.formattedAddress,places.types"

        places_data = self._make_request(field_mask, 'administrative_area_level_3', latitude, longitude, radius_km)
        print(f"✅ Ricerca completata! Trovati {len(places_data)} .")
        return [p.name for p in places_data.values()]

    def find_places_nightlife(self, place_type: str, latitude: float, longitude: float, radius_km: int) -> Dict[str, Place]:
        """
        Trova luoghi e li filtra per orario di apertura serale in una SOLA chiamata API.
        """
        filter_hour = 22
        print(f"🚀 Eseguo una ricerca efficiente per '{place_type}' aperti dopo le {filter_hour}:00...")

        # Con la Field Mask, chiediamo anche gli orari di apertura dettagliati
        field_mask = "places.id,places.displayName,places.formattedAddress,places.regularOpeningHours"

        all_places_data = self._make_request(field_mask, place_type, latitude, longitude, radius_km)

        # Filtra i risultati ottenuti
        locali_filtrati_data = {}
        today_weekday = datetime.now().weekday()

        for k, place in all_places_data.items():
            if self._is_open_after(place, filter_hour, 5):
                locali_filtrati_data.update({k: place})

        print(
            f"✅ Filtraggio completato! Trovati {len(locali_filtrati_data)} locali aperti su {len(all_places_data)} totali.")
        return locali_filtrati_data

    def find_bars(self, latitude: float, longitude: float, radius_km: int) -> Dict[str, Place]:
        """Metodo scorciatoia per trovare bar serali."""
        return self.find_places_nightlife("bar", latitude, longitude, radius_km)

    def _is_open_after(self, place: Place, hour: int, weekday: int) -> bool:
        """Helper function per controllare l'orario di apertura."""
        if not place.opening_hours or not place.opening_hours.get('periods'):
            return False
        for period in place.opening_hours['periods']:
            open_info = period.get('open')
            if not open_info or open_info.get('day') != weekday:
                continue
            close_info = period.get('close')
            if not close_info or close_info.get('day') != weekday or close_info.get('hour', 0) > hour:
                return True
        return False


# --- ESEMPIO DI UTILIZZO ---
if __name__ == '__main__':
    # Coordinate di Carate Brianza
    LATITUDE = 45.48285755202353
    LONGITUDE = 11.260698962274315
    RADIUS_KM = 10

    maps_api = GoogleMapsApiInterface()

    # print("\n--- CERCO BAR SERALI (METODO EFFICIENTE) ---")
    # bar_serali = maps_api.find_bars(LATITUDE, LONGITUDE, RADIUS_KM)
    # for bar in bar_serali:
    #     print(f"🍸 {bar.name} - {bar.address}")

    print("\n--- CERCO PAESI VICINI ---")
    paesi = maps_api.find_villages(LATITUDE, LONGITUDE, RADIUS_KM)
    for paese in paesi:
        print(f"📍 {paese}")