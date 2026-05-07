from .routers import auth, products, warehouses, stock, procurement, sales, batches, reports
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from .database import engine, Base, SessionLocal, get_db
from .core.config import settings
from .models.product import *
from .models.warehouse import *
from .models.stock import *
from .models.user import *
from .models.procurement import *
from .models.sales import *
from .models.batch import *
from .models.storage_location import *

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inventory Management API",
    description="Full-featured inventory system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Inventory API v1.0 - /docs for API"}


app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(warehouses.router, prefix="/api/v1", tags=["warehouses"])
app.include_router(stock.router, prefix="/api/v1", tags=["stock"])
app.include_router(procurement.router, prefix="/api/v1", tags=["procurement"])
app.include_router(sales.router, prefix="/api/v1", tags=["sales"])
app.include_router(batches.router, prefix="/api/v1", tags=["batches"])
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
