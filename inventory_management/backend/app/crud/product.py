from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models.product import Category, Product
from ..schemas.product import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(Category).offset(skip).limit(limit)).all()


def get_category(db: Session, category_id: int):
    return db.get(Category, category_id)


def create_category(db: Session, category: CategoryCreate):
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category: CategoryUpdate):
    db_category = db.get(Category, category_id)
    if not db_category:
        return None
    update_data = category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int):
    db_category = db.get(Category, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(Product).offset(skip).limit(limit)).all()


def get_product(db: Session, product_id: int):
    return db.get(Product, product_id)


def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: ProductUpdate):
    db_product = db.get(Product, product_id)
    if not db_product:
        return None
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    db_product = db.get(Product, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False


def get_low_stock_products(db: Session):
    """
    Get products with low stock (calls stock logic)
    """
    from .stock import get_low_stock_products
    return get_low_stock_products(db)
