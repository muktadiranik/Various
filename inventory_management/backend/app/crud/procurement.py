from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models.procurement import Supplier, PurchaseOrder, GoodsReceipt
from ..schemas.procurement import SupplierCreate, PurchaseOrderCreate, GoodsReceiptCreate, SupplierOut, PurchaseOrderOut, GoodsReceiptOut
from ..schemas.stock import StockMovementCreate


def get_suppliers(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(Supplier).offset(skip).limit(limit)).all()


def get_supplier(db: Session, supplier_id: int):
    return db.get(Supplier, supplier_id)


def create_supplier(db: Session, supplier: SupplierCreate):
    db_supplier = Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


def update_supplier(db: Session, supplier_id: int, supplier: SupplierCreate):
    db_supplier = db.get(Supplier, supplier_id)
    if not db_supplier:
        return None
    update_data = supplier.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_supplier, field, value)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


def delete_supplier(db: Session, supplier_id: int):
    db_supplier = db.get(Supplier, supplier_id)
    if db_supplier:
        db.delete(db_supplier)
        db.commit()
        return True
    return False


def get_purchase_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(PurchaseOrder).offset(skip).limit(limit)).all()


def get_purchase_order(db: Session, po_id: int):
    return db.get(PurchaseOrder, po_id)


def create_purchase_order(db: Session, po: PurchaseOrderCreate):
    db_po = PurchaseOrder(**po.model_dump())
    db.add(db_po)
    db.commit()
    db.refresh(db_po)
    return db_po


def update_purchase_order(db: Session, po_id: int, po: PurchaseOrderCreate):
    db_po = db.get(PurchaseOrder, po_id)
    if not db_po:
        return None
    update_data = po.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_po, field, value)
    db.commit()
    db.refresh(db_po)
    return db_po


def delete_purchase_order(db: Session, po_id: int):
    db_po = db.get(PurchaseOrder, po_id)
    if db_po:
        db.delete(db_po)
        db.commit()
        return True
    return False


def get_goods_receipts(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(GoodsReceipt).offset(skip).limit(limit)).all()


def get_goods_receipt(db: Session, receipt_id: int):
    return db.get(GoodsReceipt, receipt_id)


def create_goods_receipt(db: Session, receipt: GoodsReceiptCreate):
    # First create the receipt record
    db_receipt = GoodsReceipt(
        **receipt.model_dump(exclude={'stock_movement_id'}))
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)

    # Auto create stock movement for receiving (only if quality passed)
    if db_receipt.quality_passed:
        from .stock import create_stock_movement  # Avoid circular import

        # Assume receipt needs product_id, stock_id, cost etc - extend schema if needed
        # For demo, use example values; in prod, receipt schema needs product/stock/cost fields
        movement_data = StockMovementCreate(
            product_id=receipt.product_id,
            stock_id=receipt.stock_id,
            type="stock_in",
            quantity=receipt.received_qty,
            reference_id=db_receipt.po_id,
            reason="Goods receipt",
            cost=receipt.unit_cost
        )
        movement = create_stock_movement(db, movement_data)
        db_receipt.stock_movement_id = movement.id
        db.commit()
        db.refresh(db_receipt)

    return db_receipt


def update_goods_receipt(db: Session, receipt_id: int, receipt: GoodsReceiptCreate):
    db_receipt = db.get(GoodsReceipt, receipt_id)
    if not db_receipt:
        return None
    update_data = receipt.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_receipt, field, value)
    db.commit()
    db.refresh(db_receipt)
    return db_receipt


def delete_goods_receipt(db: Session, receipt_id: int):
    db_receipt = db.get(GoodsReceipt, receipt_id)
    if db_receipt:
        db.delete(db_receipt)
        db.commit()
        return True
    return False
