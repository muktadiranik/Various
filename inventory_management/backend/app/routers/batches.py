from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..crud.batch import get_batches, get_batch, create_batch, update_batch, delete_batch
from ..schemas.batch import BatchCreate, BatchOut
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(prefix="/batches", tags=["batches"])


@router.get("/", response_model=List[BatchOut])
def read_batches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    batches = get_batches(db, skip=skip, limit=limit)
    return batches


@router.post("/", response_model=BatchOut, status_code=201)
def create_new_batch(batch: BatchCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_batch(db, batch)


@router.put("/{batch_id}", response_model=BatchOut)
def modify_batch(batch_id: int, batch: BatchCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = update_batch(db, batch_id, batch)
    if updated is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return updated


@router.delete("/{batch_id}", status_code=204)
def remove_batch(batch_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    success = delete_batch(db, batch_id)
    if not success:
        raise HTTPException(status_code=404, detail="Batch not found")
