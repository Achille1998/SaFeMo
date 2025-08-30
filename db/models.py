import json
from abc import ABC
from dataclasses import dataclass, field
from typing import ClassVar, Type, Mapping, Any, List

import marshmallow
import marshmallow_dataclass
from bson import ObjectId


class BaseSchema(marshmallow.Schema):
    class Meta:
        unknown = marshmallow.EXCLUDE


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class BasicModel(ABC):
    Schema: ClassVar[Type[BaseSchema]]  # only for type hinting

    def __getitem__(self, key):
        return self.__getattribute__(key)

    def dump(self) -> dict:
        if not self.Schema().ordered:
            return self.Schema().dump(self)
        else:
            return dict(self.Schema().dump(self))

    def dumps(self) -> str:
        return self.Schema().dumps(self)

    @classmethod
    def dump_many(cls, obj):
        return cls.Schema(many=True).dump(obj)

    @classmethod
    def load(cls, mapping: Mapping):
        return cls.Schema().load(mapping)

    @classmethod
    def loadm(cls, model: Any):
        return cls.loads(
            json.dumps(model, default=cls.todict))

    @classmethod
    def todict(cls, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, bytes):
            return o.decode('utf-8')
        return o.__dict__

    @classmethod
    def load_many(cls, model: Any):
        return cls.Schema(many=True).load(model)

    @classmethod
    def loads(cls, model: str):
        return cls.Schema().loads(model)


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class Event(BasicModel):
    name: str = None
    date: float = None
    start_time: float = None
    end_time: float = None
    price: float = 0.0
    description: str = ""


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class Place(BasicModel):
    name: str
    address: str
    rating: float
    type: List[str]
    longitude: float
    latitude: float
    instagram_URL: str = ""
    events: List[Event] = field(default_factory=list)  # list of events

    @classmethod
    def load_from_google_place(cls, place: dict):
        map = dict(name=place.get('name', ''),
                   address=place.get('vicinity', ''),
                   rating=place.get('rating', 0.0),
                   type=place.get('types', []),
                   longitude=place.get('geometry', {}).get('location', {}).get('lng', 0.0),
                   latitude=place.get('geometry', {}).get('location', {}).get('lat', 0.0))
        return cls.load(map)

    @property
    def id(self):
        return f"{self.name}_{self.address}".replace(" ", "_").lower()


