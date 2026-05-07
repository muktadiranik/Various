from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..crud.stock import (get_stocks, get_stock, create_stock, update_stock, delete_stock,
                          get_stock_movements, create_stock_movement, get_stock_movement, update_stock_movement, delete_stock_movement)
from ..schemas.stock import StockCreate, StockUpdate, StockMovementCreate, StockOut
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("/", response_model=List[StockOut])
def read_stocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stocks = get_stocks(db, skip=skip, limit=limit)
    return stocks


@router.post("/", response_model=StockOut, status_code=201)
def create_new_stock(stock: StockCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_stock(db, stock)


@router.get("/movements", response_model=List[StockOut])
def read_stock_movements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movements = get_stock_movements(db, skip=skip, limit=limit)
    return movements


@router.post("/movements", response_model=StockOut, status_code=201)
def create_new_movement(movement: StockMovementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_stock_movement(db, movement)
