from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from typing import List
from ..database import get_db
from ..crud.stock import get_stock_movements, get_stocks
from ..crud.product import get_low_stock_products
from ..crud.product import Product
from ..models.stock import StockStatus, StockMovement
from ..schemas.stock import StockOut
from ..core.security import get_current_user
from ..models.user import User
from datetime import date, timedelta
from pydantic import BaseModel

router = APIRouter(prefix="/reports", tags=["reports"])


class LowStockReport(BaseModel):
    product: str
    sku: str
    current_stock: int
    min_level: int
    days_supply: int


class ValuationReport(BaseModel):
    product_id: int
    sku: str
    total_value: float
    method: str
    available_qty: int


@router.get("/low-stock", response_model=List[LowStockReport])
def get_low_stock_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Low stock alerts across all products
    """
    low_stocks = get_low_stock_products(db)  # Implement in crud/product.py
    return low_stocks


@router.get("/valuation/{product_id}", response_model=ValuationReport)
def get_stock_valuation(product_id: int, method: str = "weighted", db: Session = Depends(get_db)):
    """
    Stock valuation: FIFO/LIFO/Weighted Average
    """
    from ..crud.stock import calculate_valuation
    valuation = calculate_valuation(db, product_id, method)
    return valuation


@router.get("/movements-summary")
def get_movements_summary(days: int = 30, db: Session = Depends(get_db)):
    """
    Recent stock movements summary
    """
    from_date = date.today() - timedelta(days=days)
    movements = db.scalars(
        select(StockMovement)
        .where(StockMovement.created_at >= from_date)
        .order_by(StockMovement.created_at.desc())
    ).all()
    return {
        "total_movements": len(movements),
        "total_in": sum(m.quantity for m in movements if m.type == 'stock_in'),
        "total_out": sum(m.quantity for m in movements if m.type == 'stock_out'),
        "movements": movements[:50]
    }


@router.get("/cogs")
def get_cogs_report(days: int = 30, db: Session = Depends(get_db)):
    """
    Cost of Goods Sold report
    """
    from_date = date.today() - timedelta(days=days)
    out_movements = db.scalars(
        select(func.sum(StockMovement.quantity * StockMovement.cost))
        .where(and_(StockMovement.type == 'stock_out', StockMovement.created_at >= from_date))
    ).one()
    return {"cogs": out_movements or 0}
