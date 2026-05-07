from sqlalchemy import String, Integer, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from ..database import Base
from .base import AuditMixin
from typing import List, Optional


class Category(Base, AuditMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    products: Mapped[List['Product']] = relationship(
        "Product", back_populates="category")


class Product(Base, AuditMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"))
    uom: Mapped[str] = mapped_column(
        String(20), default="pcs")  # pcs, kg, liter
    barcode: Mapped[Optional[str]] = mapped_column(String(100))
    qr_code: Mapped[Optional[str]] = mapped_column(Text)  # JSON or URL
    tags: Mapped[Optional[str]] = mapped_column(SQLiteJSON)  # list[str]
    min_stock_level: Mapped[int] = mapped_column(Integer, default=0)
    variants: Mapped[Optional[str]] = mapped_column(
        SQLiteJSON)  # list[dict: size/color]

    category: Mapped["Category"] = relationship(
        "Category", back_populates="products")
    stocks: Mapped[List["Stock"]] = relationship( # type: ignore
        "Stock", back_populates="product")
    stock_movements: Mapped[List['StockMovement']] = relationship(  # type: ignore
        "StockMovement", back_populates="product")
