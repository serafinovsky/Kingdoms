from pydantic import BaseModel, ConfigDict, Field

from app_types.common import PyObjectId
from app_types.map import GameMap, MapMeta


class MapAndMetaBase(BaseModel):
    map: GameMap
    meta: MapMeta

    model_config = ConfigDict(
        use_enum_values=True,
    )


class MapAndMetaCreate(MapAndMetaBase):
    model_config = ConfigDict(
        use_enum_values=True,
    )


class MapAndMeta(MapAndMetaBase):
    id: PyObjectId = Field(alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )


class MapAndMetaCollection(BaseModel):
    items: list[MapAndMeta]


class MapBase(BaseModel):
    map: GameMap


class MapCreate(MapBase):
    model_config = ConfigDict(
        use_enum_values=True,
    )


class MapUpdate(MapBase):
    model_config = ConfigDict(
        use_enum_values=True,
    )
