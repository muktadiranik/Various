from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models.batch import Batch
from ..schemas.batch import BatchCreate


def get_batches(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(Batch).offset(skip).limit(limit)).all()


def get_batch(db: Session, batch_id: int):
    return db.get(Batch, batch_id)


def create_batch(db: Session, batch: BatchCreate):
    db_batch = Batch(**batch.model_dump())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def update_batch(db: Session, batch_id: int, batch: BatchCreate):
    db_batch = db.get(Batch, batch_id)
    if not db_batch:
        return None
    update_data = batch.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_batch, field, value)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def delete_batch(db: Session, batch_id: int):
    db_batch = db.get(Batch, batch_id)
    if db_batch:
        db.delete(db_batch)
        db.commit()
        return True
    return False
