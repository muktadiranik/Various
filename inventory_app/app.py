# app.py - Complete Fixed Inventory System API with Proper Connection Management
from fastapi import FastAPI, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import io
import csv
from contextlib import asynccontextmanager

# Database Setup with Proper Connection Pooling
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Association Tables
product_tag_links = Table(
    "product_tag_links",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

product_category_links = Table(
    "product_category_links",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True)
)

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    role = relationship("Role", back_populates="users")
    activity_logs = relationship("ActivityLog", back_populates="user")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    permissions = Column(JSON)
    users = relationship("User", back_populates="role")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String)
    timestamp = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="activity_logs")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    level = Column(Integer, default=0)
    path = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", secondary="product_category_links", back_populates="categories")

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

class UnitOfMeasure(Base):
    __tablename__ = "units_of_measure"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    code = Column(String, unique=True)
    type = Column(String)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    products = relationship("Product", secondary="product_tag_links", back_populates="tags")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units_of_measure.id"))
    barcode = Column(String, unique=True, nullable=True)
    qr_code = Column(String, unique=True, nullable=True)
    weight = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    is_bundle = Column(Boolean, default=False)
    has_serial_tracking = Column(Boolean, default=False)
    has_batch_tracking = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    brand = relationship("Brand")
    unit = relationship("UnitOfMeasure")
    variants = relationship("ProductVariant", back_populates="product")
    tags = relationship("Tag", secondary="product_tag_links", back_populates="products")
    categories = relationship("Category", secondary="product_category_links", back_populates="products")
    images = relationship("ProductImage", back_populates="product")
    bundle_components = relationship("BundleComponent", foreign_keys="BundleComponent.parent_product_id", back_populates="parent_product")
    batches = relationship("Batch", back_populates="product")

class ProductVariant(Base):
    __tablename__ = "product_variants"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    sku = Column(String, unique=True, index=True)
    attributes = Column(JSON)
    price_adjustment = Column(Float, default=0)
    created_at = Column(DateTime, default=func.now())
    
    product = relationship("Product", back_populates="variants")

class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    image_url = Column(String)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    
    product = relationship("Product", back_populates="images")

class BundleComponent(Base):
    __tablename__ = "bundle_components"
    id = Column(Integer, primary_key=True, index=True)
    parent_product_id = Column(Integer, ForeignKey("products.id"))
    component_product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float)
    
    parent_product = relationship("Product", foreign_keys=[parent_product_id], back_populates="bundle_components")
    component_product = relationship("Product", foreign_keys=[component_product_id])

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    code = Column(String, unique=True)
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    locations = relationship("WarehouseLocation", back_populates="warehouse")
    stock = relationship("Stock", back_populates="warehouse")

class WarehouseLocation(Base):
    __tablename__ = "warehouse_locations"
    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    zone = Column(String)
    rack = Column(String)
    bin = Column(String)
    barcode = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    
    warehouse = relationship("Warehouse", back_populates="locations")

class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    batch_number = Column(String, index=True)
    manufacturing_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    quantity = Column(Float)
    created_at = Column(DateTime, default=func.now())
    
    product = relationship("Product", back_populates="batches")
    stock = relationship("Stock", back_populates="batch")

class Stock(Base):
    __tablename__ = "stock"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    location_id = Column(Integer, ForeignKey("warehouse_locations.id"), nullable=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    serial_number = Column(String, nullable=True)
    quantity = Column(Float, default=0)
    reserved_quantity = Column(Float, default=0)
    min_stock = Column(Float, default=0)
    max_stock = Column(Float, default=0)
    safety_stock = Column(Float, default=0)
    reorder_point = Column(Float, default=0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    product = relationship("Product")
    warehouse = relationship("Warehouse", back_populates="stock")
    location = relationship("WarehouseLocation")
    batch = relationship("Batch", back_populates="stock")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, unique=True)
    contact_person = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    tax_number = Column(String, nullable=True)
    payment_terms = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    order_date = Column(DateTime, default=func.now())
    expected_delivery = Column(DateTime, nullable=True)
    status = Column(String, default="draft")
    subtotal = Column(Float, default=0)
    tax = Column(Float, default=0)
    discount = Column(Float, default=0)
    total = Column(Float, default=0)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    
    supplier = relationship("Supplier")
    warehouse = relationship("Warehouse")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float)
    received_quantity = Column(Float, default=0)
    unit_price = Column(Float)
    total = Column(Float)
    
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")

class GoodsReceivedNote(Base):
    __tablename__ = "goods_received_notes"
    id = Column(Integer, primary_key=True, index=True)
    grn_number = Column(String, unique=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    received_date = Column(DateTime, default=func.now())
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    status = Column(String, default="pending")
    created_by = Column(Integer, ForeignKey("users.id"))
    
    purchase_order = relationship("PurchaseOrder")
    warehouse = relationship("Warehouse")
    items = relationship("GRNItem", back_populates="grn")

class GRNItem(Base):
    __tablename__ = "grn_items"
    id = Column(Integer, primary_key=True, index=True)
    grn_id = Column(Integer, ForeignKey("goods_received_notes.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    po_item_id = Column(Integer, ForeignKey("purchase_order_items.id"))
    quantity_received = Column(Float)
    batch_number = Column(String, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    location_id = Column(Integer, ForeignKey("warehouse_locations.id"), nullable=True)
    
    grn = relationship("GoodsReceivedNote", back_populates="items")
    product = relationship("Product")
    location = relationship("WarehouseLocation")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    tax_number = Column(String, nullable=True)
    price_tier = Column(String, default="retail")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class SalesOrder(Base):
    __tablename__ = "sales_orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    order_date = Column(DateTime, default=func.now())
    status = Column(String, default="pending")
    subtotal = Column(Float, default=0)
    tax = Column(Float, default=0)
    discount = Column(Float, default=0)
    shipping_charge = Column(Float, default=0)
    total = Column(Float, default=0)
    shipping_address = Column(Text)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    
    warehouse = relationship("Warehouse")
    customer = relationship("Customer")
    items = relationship("SalesOrderItem", back_populates="sales_order")

class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float)
    shipped_quantity = Column(Float, default=0)
    unit_price = Column(Float)
    discount = Column(Float, default=0)
    total = Column(Float)
    
    sales_order = relationship("SalesOrder", back_populates="items")
    product = relationship("Product")

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    id = Column(Integer, primary_key=True, index=True)
    movement_type = Column(String)
    reference_type = Column(String)
    reference_id = Column(Integer)
    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    location_id = Column(Integer, ForeignKey("warehouse_locations.id"), nullable=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    serial_number = Column(String, nullable=True)
    quantity_before = Column(Float)
    quantity_change = Column(Float)
    quantity_after = Column(Float)
    cost_per_unit = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    
    product = relationship("Product")
    warehouse = relationship("Warehouse")
    location = relationship("WarehouseLocation")
    batch = relationship("Batch")

class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"
    id = Column(Integer, primary_key=True, index=True)
    adjustment_number = Column(String, unique=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    adjustment_type = Column(String)
    quantity = Column(Float)
    reason = Column(Text)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    approved_at = Column(DateTime, nullable=True)

class TransferOrder(Base):
    __tablename__ = "transfer_orders"
    id = Column(Integer, primary_key=True, index=True)
    transfer_number = Column(String, unique=True)
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float)
    status = Column(String, default="pending")
    requested_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

# Pydantic Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role_id: int

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    brand_id: Optional[int] = None
    unit_id: int
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    weight: Optional[float] = None
    volume: Optional[float] = None
    is_bundle: bool = False
    has_serial_tracking: bool = False
    has_batch_tracking: bool = False
    category_ids: Optional[List[int]] = []
    tag_names: Optional[List[str]] = []
    variants: Optional[List[Dict[str, Any]]] = []

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str]
    brand_id: Optional[int]
    unit_id: int
    barcode: Optional[str]
    qr_code: Optional[str]
    is_bundle: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class StockResponse(BaseModel):
    product_id: int
    product_name: str
    sku: str
    warehouse_id: int
    warehouse_name: str
    quantity: float
    reserved_quantity: float
    available_quantity: float
    min_stock: float
    max_stock: float
    reorder_point: float

class StockUpdate(BaseModel):
    quantity: Optional[float] = None
    reserved_quantity: Optional[float] = None
    min_stock: Optional[float] = None
    max_stock: Optional[float] = None
    reorder_point: Optional[float] = None

class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    warehouse_id: int
    expected_delivery: datetime
    items: List[Dict[str, Any]]
    notes: Optional[str] = None

class SalesOrderCreate(BaseModel):
    customer_id: int
    warehouse_id: int
    items: List[Dict[str, Any]]
    shipping_address: str
    notes: Optional[str] = None

class TransferOrderCreate(BaseModel):
    from_warehouse_id: int
    to_warehouse_id: int
    product_id: int
    quantity: float

class StockAdjustmentCreate(BaseModel):
    product_id: int
    warehouse_id: int
    adjustment_type: str
    quantity: float
    reason: str

class WarehouseCreate(BaseModel):
    name: str
    code: str
    address: str

class SupplierCreate(BaseModel):
    name: str
    code: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    payment_terms: int = 30

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    price_tier: str = "retail"

# Database Dependency - CRITICAL FIX
def get_db():
    """Dependency that provides a database session and ensures it's closed"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def check_permission(current_user: User, required_permission: str, db: Session):
    role = db.query(Role).filter(Role.id == current_user.role_id).first()
    if not role or (required_permission not in role.permissions and "*" not in role.permissions):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return True

# FastAPI App with Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(Role).first():
            admin_role = Role(name="admin", permissions=["*"])
            manager_role = Role(name="manager", permissions=["read", "create", "update", "delete"])
            staff_role = Role(name="staff", permissions=["read", "create", "update"])
            viewer_role = Role(name="viewer", permissions=["read"])
            db.add_all([admin_role, manager_role, staff_role, viewer_role])
            db.commit()
            
            if not db.query(User).first():
                hashed_pwd = get_password_hash("admin123")
                admin_user = User(username="admin", email="admin@example.com", hashed_password=hashed_pwd, role_id=admin_role.id)
                db.add(admin_user)
                db.commit()
                
            # Seed default units
            if not db.query(UnitOfMeasure).first():
                units = [
                    UnitOfMeasure(name="Piece", code="PCS", type="quantity"),
                    UnitOfMeasure(name="Kilogram", code="KG", type="weight"),
                    UnitOfMeasure(name="Liter", code="LTR", type="volume"),
                    UnitOfMeasure(name="Box", code="BOX", type="quantity"),
                    UnitOfMeasure(name="Meter", code="M", type="length")
                ]
                db.add_all(units)
                db.commit()
    finally:
        db.close()
    yield

app = FastAPI(title="Inventory System API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth endpoints
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pwd = get_password_hash(user_data.password)
    db_user = User(username=user_data.username, email=user_data.email, hashed_password=hashed_pwd, role_id=user_data.role_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "read", db)
    return db.query(User).offset(skip).limit(limit).all()

# Product endpoints
@app.post("/products", response_model=ProductResponse)
async def create_product(product: ProductCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    
    existing = db.query(Product).filter(Product.sku == product.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    db_product = Product(
        sku=product.sku,
        name=product.name,
        description=product.description,
        brand_id=product.brand_id,
        unit_id=product.unit_id,
        barcode=product.barcode,
        qr_code=product.qr_code,
        weight=product.weight,
        volume=product.volume,
        is_bundle=product.is_bundle,
        has_serial_tracking=product.has_serial_tracking,
        has_batch_tracking=product.has_batch_tracking
    )
    db.add(db_product)
    db.flush()
    
    if product.category_ids:
        categories = db.query(Category).filter(Category.id.in_(product.category_ids)).all()
        db_product.categories = categories
    
    if product.tag_names:
        for tag_name in product.tag_names:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush()
            if tag not in db_product.tags:
                db_product.tags.append(tag)
    
    if product.variants:
        for variant_data in product.variants:
            variant = ProductVariant(
                product_id=db_product.id,
                sku=variant_data.get('sku', f"{product.sku}-{variant_data.get('attributes', {}).get('color', 'VAR')}"),
                attributes=variant_data.get('attributes', {}),
                price_adjustment=variant_data.get('price_adjustment', 0)
            )
            db.add(variant)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products", response_model=List[ProductResponse])
async def list_products(skip: int = 0, limit: int = 100, search: Optional[str] = None, category_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Product)
    if search:
        query = query.filter(Product.name.contains(search) | Product.sku.contains(search) | Product.description.contains(search))
    if category_id:
        query = query.join(Product.categories).filter(Category.id == category_id)
    return query.offset(skip).limit(limit).all()

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "update", db)
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product.sku = product.sku
    db_product.name = product.name
    db_product.description = product.description
    db_product.brand_id = product.brand_id
    db_product.unit_id = product.unit_id
    db_product.barcode = product.barcode
    db_product.qr_code = product.qr_code
    db_product.weight = product.weight
    db_product.volume = product.volume
    db_product.is_bundle = product.is_bundle
    
    if product.category_ids:
        categories = db.query(Category).filter(Category.id.in_(product.category_ids)).all()
        db_product.categories = categories
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
async def delete_product(product_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "delete", db)
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}

# Stock endpoints
@app.get("/stock", response_model=List[StockResponse])
async def get_stock(warehouse_id: Optional[int] = None, product_id: Optional[int] = None, low_stock_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(Stock).join(Product).join(Warehouse)
    if warehouse_id:
        query = query.filter(Stock.warehouse_id == warehouse_id)
    if product_id:
        query = query.filter(Stock.product_id == product_id)
    if low_stock_only:
        query = query.filter(Stock.quantity <= Stock.reorder_point)
    
    results = []
    for stock in query.all():
        results.append(StockResponse(
            product_id=stock.product_id,
            product_name=stock.product.name,
            sku=stock.product.sku,
            warehouse_id=stock.warehouse_id,
            warehouse_name=stock.warehouse.name,
            quantity=stock.quantity,
            reserved_quantity=stock.reserved_quantity,
            available_quantity=stock.quantity - stock.reserved_quantity,
            min_stock=stock.min_stock,
            max_stock=stock.max_stock,
            reorder_point=stock.reorder_point
        ))
    return results

@app.put("/stock/{stock_id}")
async def update_stock(stock_id: int, stock_update: StockUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "update", db)
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    old_quantity = stock.quantity
    for key, value in stock_update.dict(exclude_unset=True).items():
        setattr(stock, key, value)
    
    if stock_update.quantity is not None:
        movement = InventoryMovement(
            movement_type="adjustment",
            reference_type="stock_adjustment",
            product_id=stock.product_id,
            warehouse_id=stock.warehouse_id,
            quantity_before=old_quantity,
            quantity_change=stock_update.quantity - old_quantity,
            quantity_after=stock.quantity,
            notes="Manual stock adjustment",
            created_by=current_user.id
        )
        db.add(movement)
    
    db.commit()
    return {"message": "Stock updated"}

# Purchase Order endpoints
@app.post("/purchase-orders")
async def create_purchase_order(po: PurchaseOrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    total = 0
    items_data = []
    
    for item in po.items:
        product = db.query(Product).filter(Product.id == item['product_id']).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item['product_id']} not found")
        item_total = item['quantity'] * item['unit_price']
        total += item_total
        items_data.append({
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'unit_price': item['unit_price'],
            'total': item_total
        })
    
    po_number = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    db_po = PurchaseOrder(
        po_number=po_number,
        supplier_id=po.supplier_id,
        warehouse_id=po.warehouse_id,
        expected_delivery=po.expected_delivery,
        status="draft",
        subtotal=total,
        total=total,
        notes=po.notes,
        created_by=current_user.id
    )
    db.add(db_po)
    db.flush()
    
    for item_data in items_data:
        po_item = PurchaseOrderItem(po_id=db_po.id, **item_data)
        db.add(po_item)
    
    db.commit()
    return {"po_id": db_po.id, "po_number": po_number}

@app.get("/purchase-orders")
async def list_purchase_orders(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(PurchaseOrder)
    if status:
        query = query.filter(PurchaseOrder.status == status)
    return query.offset(skip).limit(limit).all()

@app.get("/purchase-orders/{po_id}")
async def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po

@app.post("/purchase-orders/{po_id}/receive")
async def receive_purchase_order(po_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "update", db)
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    grn_number = f"GRN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    grn = GoodsReceivedNote(
        grn_number=grn_number,
        po_id=po_id,
        warehouse_id=po.warehouse_id,
        status="completed",
        created_by=current_user.id
    )
    db.add(grn)
    db.flush()
    
    for po_item in po.items:
        stock = db.query(Stock).filter(
            Stock.product_id == po_item.product_id,
            Stock.warehouse_id == po.warehouse_id
        ).first()
        
        if not stock:
            stock = Stock(
                product_id=po_item.product_id,
                warehouse_id=po.warehouse_id,
                quantity=0,
                reserved_quantity=0,
                min_stock=5,
                reorder_point=10
            )
            db.add(stock)
            db.flush()
        
        old_quantity = stock.quantity
        stock.quantity += po_item.quantity
        
        movement = InventoryMovement(
            movement_type="purchase_receipt",
            reference_type="purchase_order",
            reference_id=po_id,
            product_id=po_item.product_id,
            warehouse_id=po.warehouse_id,
            quantity_before=old_quantity,
            quantity_change=po_item.quantity,
            quantity_after=stock.quantity,
            cost_per_unit=po_item.unit_price,
            created_by=current_user.id
        )
        db.add(movement)
        
        grn_item = GRNItem(
            grn_id=grn.id,
            product_id=po_item.product_id,
            po_item_id=po_item.id,
            quantity_received=po_item.quantity
        )
        db.add(grn_item)
        
        po_item.received_quantity = po_item.quantity
    
    po.status = "received"
    db.commit()
    
    return {"grn_number": grn_number, "message": "Goods received successfully"}

# Sales Order endpoints
@app.post("/sales-orders")
async def create_sales_order(so: SalesOrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    total = 0
    items_data = []
    
    for item in so.items:
        stock = db.query(Stock).filter(
            Stock.product_id == item['product_id'],
            Stock.warehouse_id == so.warehouse_id
        ).first()
        
        if not stock or stock.quantity - stock.reserved_quantity < item['quantity']:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item['product_id']}")
        
        item_total = item['quantity'] * item['unit_price'] - item.get('discount', 0)
        total += item_total
        items_data.append({
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'unit_price': item['unit_price'],
            'discount': item.get('discount', 0),
            'total': item_total
        })
        
        stock.reserved_quantity += item['quantity']
    
    order_number = f"SO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    db_so = SalesOrder(
        order_number=order_number,
        customer_id=so.customer_id,
        warehouse_id=so.warehouse_id,
        status="pending",
        subtotal=total,
        total=total,
        shipping_address=so.shipping_address,
        notes=so.notes,
        created_by=current_user.id
    )
    db.add(db_so)
    db.flush()
    
    for item_data in items_data:
        so_item = SalesOrderItem(order_id=db_so.id, **item_data)
        db.add(so_item)
    
    db.commit()
    return {"order_id": db_so.id, "order_number": order_number}

@app.get("/sales-orders")
async def list_sales_orders(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(SalesOrder)
    if status:
        query = query.filter(SalesOrder.status == status)
    return query.offset(skip).limit(limit).all()

@app.post("/sales-orders/{order_id}/dispatch")
async def dispatch_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "update", db)
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")
    
    for item in order.items:
        stock = db.query(Stock).filter(
            Stock.product_id == item.product_id,
            Stock.warehouse_id == order.warehouse_id
        ).first()
        
        if not stock:
            raise HTTPException(status_code=400, detail=f"No stock found for product {item.product_id}")
        
        old_quantity = stock.quantity
        stock.quantity -= item.quantity
        stock.reserved_quantity -= item.quantity
        
        movement = InventoryMovement(
            movement_type="sales_dispatch",
            reference_type="sales_order",
            reference_id=order_id,
            product_id=item.product_id,
            warehouse_id=order.warehouse_id,
            quantity_before=old_quantity,
            quantity_change=-item.quantity,
            quantity_after=stock.quantity,
            created_by=current_user.id
        )
        db.add(movement)
        
        item.shipped_quantity = item.quantity
    
    order.status = "shipped"
    db.commit()
    
    return {"message": "Order dispatched successfully"}

# Transfer Order endpoints
@app.post("/transfer-orders")
async def create_transfer_order(transfer: TransferOrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    
    from_stock = db.query(Stock).filter(
        Stock.product_id == transfer.product_id,
        Stock.warehouse_id == transfer.from_warehouse_id
    ).first()
    
    if not from_stock or from_stock.quantity - from_stock.reserved_quantity < transfer.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock in source warehouse")
    
    transfer_number = f"TR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    db_transfer = TransferOrder(
        transfer_number=transfer_number,
        from_warehouse_id=transfer.from_warehouse_id,
        to_warehouse_id=transfer.to_warehouse_id,
        product_id=transfer.product_id,
        quantity=transfer.quantity,
        status="pending",
        requested_by=current_user.id
    )
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    
    return {"transfer_id": db_transfer.id, "transfer_number": transfer_number}

@app.get("/transfer-orders")
async def list_transfer_orders(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(TransferOrder)
    if status:
        query = query.filter(TransferOrder.status == status)
    return query.offset(skip).limit(limit).all()

@app.post("/transfer-orders/{transfer_id}/complete")
async def complete_transfer(transfer_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "update", db)
    transfer = db.query(TransferOrder).filter(TransferOrder.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer order not found")
    
    from_stock = db.query(Stock).filter(
        Stock.product_id == transfer.product_id,
        Stock.warehouse_id == transfer.from_warehouse_id
    ).first()
    
    to_stock = db.query(Stock).filter(
        Stock.product_id == transfer.product_id,
        Stock.warehouse_id == transfer.to_warehouse_id
    ).first()
    
    if not to_stock:
        to_stock = Stock(
            product_id=transfer.product_id,
            warehouse_id=transfer.to_warehouse_id,
            quantity=0,
            reserved_quantity=0,
            min_stock=5,
            reorder_point=10
        )
        db.add(to_stock)
        db.flush()
    
    old_from_qty = from_stock.quantity
    old_to_qty = to_stock.quantity
    
    from_stock.quantity -= transfer.quantity
    to_stock.quantity += transfer.quantity
    
    movement_out = InventoryMovement(
        movement_type="transfer_out",
        reference_type="transfer_order",
        reference_id=transfer_id,
        product_id=transfer.product_id,
        warehouse_id=transfer.from_warehouse_id,
        quantity_before=old_from_qty,
        quantity_change=-transfer.quantity,
        quantity_after=from_stock.quantity,
        created_by=current_user.id
    )
    
    movement_in = InventoryMovement(
        movement_type="transfer_in",
        reference_type="transfer_order",
        reference_id=transfer_id,
        product_id=transfer.product_id,
        warehouse_id=transfer.to_warehouse_id,
        quantity_before=old_to_qty,
        quantity_change=transfer.quantity,
        quantity_after=to_stock.quantity,
        created_by=current_user.id
    )
    
    db.add_all([movement_out, movement_in])
    transfer.status = "completed"
    transfer.completed_at = datetime.now()
    
    db.commit()
    
    return {"message": "Transfer completed successfully"}

# Stock Adjustment endpoints
@app.post("/stock-adjustments")
async def create_stock_adjustment(adjustment: StockAdjustmentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "update", db)
    
    stock = db.query(Stock).filter(
        Stock.product_id == adjustment.product_id,
        Stock.warehouse_id == adjustment.warehouse_id
    ).first()
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock record not found")
    
    adjustment_number = f"ADJ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    db_adjustment = StockAdjustment(
        adjustment_number=adjustment_number,
        product_id=adjustment.product_id,
        warehouse_id=adjustment.warehouse_id,
        adjustment_type=adjustment.adjustment_type,
        quantity=adjustment.quantity,
        reason=adjustment.reason,
        created_by=current_user.id,
        approved_by=current_user.id,
        approved_at=datetime.now()
    )
    db.add(db_adjustment)
    
    old_quantity = stock.quantity
    if adjustment.adjustment_type == "increase":
        stock.quantity += adjustment.quantity
    else:
        stock.quantity -= adjustment.quantity
    
    movement = InventoryMovement(
        movement_type="adjustment",
        reference_type="stock_adjustment",
        reference_id=db_adjustment.id,
        product_id=adjustment.product_id,
        warehouse_id=adjustment.warehouse_id,
        quantity_before=old_quantity,
        quantity_change=adjustment.quantity if adjustment.adjustment_type == "increase" else -adjustment.quantity,
        quantity_after=stock.quantity,
        notes=adjustment.reason,
        created_by=current_user.id
    )
    db.add(movement)
    
    db.commit()
    
    return {"adjustment_number": adjustment_number, "message": "Stock adjustment completed"}

# Warehouse endpoints
@app.post("/warehouses")
async def create_warehouse(warehouse: WarehouseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    db_warehouse = Warehouse(**warehouse.dict())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse

@app.get("/warehouses")
async def list_warehouses(db: Session = Depends(get_db)):
    return db.query(Warehouse).all()

@app.get("/warehouses/{warehouse_id}")
async def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse

@app.post("/warehouses/{warehouse_id}/locations")
async def add_warehouse_location(warehouse_id: int, zone: str, rack: str, bin: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    barcode = f"{zone}-{rack}-{bin}"
    location = WarehouseLocation(
        warehouse_id=warehouse_id,
        zone=zone,
        rack=rack,
        bin=bin,
        barcode=barcode
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

# Supplier endpoints
@app.post("/suppliers")
async def create_supplier(supplier: SupplierCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    db_supplier = Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@app.get("/suppliers")
async def list_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Supplier).offset(skip).limit(limit).all()

@app.get("/suppliers/{supplier_id}")
async def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

# Customer endpoints
@app.post("/customers")
async def create_customer(customer: CustomerCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.get("/customers")
async def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Customer).offset(skip).limit(limit).all()

# Category endpoints
@app.post("/categories")
async def create_category(name: str, parent_id: Optional[int] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    
    level = 0
    path = name
    
    if parent_id:
        parent = db.query(Category).filter(Category.id == parent_id).first()
        if parent:
            level = parent.level + 1
            path = f"{parent.path}/{name}"
    
    category = Category(name=name, parent_id=parent_id, level=level, path=path)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@app.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

# Reports endpoints
@app.get("/reports/stock-levels")
async def stock_levels_report(warehouse_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Stock).join(Product).join(Warehouse)
    if warehouse_id:
        query = query.filter(Stock.warehouse_id == warehouse_id)
    
    results = []
    for stock in query.all():
        results.append({
            "product_name": stock.product.name,
            "sku": stock.product.sku,
            "warehouse": stock.warehouse.name,
            "quantity": stock.quantity,
            "reserved": stock.reserved_quantity,
            "available": stock.quantity - stock.reserved_quantity,
            "reorder_point": stock.reorder_point,
            "status": "Low Stock" if stock.quantity <= stock.reorder_point else "Normal"
        })
    return results

@app.get("/reports/low-stock")
async def low_stock_report(db: Session = Depends(get_db)):
    low_stock_items = db.query(Stock).filter(Stock.quantity <= Stock.reorder_point).all()
    results = []
    for item in low_stock_items:
        results.append({
            "product_id": item.product_id,
            "product_name": item.product.name,
            "sku": item.product.sku,
            "current_stock": item.quantity,
            "reorder_point": item.reorder_point,
            "shortage": item.reorder_point - item.quantity if item.quantity < item.reorder_point else 0,
            "warehouse": item.warehouse.name
        })
    return results

@app.get("/reports/inventory-movements")
async def inventory_movements_report(start_date: datetime, end_date: datetime, product_id: Optional[int] = None, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(InventoryMovement).filter(
        InventoryMovement.created_at.between(start_date, end_date)
    )
    if product_id:
        query = query.filter(InventoryMovement.product_id == product_id)
    
    return query.order_by(InventoryMovement.created_at.desc()).limit(limit).all()

# Activity Logs
@app.get("/activity-logs")
async def get_activity_logs(skip: int = 0, limit: int = 100, user_id: Optional[int] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "read", db)
    query = db.query(ActivityLog)
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    return query.order_by(ActivityLog.timestamp.desc()).offset(skip).limit(limit).all()

# Bulk Import/Export
@app.post("/bulk/import/products")
async def bulk_import_products(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    contents = await file.read()
    csv_data = csv.DictReader(io.StringIO(contents.decode('utf-8')))
    
    created = 0
    for row in csv_data:
        product = Product(
            sku=row['sku'],
            name=row['name'],
            description=row.get('description', ''),
            unit_id=int(row.get('unit_id', 1)),
            barcode=row.get('barcode'),
            weight=float(row['weight']) if row.get('weight') else None
        )
        db.add(product)
        created += 1
    
    db.commit()
    return {"message": f"Imported {created} products"}

@app.get("/bulk/export/products")
async def bulk_export_products(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "read", db)
    products = db.query(Product).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'sku', 'name', 'description', 'brand_id', 'unit_id', 'barcode', 'weight', 'created_at'])
    
    for product in products:
        writer.writerow([
            product.id, product.sku, product.name, product.description,
            product.brand_id, product.unit_id, product.barcode,
            product.weight, product.created_at
        ])
    
    return Response(
        content=output.getvalue().encode(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products_export.csv"}
    )

# Search endpoint
@app.get("/search")
async def advanced_search(q: str, category_id: Optional[int] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, db: Session = Depends(get_db)):
    query = db.query(Product)
    
    if q:
        query = query.filter(
            Product.name.contains(q) | 
            Product.sku.contains(q) | 
            Product.description.contains(q) |
            Product.barcode.contains(q)
        )
    
    if category_id:
        query = query.join(Product.categories).filter(Category.id == category_id)
    
    return query.limit(50).all()

# Dashboard stats endpoint
@app.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    total_products = db.query(Product).count()
    low_stock = db.query(Stock).filter(Stock.quantity <= Stock.reorder_point).count()
    pending_purchase_orders = db.query(PurchaseOrder).filter(PurchaseOrder.status == "draft").count()
    pending_sales_orders = db.query(SalesOrder).filter(SalesOrder.status == "pending").count()
    
    return {
        "total_products": total_products,
        "low_stock_alerts": low_stock,
        "pending_purchase_orders": pending_purchase_orders,
        "pending_sales_orders": pending_sales_orders,
        "total_warehouses": db.query(Warehouse).count(),
        "total_suppliers": db.query(Supplier).count(),
        "total_customers": db.query(Customer).count()
    }

# Units endpoint
@app.get("/units")
async def get_units(db: Session = Depends(get_db)):
    return db.query(UnitOfMeasure).all()

# Brands endpoints
@app.get("/brands")
async def get_brands(db: Session = Depends(get_db)):
    return db.query(Brand).all()

@app.post("/brands")
async def create_brand(name: str, description: str = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await check_permission(current_user, "create", db)
    brand = Brand(name=name, description=description)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)