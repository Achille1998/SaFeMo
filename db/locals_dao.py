import json
from typing import Dict, Optional, Union

from marshmallow import ValidationError

from db.models import Place


class LocalsDAO:

    @staticmethod
    def load_db() -> Optional[Dict[str, Dict[str, Place]]]:
        """ load the db file and return a dict of places """
        with open("db/locals_db.json", "r") as f:
            try:
                db = json.load(f)
                for place_type, places in db.items():
                    for place_id, place in places.items():
                        try:
                            db[place_type].update({place_id: Place.load(place)})
                        except ValidationError:
                            pass
            except json.JSONDecodeError:
                return {}
        return db

    def get_places_details(self, place_type: str, new_places: Dict[str, Place]):
        """ update the db file with new places """
        db = self.load_db()
        if not (places := db.get(place_type)):
            print("no data found in db for this place type")
            return new_places
        for p_id, p in new_places.items():
            if p_id in db[place_type]:
                p.update(places.get(p_id).dump())
        return new_places

    def dump_db(self, place_type: str, new_places: Dict[str, Union[dict, Place]]):
        """ update the db file with new places """
        db = self.load_db()
        for p_id, p in db.get(place_type, {}).items():
            if isinstance(place := new_places.get(p_id, {}), Place):
                place = place.dump()
            p.update(place)
        with open("db/locals_db.json", "w") as f:
            json.dump(self.db_to_dict(db), f, indent=4)

    @staticmethod
    def db_to_dict(db: Dict[str, Union[dict, Place]]) -> Dict[str, Dict[str, dict]]:
        """ return the db as a dict """
        for place_type, places in db.items():
            for place_id, place in places.items():
                if isinstance(place, Place):
                    db[place_type].update({place_id: place.dump()})
        return db
