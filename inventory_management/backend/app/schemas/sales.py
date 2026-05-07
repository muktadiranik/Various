from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date
from ..models.sales import SalesStatus


class SalesOrderBase(BaseModel):
    customer_name: str
    status: SalesStatus = SalesStatus.PENDING
    order_date: Optional[date] = None
    total_amount: float = 0.0
    line_items: Optional[str] = None  # JSON string from DB


class SalesOrderCreate(SalesOrderBase):
    pass


class SalesOrderOut(SalesOrderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
