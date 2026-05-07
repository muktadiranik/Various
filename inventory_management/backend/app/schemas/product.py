from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryOut(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    category_id: int
    uom: str = "pcs"
    barcode: Optional[str] = None
    tags: Optional[List[str]] = None
    min_stock_level: int = 0
    variants: Optional[List[dict]] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    uom: Optional[str] = None
    barcode: Optional[str] = None
    tags: Optional[List[str]] = None
    min_stock_level: Optional[int] = None
    variants: Optional[List[dict]] = None


class ProductOut(ProductBase):
    id: int
    category: CategoryOut

    model_config = ConfigDict(from_attributes=True)
