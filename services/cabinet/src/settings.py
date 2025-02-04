from pydantic import Field, MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    mongo_dsn: MongoDsn
    debug: bool = Field(validation_alias="debug")
    mongo_db: str
    rooms_collection: str = Field(default="rooms")
    maps_collection: str = Field(default="maps")
    internal_url: str = Field(validation_alias="internal_url")

    model_config = SettingsConfigDict(env_prefix="cabinet_")


settings = AppSettings()
