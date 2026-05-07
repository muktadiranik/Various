from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..crud.sales import get_sales_orders, get_sales_order, create_sales_order, update_sales_order, delete_sales_order
from ..schemas.sales import SalesOrderCreate, SalesOrderOut
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/", response_model=List[SalesOrderOut])
def read_sales_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        orders = get_sales_orders(db, skip=skip, limit=limit)
        return orders
    except Exception:
        return []


@router.get("/{so_id}", response_model=SalesOrderOut)
def read_sales_order(so_id: int, db: Session = Depends(get_db)):
    order = get_sales_order(db, so_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Sales order not found")
    return order


@router.post("/", response_model=SalesOrderOut, status_code=201)
def create_new_sales_order(order: SalesOrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_order = create_sales_order(db, order)
    db_order.line_items = order.line_items
    return db_order


@router.put("/{so_id}", response_model=SalesOrderOut)
def modify_sales_order(so_id: int, order: SalesOrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = update_sales_order(db, so_id, order)
    if updated is None:
        raise HTTPException(status_code=404, detail="Sales order not found")
    updated.line_items = order.line_items
    return updated


@router.delete("/{so_id}", status_code=204)
def remove_sales_order(so_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    success = delete_sales_order(db, so_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sales order not found")
