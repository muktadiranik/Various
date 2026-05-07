from ..models.stock import StockStatus
from ..models.product import Product
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..models.stock import Stock, StockMovement
from ..schemas.stock import StockCreate, StockUpdate, StockMovementCreate, StockOut


def get_stocks(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(Stock).offset(skip).limit(limit)).all()


def get_stock(db: Session, stock_id: int):
    return db.get(Stock, stock_id)


def create_stock(db: Session, stock: StockCreate):
    db_stock = Stock(**stock.model_dump())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock


def update_stock(db: Session, stock_id: int, stock: StockUpdate):
    db_stock = db.get(Stock, stock_id)
    if not db_stock:
        return None
    update_data = stock.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_stock, field, value)
    db.commit()
    db.refresh(db_stock)
    return db_stock


def delete_stock(db: Session, stock_id: int):
    db_stock = db.get(Stock, stock_id)
    if db_stock:
        db.delete(db_stock)
        db.commit()
        return True
    return False


def get_stock_movements(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(StockMovement).offset(skip).limit(limit)).all()


def get_stock_movement(db: Session, movement_id: int):
    return db.get(StockMovement, movement_id)


def create_stock_movement(db: Session, movement: StockMovementCreate):
    db_movement = StockMovement(**movement.model_dump())
    if 'cost' not in movement.model_dump() or movement.model_dump()['cost'] is None:
        db_movement.cost = 0.0
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)

    # Auto process stock update
    process_stock_movement(db, db_movement)

    return db_movement


def process_stock_movement(db: Session, movement: StockMovement):
    """
    Automatically update stock levels based on movement type.
    Audit trail via movement record.
    """
    stock = db.get(Stock, movement.stock_id)
    if not stock:
        return

    product = db.scalars(select(Product).where(
        Product.id == movement.product_id)).first()
    if not product:
        return

    qty = movement.quantity
    if qty == 0:
        return

    old_available = stock.available_qty
    old_reserved = stock.reserved_qty

    if movement.type.lower() == 'stock_in':
        # Update weighted avg cost
        if movement.cost and old_available > 0:
            new_total_cost = (stock.avg_cost * old_available) + \
                (movement.cost * qty)
            stock.avg_cost = new_total_cost / (old_available + qty)
        elif movement.cost:
            stock.avg_cost = movement.cost
        stock.available_qty += qty

    elif movement.type.lower() == 'stock_out':
        if stock.available_qty < qty:
            raise ValueError(
                f"Insufficient stock: {stock.available_qty} < {qty}")
        stock.available_qty -= qty

    elif movement.type.lower() == 'reserve':
        stock.reserved_qty += qty
        stock.available_qty -= qty  # Available excludes reserved

    elif movement.type.lower() == 'unreserve':
        stock.reserved_qty -= qty
        stock.available_qty += qty

    elif movement.type.lower() == 'transfer_out':
        stock.available_qty -= qty

    elif movement.type.lower() == 'transfer_in':
        stock.available_qty += qty

    # Update status based on min_stock_level
    stock.status = (
        StockStatus.OUT_OF_STOCK if stock.available_qty == 0 else
        StockStatus.LOW_STOCK if stock.available_qty <= product.min_stock_level else
        StockStatus.IN_STOCK
    )

    db.commit()
    db.refresh(stock)


def get_low_stock_products(db: Session, threshold: int = 10):
    """
    Get products with low stock levels across warehouses
    """
    stmt = select(Product, func.coalesce(func.sum(Stock.available_qty), 0).label('total_stock')) \
        .outerjoin(Stock).group_by(Product.id) \
        .having(func.coalesce(func.sum(Stock.available_qty), 0) <= Product.min_stock_level)
    result = db.execute(stmt).all()
    return [{"product": r.Product.name, "sku": r.Product.sku, "current_stock": r.total_stock, "min_level": r.Product.min_stock_level} for r in result]


def update_stock_movement(db: Session, movement_id: int, movement: StockMovementCreate):
    db_movement = db.get(StockMovement, movement_id)
    if not db_movement:
        return None
    update_data = movement.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_movement, field, value)
    db.commit()
    db.refresh(db_movement)
    return db_movement


def delete_stock_movement(db: Session, movement_id: int):
    db_movement = db.get(StockMovement, movement_id)
    if db_movement:
        db.delete(db_movement)
        db.commit()
        return True
    return False
