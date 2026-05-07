from pydantic import BaseModel, ConfigDict
from typing import Optional


class WarehouseBase(BaseModel):
    name: str
    location: Optional[str] = None
    address: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None


class WarehouseOut(WarehouseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
