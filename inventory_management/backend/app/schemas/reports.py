from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class LowStockReport(BaseModel):
    product: str
    sku: str
    current_stock: int
    min_level: int
    days_supply: Optional[int] = None


class ValuationReport(BaseModel):
    product_id: int
    sku: str
    total_value: float
    method: str
    available_qty: int


class MovementsSummary(BaseModel):
    total_movements: int
    total_in: int
    total_out: int
    movements: List[dict]
