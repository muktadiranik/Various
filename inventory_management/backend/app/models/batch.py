from sqlalchemy import String, Integer, Float, ForeignKey, Date, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from ..database import Base
from .base import AuditMixin
from typing import List, Optional
import datetime


class Batch(Base, AuditMixin):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    batch_number: Mapped[str] = mapped_column(String(100), unique=True)
    expiry_date: Mapped[Optional[datetime.date]]
    quantity: Mapped[int]
    cost: Mapped[float] = mapped_column(default=0.0, nullable=True)
    serial_numbers: Mapped[Optional[str]]  # JSON list
    location: Mapped[Optional[str]]  # rack/bin

# Add to StockMovement model import/rel if needed
