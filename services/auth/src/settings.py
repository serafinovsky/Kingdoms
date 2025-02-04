from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    pg_user: str
    pg_password: str
    pg_host: str = Field(validation_alias="pg_host")
    pg_name: str
    host: str
    port: int
    pg_dsn: PostgresDsn
    redis_dsn: RedisDsn
    media_root: str
    debug: bool = Field(validation_alias="debug")
    access_jwt_secret: str
    refresh_jwt_secret: str
    github_client_id: str
    github_client_secret: str
    github_redirect: str
    yandex_client_id: str
    yandex_client_secret: str
    yandex_redirect: str
    access_token_ttl: int
    refresh_token_ttl: int
    min_refresh_ttl: int = Field(default=24 * 60 * 60)
    refresh_token_cookie: str = Field(default="_rt")

    media_root: str = "/media"
    media_url: str = "/media/"

    model_config = SettingsConfigDict(env_prefix="auth_")


settings = AppSettings()
