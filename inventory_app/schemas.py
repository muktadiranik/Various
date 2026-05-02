from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# Category Schemas
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
    items: List["ItemOut"] = []

    model_config = ConfigDict(from_attributes=True)

# Item Schemas
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int = 0
    price: float = 0.0
    category_id: int

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    category_id: Optional[int] = None

class ItemOut(ItemBase):
    id: int
    category: "CategoryOut"

    model_config = ConfigDict(from_attributes=True)

# For category items list (shallow category)
class CategoryOutForItem(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class ItemOutShort(ItemBase):
    id: int
    category: CategoryOutForItem

    model_config = ConfigDict(from_attributes=True)

