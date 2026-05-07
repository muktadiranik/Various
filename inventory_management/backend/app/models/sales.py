from sqlalchemy import String, Integer, Float, ForeignKey, Date, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from ..database import Base
from .base import AuditMixin
from typing import List, Optional
from .stock import StockMovement
import datetime


class SalesStatus(str, PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    RETURNED = "returned"


class SalesOrder(Base, AuditMixin):
    __tablename__ = "sales_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(200))
    status: Mapped[SalesStatus] = mapped_column(default=SalesStatus.PENDING)
    order_date: Mapped[Optional[datetime.date]]
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    line_items: Mapped[Optional[str]] = mapped_column(Text, default='[]')  # JSON list[dict]

# movements: Mapped[List["StockMovement"]] = relationship(
    # "StockMovement", primaryjoin="SalesOrder.id==StockMovement.reference_id")

