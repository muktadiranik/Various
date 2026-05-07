from pydantic import BaseModel, ConfigDict
from typing import Optional
from ..models.procurement import POStatus
import datetime


class SupplierBase(BaseModel):
    name: str
    contact_email: str
    phone: str
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierOut(SupplierBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderBase(BaseModel):
    supplier_id: int
    status: POStatus = POStatus.PENDING
    expected_date: Optional[datetime.date] = None
    total_amount: float = 0.0
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    pass


class PurchaseOrderOut(PurchaseOrderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class GoodsReceiptBase(BaseModel):
    po_id: int
    product_id: int
    stock_id: int
    unit_cost: Optional[float] = 0.0
    received_qty: int
    quality_passed: bool


class GoodsReceiptCreate(GoodsReceiptBase):
    pass


class GoodsReceiptOut(GoodsReceiptBase):
    id: int
    stock_movement_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)
