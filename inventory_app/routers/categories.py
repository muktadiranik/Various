from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from crud import get_categories, get_category, create_category, update_category, delete_category
from schemas import CategoryCreate, CategoryUpdate, CategoryOut
from database import get_db

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryOut])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = get_categories(db, skip=skip, limit=limit)
    return categories


@router.get("/{category_id}", response_model=CategoryOut)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryOut, status_code=201)
def create_new_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db=db, category=category)


@router.put("/{category_id}", response_model=CategoryOut)
def modify_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    updated = update_category(db, category_id, category)
    if updated is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated


@router.delete("/{category_id}", status_code=204)
def remove_category(category_id: int, db: Session = Depends(get_db)):
    success = delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
