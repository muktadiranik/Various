from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from crud import get_items, get_item, create_item, update_item, delete_item
from schemas import ItemCreate, ItemUpdate, ItemOut
from database import get_db

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=List[ItemOut])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = get_items(db, skip=skip, limit=limit)
    return items


@router.get("/{item_id}", response_model=ItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=ItemOut, status_code=201)
def create_new_item(item: ItemCreate, db: Session = Depends(get_db)):
    return create_item(db=db, item=item)


@router.put("/{item_id}", response_model=ItemOut)
def modify_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    updated = update_item(db, item_id, item)
    if updated is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated


@router.delete("/{item_id}", status_code=204)
def remove_item(item_id: int, db: Session = Depends(get_db)):
    success = delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
