from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app_types.common import Provider
from models.base import Base


class User(Base):
    __tablename__ = "user"

    joined_dt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    provider: Mapped[Provider] = mapped_column(Enum(Provider, native_enum=False, length=48))
    external_id: Mapped[str]
    profile: Mapped["Profile"] = relationship(
        "Profile", back_populates="user", uselist=False, lazy="joined"
    )
    login_history = relationship("LoginHistory", back_populates="user", uselist=False)

    __table_args__ = (Index("ix_external_id_provider", "external_id", "provider", unique=True),)

    def __repr__(self) -> str:
        return f"<User joined_dt={self.joined_dt.isoformat()} provider={self.provider.name}>"


class Profile(Base):
    __tablename__ = "profile"

    avatar: Mapped[str] = mapped_column(String(2048), default="")
    username: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(512))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False,
        index=True,
        unique=True,
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="profile", uselist=False, lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<Profile user_id={self.user_id} username={self.username} name={self.name}>"


class LoginHistory(Base):
    __tablename__ = "login_history"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user = relationship("User", back_populates="login_history")

    provider: Mapped[Provider] = mapped_column(
        Enum(Provider, native_enum=False, length=48),
        nullable=False,
    )

    login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
    )
    user_agent: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<LoginHistory "
            f"user_id={self.user_id} "
            f"provider={self.provider.name} "
            f"login_at={self.login_at.isoformat()}>"
        )
