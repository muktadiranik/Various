# Full-Featured Inventory Management System

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (SQLite), Redis (caching)
- **Frontend**: React.js, Redux Toolkit, Tailwind CSS
- **Key Features**: Products, Warehouses, Stock Movements, PO/Sales, Valuation, Reports, Auth/Roles

## Setup

1. Backend:
   ```
   cd backend
   python -m venv venv
   venv\\Scripts\\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
2. Redis: Run locally (download Redis for Windows or Docker)
3. Frontend:
   ```
   cd frontend
   npm install
   npm run dev
   ```
4. API Docs: http://localhost:8000/docs

## Features Implemented

- Product CRUD (SKU, variants, barcode, UOM, tags)
- Warehouse & multi-location
- Stock tracking (available/reserved/status)
- Movements (in/out/transfer/adjust/audit log)
- Procurement (PO, suppliers, receiving)
- Sales (orders, reserve/deduct, returns)
- Stock valuation (FIFO/LIFO/weighted avg)
- Reorder alerts
- Batch/lot/expiry/serial tracking
- User auth/roles
- Reports & analytics
- Responsive React UI
