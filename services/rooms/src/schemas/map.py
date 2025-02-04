from pydantic import BaseModel, ConfigDict

from app_types.map import GameMap, MapMeta


class MapAndMeta(BaseModel):
    map: GameMap
    meta: MapMeta

    model_config = ConfigDict(
        use_enum_values=True,
    )
