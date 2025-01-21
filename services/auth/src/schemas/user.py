from pydantic import BaseModel


class ProfileBase(BaseModel):
    avatar: str = ""
    username: str
    name: str


class ProfileCreate(ProfileBase):
    user_id: int


class ProfileUpdate(BaseModel):
    avatar: str | None = None
    username: str | None = None
    name: str | None = None


class Profile(ProfileBase):
    class Config:
        from_attributes = True
