from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base
from .base import AuditMixin
from typing import List, Optional


class Warehouse(Base, AuditMixin):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    location: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[Optional[str]] = mapped_column(Text)

    stocks: Mapped[List['Stock']] = relationship( # type: ignore
        "Stock", back_populates="warehouse")
    storage_locations: Mapped[List["StorageLocation"]] = relationship( # type: ignore
        "StorageLocation", back_populates="warehouse")
