from typing import Dict

from api.apify_api_interface import ApifyApiInterface
from api.google_maps_api_interface import GoogleMapsApiInterface
from api.gemini_api_interface import GeminiApiInterface
from db.locals_dao import LocalsDAO
from db.models import Place


class PlacesDataCollector:
    def __init__(self):
        self.google_maps = GoogleMapsApiInterface()
        self.gemini = GeminiApiInterface()
        self.apify = ApifyApiInterface()
        self.locals_dao = LocalsDAO()

    def collect_places_nearby(self, place_type, latitude, longitude, radius) -> Dict[str, Place]:
        if place_type == "bar":
            g_places = self.google_maps.find_places_nightlife(place_type=place_type, latitude=latitude, longitude=longitude, radius_km=radius)
        else:
            g_places = self.google_maps.find_places(place_type=place_type, latitude=latitude, longitude=longitude, radius_km=radius)
        db_places = self.locals_dao.get_places_details(place_type=place_type, new_places=g_places)
        for place in db_places.values():
            if not place.instagram_URL:
                if url := self.apify.get_profile_from_place(place):
                    place.instagram_URL = url.get("url")
        self.locals_dao.dump_db(place_type, db_places)

        posts = self.apify.get_posts_from_places(db_places)
        events = self.gemini.get_events_from_posts(posts)
        self.locals_dao.dump_db(place_type, db_places)
        return db_places


# --- ESEMPIO DI UTILIZZO ---
if __name__ == '__main__':
    # Coordinate di Carate Brianza
    LATITUDE = 45.48285755202353
    LONGITUDE = 11.260698962274315
    RADIUS_KM = 2

    c = PlacesDataCollector()
    results = c.collect_places_nearby("bar", LATITUDE, LONGITUDE, RADIUS_KM)
    print(results)
