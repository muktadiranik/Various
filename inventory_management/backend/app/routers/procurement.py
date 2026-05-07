from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..crud.procurement import (get_suppliers, get_supplier, create_supplier, update_supplier, delete_supplier,
                                get_purchase_orders, get_purchase_order, create_purchase_order, update_purchase_order, delete_purchase_order,
                                get_goods_receipts, create_goods_receipt)
from ..schemas.procurement import SupplierCreate, PurchaseOrderCreate, GoodsReceiptCreate
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(prefix="/procurement", tags=["procurement"])


@router.get("/suppliers")
def read_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    suppliers = get_suppliers(db, skip=skip, limit=limit)
    return suppliers


@router.post("/suppliers", status_code=201)
def create_supplier_route(supplier: SupplierCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_supplier(db, supplier)


@router.get("/purchase-orders")
def read_purchase_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pos = get_purchase_orders(db, skip=skip, limit=limit)
    return pos


@router.post("/purchase-orders", status_code=201)
def create_po(po: PurchaseOrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_purchase_order(db, po)


@router.post("/goods-receipts", status_code=201)
def create_goods_receipt_route(receipt: GoodsReceiptCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_goods_receipt(db, receipt)
