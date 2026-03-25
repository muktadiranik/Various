from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    projects = relationship("Project", back_populates="owner")

    def __repr__(self):
        return f"User(id={self.id!r}, email={self.email!r}, is_active={self.is_active!r}, is_superuser={self.is_superuser!r}, is_verified={self.is_verified!r})"
