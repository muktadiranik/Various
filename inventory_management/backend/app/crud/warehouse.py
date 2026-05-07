from sqlalchemy.orm import Session
from ..models.warehouse import Warehouse
from ..schemas.warehouse import WarehouseCreate, WarehouseUpdate
from sqlalchemy import select


def get_warehouses(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(Warehouse).offset(skip).limit(limit)).all()


def get_warehouse(db: Session, warehouse_id: int):
    return db.get(Warehouse, warehouse_id)


def create_warehouse(db: Session, warehouse: WarehouseCreate):
    db_warehouse = Warehouse(**warehouse.model_dump())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def update_warehouse(db: Session, warehouse_id: int, warehouse: WarehouseUpdate):
    db_warehouse = db.get(Warehouse, warehouse_id)
    if not db_warehouse:
        return None
    update_data = warehouse.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_warehouse, field, value)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def delete_warehouse(db: Session, warehouse_id: int):
    db_warehouse = db.get(Warehouse, warehouse_id)
    if db_warehouse:
        db.delete(db_warehouse)
        db.commit()
        return True
    return False
