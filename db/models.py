import json
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
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
    start_time: datetime = None
    end_time: datetime = None
    price: float = None
    description: str = ""

    @classmethod
    def load_from_google_gemini(cls, event: dict):
        m = dict(name=event.get('name', ''),
                 start_time=datetime.fromisoformat(event.get('start_time')) if event.get('start_time') else None,
                 end_time=datetime.fromisoformat(event.get('end_time')) if event.get('end_time') else None,
                 price=event.get('price', 0.0),
                 description=event.get('description', ''))
        return cls.load(m)


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class Place(BasicModel):
    name: str
    id: str
    address: str
    type: List[str]
    opening_hours: dict = field(default_factory=dict)  # e.g., {'open_now': True, 'periods': [...], 'weekday_text': [...]}
    rating: float = 0.0
    longitude: float = None
    latitude: float = None
    instagram_URL: str = ""
    events: List[Event] = field(default_factory=list)  # list of events

    @classmethod
    def load_from_google_place(cls, place: dict):
        map = dict(name=place.get('displayName', {}).get("text", ''),
                   id=place.get('id', ''),
                   address=place.get('formattedAddress', ''),
                   type=place.get('types', []),
                   opening_hours=place.get('regularOpeningHours', {}),)
        return cls.load(map)

    def update(self, place_data: dict):
        for k, v in place_data.items():
            if v is not None:
                self.__setattr__(k, v)

