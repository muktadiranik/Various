from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date


class BatchBase(BaseModel):
    product_id: int
    batch_number: str
    expiry_date: Optional[date] = None
    quantity: int
    serial_numbers: Optional[List[str]] = None
    location: Optional[str] = None


class BatchCreate(BatchBase):
    pass


class BatchOut(BatchBase):
    id: int
    cost: float

    model_config = ConfigDict(from_attributes=True)
