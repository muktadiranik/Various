from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models  # Import to create tables
from database import engine
from routers import categories, items

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inventory Management API",
    description="FastAPI app to manage inventory items and categories",
    version="1.0.0"
)

# CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router, prefix="/api/v1", tags=["categories"])
app.include_router(items.router, prefix="/api/v1", tags=["items"])


@app.get("/")
def read_root():
    return {"message": "Inventory API - visit /docs for API docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
