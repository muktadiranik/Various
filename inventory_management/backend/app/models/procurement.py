from sqlalchemy import String, Integer, Float, ForeignKey, Date, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from ..database import Base
from .base import AuditMixin
from typing import List, Optional
import datetime


class POStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class Supplier(Base, AuditMixin):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    contact_email: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)

    purchase_orders: Mapped[List['PurchaseOrder']] = relationship(
        "PurchaseOrder", back_populates="supplier")


class PurchaseOrder(Base, AuditMixin):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"))
    status: Mapped[POStatus] = mapped_column(default=POStatus.PENDING)
    expected_date: Mapped[Optional[datetime.date]]
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text(500))

    supplier: Mapped["Supplier"] = relationship(
        "Supplier", back_populates="purchase_orders")
    # lines in separate table if needed


class GoodsReceipt(Base, AuditMixin):
    __tablename__ = "goods_receipts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    po_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("purchase_orders.id"))
    received_qty: Mapped[int]
    quality_passed: Mapped[bool]
    stock_movement_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("stock_movements.id"), nullable=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    unit_cost: Mapped[float] = mapped_column(Float, default=0.0)
    stock_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("stocks.id"), nullable=True)
