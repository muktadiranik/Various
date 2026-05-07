from pydantic import BaseModel, ConfigDict
from typing import Optional
from ..models.stock import StockStatus


class StockBase(BaseModel):
    product_id: int
    warehouse_id: int
    available_qty: int = 0
    reserved_qty: int = 0
    committed_qty: int = 0
    status: StockStatus = StockStatus.OUT_OF_STOCK


class StockCreate(StockBase):
    pass


class StockUpdate(BaseModel):
    available_qty: Optional[int] = None
    reserved_qty: Optional[int] = None
    committed_qty: Optional[int] = None


class StockOut(StockBase):
    id: int
    avg_cost: float

    model_config = ConfigDict(from_attributes=True)


class StockMovementBase(BaseModel):
    type: str
    quantity: int
    reference_id: Optional[int] = None
    reason: Optional[str] = None
    batch_id: Optional[int] = None


class StockMovementCreate(StockMovementBase):
    product_id: int
    stock_id: int


class StockMovementOut(StockMovementBase):
    id: int
    product_id: int
    stock_id: int
    cost: float

    model_config = ConfigDict(from_attributes=True)
