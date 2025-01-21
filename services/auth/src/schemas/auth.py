import uuid
from datetime import datetime, timedelta
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app_types.common import Provider
from settings import settings


class LoginInfo(BaseModel):
    """Information about login"""

    user_id: int
    provider: Provider
    ip_address: str
    user_agent: str


class AuthorizeData(BaseModel):
    """OAuth authorization data containing the authorization code."""

    code: str


class TokenMeta(BaseModel):
    """Base token metadata model."""

    model_config = ConfigDict(frozen=True)

    sub: str  # subject (user id)
    jti: str  # unique token identifier
    exp: int  # expiration timestamp


class AccessPayload(TokenMeta):
    """Access token payload containing user identification and expiration."""

    jti: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique token identifier",
    )
    exp: int = Field(
        default_factory=lambda: int(
            (
                datetime.now() + timedelta(seconds=settings.access_token_ttl)
            ).timestamp()
        ),
        description="Token expiration timestamp",
    )

    @field_validator("sub", mode="before")
    @classmethod
    def convert_sub_to_str(cls, value: int) -> str:
        """Convert subject ID to string."""
        return str(value)


class RefreshPayload(TokenMeta):
    """Refresh token payload containing user identification, fingerprint,
    and expiration."""

    fgp: str  # fingerprint
    jti: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique token identifier",
    )
    exp: int = Field(
        default_factory=lambda: int(
            (
                datetime.now() + timedelta(seconds=settings.refresh_token_ttl)
            ).timestamp()
        ),
        description="Token expiration timestamp",
    )

    @field_validator("sub", mode="before")
    @classmethod
    def convert_sub_to_str(cls, value: int) -> str:
        """Convert subject ID to string."""
        return str(value)


class UserCreate(BaseModel):
    """Model for creating a new user."""

    provider: Provider
    external_id: str


class UserUpdate(BaseModel):
    """Model for updating user data."""

    is_active: bool


class UserData(BaseModel):
    """Common user data model across different providers."""

    provider: Provider
    external_id: str
    avatar_url: str
    username: str
    name: str


class GithubUser(BaseModel):
    """GitHub OAuth user data model."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    login: str
    name: str
    avatar_url: str
    email: str = ""

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_str(cls, value: int) -> str:
        """Convert GitHub ID to string."""
        return str(value)

    @field_validator("email", mode="before")
    @classmethod
    def process_empty_email(cls, value: Optional[str]) -> str:
        """Handle null email values from GitHub."""
        return "" if value is None else value

    def to_user_data(self) -> UserData:
        """Convert GithubUser to common UserData format."""
        return UserData(
            provider=Provider.GITHUB,
            external_id=self.id,
            avatar_url=self.avatar_url,
            username=self.login,
            name=self.name,
        )


class YandexUser(BaseModel):
    """Yandex OAuth user data model."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    id: str
    login: str
    name: str = Field(alias="real_name")
    avatar_url: str = ""
    email: str = Field(alias="default_email")
    is_avatar_empty: bool
    default_avatar_id: str

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_str(cls, value: int) -> str:
        """Convert Yandex ID to string."""
        return str(value)

    @model_validator(mode="after")
    @classmethod
    def set_avatar_url(cls, data: "YandexUser") -> "YandexUser":
        """Set avatar URL based on Yandex avatar data."""
        if not data.is_avatar_empty:
            data.avatar_url = (
                f"https://avatars.yandex.net/get-yapic/"
                f"{data.default_avatar_id}/islands-retina-middle"
            )
        return data

    def to_user_data(self) -> UserData:
        """Convert YandexUser to common UserData format."""
        return UserData(
            provider=Provider.YANDEX,
            external_id=self.id,
            avatar_url=self.avatar_url,
            username=self.login,
            name=self.name,
        )
