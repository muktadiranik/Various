from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..crud.product import (get_categories, get_category, create_category, update_category, delete_category,
                            get_products, get_product, create_product, update_product, delete_product)
from ..schemas.product import (
    CategoryCreate, CategoryUpdate, CategoryOut, ProductCreate, ProductUpdate, ProductOut)
from ..database import get_db
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/categories", response_model=List[CategoryOut])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = get_categories(db, skip=skip, limit=limit)
    return categories


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_new_category(category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_category(db, category)

# Add other CRUD operations...


@router.get("/", response_model=List[ProductOut])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = get_products(db, skip=skip, limit=limit)
    return products


@router.post("/", response_model=ProductOut, status_code=201)
def create_new_product(product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_product(db, product)

# Similar for update/delete...
