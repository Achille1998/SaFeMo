import inspect
import json

from api.google_maps_api_interface import GoogleMapsApiInterface
from handlers.base_handler import BaseHandler
import logging
logger = logging.getLogger(inspect.currentframe().f_back.f_globals["__name__"])


class PLacesAroundHandler(BaseHandler):
    google_maps_api: GoogleMapsApiInterface

    def initialize(self) -> None:
        self.google_maps_api = GoogleMapsApiInterface()

    async def get(self):

        lat = self.get_query_argument("lat", default="0.0")
        lon = self.get_query_argument("lon", default="0.0")
        radius = self.get_query_argument("radius", default="1")  # in km
        logger.info(f"Ricevuta richiesta per lat: {lat}, lon: {lon} and radius: {radius}")
        if response := self.google_maps_api.find_bars(latitude=lat, longitude=lon, radius=float(radius)):
            self.write(dict(places=[place.dump() for place in response]))
            return
        self.error("No places found")
