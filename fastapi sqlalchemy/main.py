import os
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, MetaData, Table
from sqlalchemy import create_engine
from fastapi import FastAPI
from sqlalchemy.orm import Session

app = FastAPI()

# Define the database connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "test.db")

engine = create_engine(f"sqlite:///{DB_PATH}")

# Define the database schema


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    products: Mapped[List["Product"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r}, description={self.description!r})"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped[Category] = relationship(back_populates="products")

    def _repr__(self) -> str:
        return f"Product(id={self.id!r}, name={self.name!r}, description={self.description!r}, category_id={self.category_id!r})"


Base.metadata.create_all(engine)


# Define the models


class CategoryOut(BaseModel):
    id: int | None
    name: str | None
    description: str | None
    products: list["ProductOut"] | None

    model_config = ConfigDict(from_attributes=True)


class ProductOut(BaseModel):
    id: int | None
    name: str | None
    description: str | None
    category_id: int | None

    model_config = ConfigDict(from_attributes=True)


# Define the routes

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/categories")
async def get_all_categories():
    with Session(engine) as session:
        categories = session.query(Category).all()
        return categories


@app.get("/categories/{category_id}")
async def get_category(category_id: int):
    with Session(engine) as session:
        category = session.query(
            Category
        ).options(
            selectinload(Category.products)
        ).filter(Category.id == category_id).first()

        return CategoryOut.model_validate(category)


@app.get("/products")
async def get_all_products():
    with Session(engine) as session:
        products = session.query(Product).all()
        return products


@app.get("/products/{product_id}")
async def get_product(product_id: int):
    with Session(engine) as session:
        product = session.query(Product).get(product_id)
        return product


# Run the app
"""
    if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
"""
