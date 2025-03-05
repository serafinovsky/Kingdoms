import socket

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    sentry_dsn: str = Field(validation_alias="sentry_dsn")
    redis_dsn: RedisDsn
    alphabet: str = Field(default="9Qh1UT6ewJLmGyWHokjIM7NCYfxaS4Zg2PvVEOlFpXt0rc3bDsn8RdiuBAzq5K")
    room_ttl: int = Field(default=86400)
    debug: bool = Field(validation_alias="debug")
    internal_url: str = Field(validation_alias="internal_url")
    default_king_power: int = Field(default=12)
    default_castle_power: int = Field(default=12)
    colors_count: int = Field(default=6)
    replica_id: str = socket.gethostname()

    model_config = SettingsConfigDict(env_prefix="rooms_")


settings = AppSettings()
