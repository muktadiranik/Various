from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..crud.warehouse import get_warehouses, get_warehouse, create_warehouse, update_warehouse, delete_warehouse
from ..schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseOut
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@router.get("/", response_model=List[WarehouseOut])
def read_warehouses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    warehouses = get_warehouses(db, skip=skip, limit=limit)
    return warehouses


@router.get("/{warehouse_id}", response_model=WarehouseOut)
def read_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    warehouse = get_warehouse(db, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.post("/", response_model=WarehouseOut, status_code=201)
def create_new_warehouse(warehouse: WarehouseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_warehouse(db, warehouse)


@router.put("/{warehouse_id}", response_model=WarehouseOut)
def modify_warehouse(warehouse_id: int, warehouse: WarehouseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = update_warehouse(db, warehouse_id, warehouse)
    if updated is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return updated


@router.delete("/{warehouse_id}", status_code=204)
def remove_warehouse(warehouse_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    success = delete_warehouse(db, warehouse_id)
    if not success:
        raise HTTPException(status_code=404, detail="Warehouse not found")
