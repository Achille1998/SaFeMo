import json
from models import Place
from instaScrapping.api.google_maps_api import GoogleApi
from instaScrapping.api.apify_api import InstaScraper


class LocalsDAO:
    def __init__(self):
        self.google_api = GoogleApi()
        self.apify_client = InstaScraper()
        with open("instaScrapping/locals_db.json", "r") as f:
            try:
                self.locals = {k: Place.load(v) for k, v in json.load(f).get('locals', {}).items()}
            except json.JSONDecodeError:
                self.locals = {}

    def get_bars_details(self, latitude, longitude, radius):
        bars = self.google_api.find_bars(latitude=latitude, longitude=longitude, radius=radius)
        bars_details = []
        for bar in bars:
            if bar_in_db := self.locals.get(bar.id):
                pass
            bars_details.append(bar_in_db)
            insta_url = self.apify_client.get_profile(bar.name + " " + bar.address)

    def update_bars_details(self):
        self.google_api.find_bars()
        with open("instaScrapping/locals_db.json", "w") as f:
            json.dump(self.locals, f, indent=4)

    def get_local_by_name(self, name):
        for bar in self.bars:
            if bar['name'].lower() == name.lower():
                return bar
        return None

    def get_all_bars(self):
        return self.bars

with open("instaScrapping/bar_db.json", "r") as f:
    bars = json.load(f)