from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base
from .base import AuditMixin
from typing import List, Optional


class StorageLocation(Base, AuditMixin):
    __tablename__ = "storage_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warehouses.id"))
    code: Mapped[str] = mapped_column(String(50))  # A-01-Rack1
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(200))
    capacity: Mapped[Optional[int]] = mapped_column(Integer)

    warehouse: Mapped["Warehouse"] = relationship( # type: ignore
        "Warehouse", back_populates="storage_locations")
