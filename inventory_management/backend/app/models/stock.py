from sqlalchemy import Integer, Float, ForeignKey, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from ..database import Base
from .base import AuditMixin
from typing import List, Optional


class StockStatus(str, PyEnum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


class Stock(Base, AuditMixin):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warehouses.id"))
    available_qty: Mapped[int] = mapped_column(Integer, default=0)
    reserved_qty: Mapped[int] = mapped_column(Integer, default=0)
    committed_qty: Mapped[int] = mapped_column(Integer, default=0)
    avg_cost: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[StockStatus] = mapped_column(
        default=StockStatus.OUT_OF_STOCK)

    product: Mapped["Product"] = relationship(  # type: ignore
        "Product", back_populates="stocks")
    warehouse: Mapped["Warehouse"] = relationship( # type: ignore
        "Warehouse", back_populates="stocks")
    movements: Mapped[List['StockMovement']] = relationship(
        "StockMovement", back_populates="stock")


class StockMovement(Base, AuditMixin):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    stock_id: Mapped[int] = mapped_column(Integer, ForeignKey("stocks.id"))
    type: Mapped[str] = mapped_column(String(20))  # in, out, transfer, adjust
    quantity: Mapped[int] = mapped_column(Integer)
    reference_id: Mapped[Optional[int]] = mapped_column(Integer)  # PO/SO id
    reason: Mapped[Optional[str]] = mapped_column(String(200))
    batch_id: Mapped[Optional[int]] = mapped_column(Integer)
    cost: Mapped[float] = mapped_column(Float)

    product: Mapped["Product"] = relationship("Product")  # type: ignore
    stock: Mapped["Stock"] = relationship("Stock")
