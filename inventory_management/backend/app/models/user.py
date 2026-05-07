from sqlalchemy import String, Integer, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from ..database import Base
from .base import AuditMixin


class UserRole(str, PyEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"


class User(Base, AuditMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(default=UserRole.STAFF)
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=True)

    movements: Mapped[list["StockMovement"]] = relationship(  # type: ignore
        "StockMovement", primaryjoin="StockMovement.created_by==User.id", foreign_keys="[StockMovement.created_by]")
