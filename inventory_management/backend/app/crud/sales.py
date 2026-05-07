from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models.sales import SalesOrder
from ..schemas.sales import SalesOrderCreate
from ..schemas.stock import StockMovementCreate
import json


def get_sales_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(SalesOrder).offset(skip).limit(limit)).all()


def get_sales_order(db: Session, so_id: int):
    return db.get(SalesOrder, so_id)


def create_sales_order(db: Session, so: SalesOrderCreate):
    db_so = SalesOrder(**so.model_dump(exclude={'line_items'}))
    import json
    db_so.line_items = json.dumps(so.line_items or [])
    db.add(db_so)
    db.commit()
    db.refresh(db_so)
    return db_so


def update_sales_order(db: Session, so_id: int, so: SalesOrderCreate):
    db_so = db.get(SalesOrder, so_id)
    if not db_so:
        return None

    old_status = db_so.status

    update_data = so.model_dump(exclude_unset=True)
    if 'line_items' in update_data:
        setattr(db_so, 'line_items', json.dumps(
            update_data.pop('line_items') or []))
    for field, value in update_data.items():
        setattr(db_so, field, value)
    db.commit()
    db.refresh(db_so)

    # Handle status transitions with stock logic
    if so.status != old_status:
        handle_sales_status_change(db, db_so)

    return db_so


def handle_sales_status_change(db: Session, sales_order: SalesOrder):
    """
    Handle stock reservation/deduct based on status change
    """
    from .stock import create_stock_movement
    import json

    line_items = json.loads(sales_order.line_items or '[]')
    for line in line_items:
        movement_data = StockMovementCreate(
            product_id=line['product_id'],
            stock_id=line['stock_id'],
            quantity=line['qty'],
            reference_id=sales_order.id,
            reason=f"Sales order {sales_order.status}"
        )

        if sales_order.status == "confirmed" and line.get('reserved', False) == False:
            movement_data.type = "reserve"
            create_stock_movement(db, movement_data)
            line['reserved'] = True

        elif sales_order.status == "shipped":
            movement_data.type = "stock_out"
            create_stock_movement(db, movement_data)

        elif sales_order.status == "returned":
            movement_data.type = "stock_in"  # Restock
            movement_data.quantity = -line['qty']  # Negative for return
            create_stock_movement(db, movement_data)


def delete_sales_order(db: Session, so_id: int):
    db_so = db.get(SalesOrder, so_id)
    if db_so:
        db.delete(db_so)
        db.commit()
        return True
    return False
