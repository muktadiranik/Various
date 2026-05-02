from sqlalchemy.orm import Session
from sqlalchemy import select
import models
import schemas
from typing import List

# Category CRUD


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[models.Category]:
    return db.execute(select(models.Category).offset(skip).limit(limit)).scalars().all()


def get_category(db: Session, category_id: int):
    return db.get(models.Category, category_id)


def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category: schemas.CategoryUpdate):
    db_category = db.get(models.Category, category_id)
    if not db_category:
        return None
    update_data = category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int):
    db_category = db.get(models.Category, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False

# Item CRUD


def get_items(db: Session, skip: int = 0, limit: int = 100) -> List[models.Item]:
    return db.execute(select(models.Item).offset(skip).limit(limit)).scalars().all()


def get_item(db: Session, item_id: int):
    return db.get(models.Item, item_id)


def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, item: schemas.ItemUpdate):
    db_item = db.get(models.Item, item_id)
    if not db_item:
        return None
    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int):
    db_item = db.get(models.Item, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False
