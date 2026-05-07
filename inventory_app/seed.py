# seed_via_api.py - Final Optimized Version
import requests
import json
import time
from datetime import datetime, timedelta

# API Configuration
API_BASE_URL = "http://localhost:8000"
TOKEN = None


def login():
    """Login and get authentication token"""
    global TOKEN
    response = requests.post(
        f"{API_BASE_URL}/token",
        data={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        TOKEN = response.json()["access_token"]
        print("✓ Logged in successfully")
        return True
    else:
        print(f"✗ Login failed: {response.text}")
        return False


def get_headers():
    """Get request headers with authentication"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }


def create_category(name, parent_id=None):
    """Create a category - using query parameters"""
    url = f"{API_BASE_URL}/categories?name={name}"
    if parent_id:
        url += f"&parent_id={parent_id}"
    
    response = requests.post(url, headers={"Authorization": f"Bearer {TOKEN}"})
    if response.status_code == 200:
        print(f"  ✓ Created category: {name}")
        return response.json()
    else:
        print(f"  ✗ Failed to create category {name}: {response.text}")
        return None


def create_product(product_data):
    """Create a product"""
    response = requests.post(
        f"{API_BASE_URL}/products",
        json=product_data,
        headers=get_headers()
    )
    if response.status_code == 200:
        print(f"  ✓ Created product: {product_data['name']}")
        return response.json()
    else:
        print(f"  ✗ Failed to create product {product_data['name']}: {response.text}")
        return None


def create_warehouse(name, code, address):
    """Create a warehouse"""
    data = {"name": name, "code": code, "address": address}
    response = requests.post(
        f"{API_BASE_URL}/warehouses",
        json=data,
        headers=get_headers()
    )
    if response.status_code == 200:
        print(f"  ✓ Created warehouse: {name}")
        return response.json()
    else:
        print(f"  ✗ Failed to create warehouse {name}: {response.text}")
        return None


def add_warehouse_location(warehouse_id, zone, rack, bin_, warehouse_code):
    """Add a location to warehouse with unique barcode"""
    response = requests.post(
        f"{API_BASE_URL}/warehouses/{warehouse_id}/locations",
        params={"zone": zone, "rack": rack, "bin": bin_},
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    if response.status_code == 200:
        print(f"  ✓ Added location: {zone}-{rack}-{bin_}")
        return response.json()
    else:
        # If duplicate, skip silently (location already exists)
        return None


def create_supplier(supplier_data):
    """Create a supplier"""
    response = requests.post(
        f"{API_BASE_URL}/suppliers",
        json=supplier_data,
        headers=get_headers()
    )
    if response.status_code == 200:
        print(f"  ✓ Created supplier: {supplier_data['name']}")
        return response.json()
    else:
        print(f"  ✗ Failed to create supplier: {response.text}")
        return None


def create_customer(customer_data):
    """Create a customer"""
    response = requests.post(
        f"{API_BASE_URL}/customers",
        json=customer_data,
        headers=get_headers()
    )
    if response.status_code == 200:
        print(f"  ✓ Created customer: {customer_data['name']}")
        return response.json()
    else:
        print(f"  ✗ Failed to create customer: {response.text}")
        return None


def create_purchase_order(po_data):
    """Create a purchase order"""
    response = requests.post(
        f"{API_BASE_URL}/purchase-orders",
        json=po_data,
        headers=get_headers()
    )
    if response.status_code == 200:
        print(f"  ✓ Created purchase order")
        return response.json()
    else:
        print(f"  ✗ Failed to create PO: {response.text}")
        return None


def receive_purchase_order(po_id):
    """Receive a purchase order"""
    response = requests.post(
        f"{API_BASE_URL}/purchase-orders/{po_id}/receive",
        headers=get_headers()
    )
    if response.status_code == 200:
        print(f"  ✓ Received purchase order")
        return True
    else:
        print(f"  ✗ Failed to receive PO: {response.text}")
        return False


def create_sales_order(so_data):
    """Create a sales order"""
    response = requests.post(
        f"{API_BASE_URL}/sales-orders",
        json=so_data,
        headers=get_headers()
    )
    if response.status_code == 200:
        print(f"  ✓ Created sales order")
        return response.json()
    else:
        print(f"  ✗ Failed to create SO: {response.text}")
        return None


def dispatch_sales_order(order_id):
    """Dispatch a sales order"""
    response = requests.post(
        f"{API_BASE_URL}/sales-orders/{order_id}/dispatch",
        headers=get_headers()
    )
    if response.status_code == 200:
        print(f"  ✓ Dispatched sales order")
        return True
    else:
        print(f"  ✗ Failed to dispatch SO: {response.text}")
        return False


def create_transfer_order(transfer_data):
    """Create a transfer order"""
    response = requests.post(
        f"{API_BASE_URL}/transfer-orders",
        json=transfer_data,
        headers=get_headers()
    )
    if response.status_code == 200:
        print(f"  ✓ Created transfer order")
        return response.json()
    else:
        print(f"  ✗ Failed to create transfer: {response.text}")
        return None


def complete_transfer(transfer_id):
    """Complete a transfer order"""
    response = requests.post(
        f"{API_BASE_URL}/transfer-orders/{transfer_id}/complete",
        headers=get_headers()
    )
    if response.status_code == 200:
        print(f"  ✓ Completed transfer")
        return True
    else:
        print(f"  ✗ Failed to complete transfer: {response.text}")
        return False


def seed_database():
    """Main seeding function"""
    print("\n" + "="*60)
    print("Starting Database Seeding via API")
    print("="*60 + "\n")

    # Login first
    if not login():
        print("Failed to authenticate. Please make sure the API server is running.")
        return False

    print("\n--- Creating Categories ---")
    electronics = create_category("Electronics")
    # time.sleep(0.1)
    laptops = create_category("Laptops", electronics["id"] if electronics else None)
    # time.sleep(0.1)
    smartphones = create_category("Smartphones", electronics["id"] if electronics else None)
    # time.sleep(0.1)
    accessories = create_category("Accessories", electronics["id"] if electronics else None)
    # time.sleep(0.1)
    clothing = create_category("Clothing")
    # time.sleep(0.1)
    mens = create_category("Men's Clothing", clothing["id"] if clothing else None)
    # time.sleep(0.1)
    womens = create_category("Women's Clothing", clothing["id"] if clothing else None)
    # time.sleep(0.1)
    home_garden = create_category("Home & Garden")
    # time.sleep(0.1)
    furniture = create_category("Furniture", home_garden["id"] if home_garden else None)
    # time.sleep(0.1)
    kitchen = create_category("Kitchen", home_garden["id"] if home_garden else None)

    print("\n--- Creating Products ---")
    products = []
    unit_id = 1

    # Product 1: MacBook Pro
    product1 = create_product({
        "sku": "MBP-001", "name": "MacBook Pro 14",
        "description": "Apple M3 Pro chip, 16GB RAM, 512GB SSD",
        "brand_id": None, "unit_id": unit_id, "barcode": "123456789012",
        "qr_code": "QR001", "weight": 1.6, "volume": None,
        "is_bundle": False, "has_serial_tracking": True, "has_batch_tracking": False,
        "category_ids": [electronics["id"], laptops["id"]] if electronics and laptops else [],
        "tag_names": ["new", "featured", "best-seller"], "variants": []
    })
    if product1:
        products.append(product1)
    # time.sleep(0.2)

    # Product 2: iPhone 13
    product2 = create_product({
        "sku": "IP13-001", "name": "iPhone 13",
        "description": "128GB, 5G capable, A15 Bionic chip",
        "brand_id": None, "unit_id": unit_id, "barcode": "123456789013",
        "qr_code": "QR002", "weight": 0.174, "volume": None,
        "is_bundle": False, "has_serial_tracking": True, "has_batch_tracking": False,
        "category_ids": [electronics["id"], smartphones["id"]] if electronics and smartphones else [],
        "tag_names": ["best-seller", "new"], "variants": []
    })
    if product2:
        products.append(product2)
    # time.sleep(0.2)

    # Product 3: Samsung Galaxy S23
    product3 = create_product({
        "sku": "SGS23-001", "name": "Samsung Galaxy S23",
        "description": "256GB, 8GB RAM, 50MP Camera",
        "brand_id": None, "unit_id": unit_id, "barcode": "123456789014",
        "qr_code": "QR003", "weight": 0.168, "volume": None,
        "is_bundle": False, "has_serial_tracking": True, "has_batch_tracking": False,
        "category_ids": [electronics["id"], smartphones["id"]] if electronics and smartphones else [],
        "tag_names": ["sale", "budget"], "variants": []
    })
    if product3:
        products.append(product3)
    # time.sleep(0.2)

    # Product 4: Dell XPS 15
    product4 = create_product({
        "sku": "XPS-001", "name": "Dell XPS 15",
        "description": "Intel i7, 32GB RAM, 1TB SSD, 4K Display",
        "brand_id": None, "unit_id": unit_id, "barcode": "123456789015",
        "qr_code": "QR004", "weight": 1.8, "volume": None,
        "is_bundle": False, "has_serial_tracking": True, "has_batch_tracking": False,
        "category_ids": [electronics["id"], laptops["id"]] if electronics and laptops else [],
        "tag_names": ["premium"], "variants": []
    })
    if product4:
        products.append(product4)
    # time.sleep(0.2)

    # Product 5: Nike Air Max
    product5 = create_product({
        "sku": "NK-001", "name": "Nike Air Max",
        "description": "Running shoes, breathable mesh, cushioned sole",
        "brand_id": None, "unit_id": unit_id, "barcode": "123456789016",
        "qr_code": "QR005", "weight": 0.3, "volume": None,
        "is_bundle": False, "has_serial_tracking": False, "has_batch_tracking": True,
        "category_ids": [clothing["id"], mens["id"]] if clothing and mens else [],
        "tag_names": ["best-seller", "premium"], "variants": []
    })
    if product5:
        products.append(product5)
    # time.sleep(0.2)

    # Product 6: Wireless Headphones
    product6 = create_product({
        "sku": "WH-001", "name": "Sony WH-1000XM5",
        "description": "Noise cancelling, Bluetooth 5.0, 30hr battery",
        "brand_id": None, "unit_id": unit_id, "barcode": "123456789018",
        "qr_code": "QR007", "weight": 0.25, "volume": None,
        "is_bundle": False, "has_serial_tracking": True, "has_batch_tracking": False,
        "category_ids": [electronics["id"], accessories["id"]] if electronics and accessories else [],
        "tag_names": ["best-seller", "sale"], "variants": []
    })
    if product6:
        products.append(product6)
    # time.sleep(0.2)

    # Product 7: MALM Bed Frame
    product7 = create_product({
        "sku": "MALM-001", "name": "MALM Bed Frame",
        "description": "Queen size, white, with storage",
        "brand_id": None, "unit_id": 4, "barcode": "123456789017",
        "qr_code": "QR006", "weight": 45.0, "volume": None,
        "is_bundle": True, "has_serial_tracking": False, "has_batch_tracking": False,
        "category_ids": [home_garden["id"], furniture["id"]] if home_garden and furniture else [],
        "tag_names": ["featured"], "variants": []
    })
    if product7:
        products.append(product7)
    # time.sleep(0.2)

    # Product 8: Blender
    product8 = create_product({
        "sku": "BL-001", "name": "Kitchen Blender 500W",
        "description": "High speed blender, 5 speeds, stainless steel blades",
        "brand_id": None, "unit_id": unit_id, "barcode": "123456789020",
        "qr_code": "QR009", "weight": 2.5, "volume": None,
        "is_bundle": False, "has_serial_tracking": False, "has_batch_tracking": True,
        "category_ids": [home_garden["id"], kitchen["id"]] if home_garden and kitchen else [],
        "tag_names": ["budget"], "variants": []
    })
    if product8:
        products.append(product8)
    # time.sleep(0.2)

    # Product 9: Cotton T-Shirt
    product9 = create_product({
        "sku": "CT-001", "name": "Cotton T-Shirt",
        "description": "100% cotton, comfortable fit, available in multiple colors",
        "brand_id": None, "unit_id": unit_id, "barcode": "123456789021",
        "qr_code": "QR010", "weight": 0.15, "volume": None,
        "is_bundle": False, "has_serial_tracking": False, "has_batch_tracking": True,
        "category_ids": [clothing["id"], mens["id"]] if clothing and mens else [],
        "tag_names": ["new"], "variants": []
    })
    if product9:
        products.append(product9)

    print("\n--- Creating Warehouses ---")
    warehouses = []

    wh1 = create_warehouse("Main Warehouse", "WH01", "123 Main Street, Downtown")
    if wh1:
        warehouses.append(wh1)
        add_warehouse_location(wh1["id"], "Zone A", "Rack 1", "Bin 1", "WH01")
        # time.sleep(0.1)
        add_warehouse_location(wh1["id"], "Zone A", "Rack 1", "Bin 2", "WH01")
        # time.sleep(0.1)
        add_warehouse_location(wh1["id"], "Zone B", "Rack 2", "Bin 1", "WH01")
    # time.sleep(0.3)

    wh2 = create_warehouse("East Warehouse", "WH02", "456 East Avenue, Industrial Area")
    if wh2:
        warehouses.append(wh2)
        add_warehouse_location(wh2["id"], "Zone A", "Rack 1", "Bin 1", "WH02")
        # time.sleep(0.1)
        add_warehouse_location(wh2["id"], "Zone A", "Rack 1", "Bin 2", "WH02")
    # time.sleep(0.3)

    wh3 = create_warehouse("West Warehouse", "WH03", "789 West Boulevard, Logistics Park")
    if wh3:
        warehouses.append(wh3)
        add_warehouse_location(wh3["id"], "Zone A", "Rack 1", "Bin 1", "WH03")

    print("\n--- Creating Suppliers ---")
    suppliers = []

    sup1 = create_supplier({
        "name": "Tech Distributors Inc.", "code": "SUP001",
        "contact_person": "John Smith", "email": "orders@techdist.com",
        "phone": "+1-555-0100", "address": "123 Tech Park, Silicon Valley, CA",
        "tax_number": "TAX123456", "payment_terms": 30
    })
    if sup1:
        suppliers.append(sup1)
    # time.sleep(0.2)

    sup2 = create_supplier({
        "name": "Fashion Wholesale Ltd.", "code": "SUP002",
        "contact_person": "Jane Doe", "email": "sales@fashionwholesale.com",
        "phone": "+1-555-0200", "address": "456 Fashion Ave, New York, NY",
        "tax_number": "TAX789012", "payment_terms": 45
    })
    if sup2:
        suppliers.append(sup2)
    # time.sleep(0.2)

    sup3 = create_supplier({
        "name": "Home Goods Supply Co.", "code": "SUP003",
        "contact_person": "Bob Johnson", "email": "info@homegoods.com",
        "phone": "+1-555-0300", "address": "789 Home St, Chicago, IL",
        "tax_number": "TAX345678", "payment_terms": 30
    })
    if sup3:
        suppliers.append(sup3)

    print("\n--- Creating Customers ---")
    customers = []

    cust1 = create_customer({
        "name": "John Doe", "email": "john@example.com",
        "phone": "+1-555-1000", "address": "123 Customer St, Los Angeles, CA",
        "tax_number": "CUST123", "price_tier": "retail"
    })
    if cust1:
        customers.append(cust1)
    # time.sleep(0.2)

    cust2 = create_customer({
        "name": "Jane Smith", "email": "jane@example.com",
        "phone": "+1-555-1001", "address": "456 Buyer Ave, Chicago, IL",
        "tax_number": "CUST456", "price_tier": "wholesale"
    })
    if cust2:
        customers.append(cust2)
    # time.sleep(0.2)

    cust3 = create_customer({
        "name": "ABC Corp", "email": "contact@abccorp.com",
        "phone": "+1-555-1002", "address": "789 Business Rd, Dallas, TX",
        "tax_number": "CUST789", "price_tier": "wholesale"
    })
    if cust3:
        customers.append(cust3)
    # time.sleep(0.2)

    cust4 = create_customer({
        "name": "XYZ Retail", "email": "orders@xyzretail.com",
        "phone": "+1-555-1003", "address": "321 Retail Blvd, Miami, FL",
        "tax_number": "CUST321", "price_tier": "retail"
    })
    if cust4:
        customers.append(cust4)

    print("\n--- Creating Purchase Orders (Initial Stock) ---")
    
    # PO 1 - Electronics (includes headphones product6)
    if suppliers and warehouses and len(products) >= 6:
        po1 = create_purchase_order({
            "supplier_id": sup1["id"],
            "warehouse_id": wh1["id"],
            "expected_delivery": (datetime.now() + timedelta(days=7)).isoformat(),
            "items": [
                {"product_id": product1["id"], "quantity": 50, "unit_price": 1999.99},
                {"product_id": product2["id"], "quantity": 100, "unit_price": 799.99},
                {"product_id": product3["id"], "quantity": 75, "unit_price": 899.99},
                {"product_id": product4["id"], "quantity": 30, "unit_price": 2499.99},  # Added XPS
                {"product_id": product6["id"], "quantity": 150, "unit_price": 349.99}   # Added headphones
            ],
            "notes": "Initial stock order - Electronics"
        })
        if po1 and "po_id" in po1:
            # time.sleep(1)
            receive_purchase_order(po1["po_id"])

    # PO 2 - Fashion
    if suppliers and warehouses and len(products) >= 5:
        po2 = create_purchase_order({
            "supplier_id": sup2["id"],
            "warehouse_id": wh2["id"] if wh2 else wh1["id"],
            "expected_delivery": (datetime.now() + timedelta(days=5)).isoformat(),
            "items": [
                {"product_id": product5["id"], "quantity": 200, "unit_price": 89.99},
                {"product_id": product9["id"], "quantity": 300, "unit_price": 19.99}
            ],
            "notes": "Initial stock order - Fashion"
        })
        if po2 and "po_id" in po2:
            # time.sleep(1)
            receive_purchase_order(po2["po_id"])

    # PO 3 - Home Goods
    if suppliers and warehouses and len(products) >= 7:
        po3 = create_purchase_order({
            "supplier_id": sup3["id"],
            "warehouse_id": wh3["id"] if wh3 else wh1["id"],
            "expected_delivery": (datetime.now() + timedelta(days=10)).isoformat(),
            "items": [
                {"product_id": product7["id"], "quantity": 10, "unit_price": 399.99},
                {"product_id": product8["id"], "quantity": 40, "unit_price": 59.99}
            ],
            "notes": "Initial stock order - Home Goods"
        })
        if po3 and "po_id" in po3:
            # time.sleep(1)
            receive_purchase_order(po3["po_id"])

    print("\n--- Creating Sales Orders ---")
    if customers and warehouses and len(products) >= 6:
        # SO 1 - Includes headphones (now in stock)
        so1 = create_sales_order({
            "customer_id": cust1["id"],
            "warehouse_id": wh1["id"],
            "items": [
                {"product_id": product1["id"], "quantity": 1, "unit_price": 2199.99, "discount": 100},
                {"product_id": product6["id"], "quantity": 2, "unit_price": 349.99, "discount": 50}
            ],
            "shipping_address": "123 Customer St, Los Angeles, CA 90001",
            "notes": "Rush delivery - Premium customer"
        })
        if so1 and "order_id" in so1:
            # time.sleep(1)
            dispatch_sales_order(so1["order_id"])

        # SO 2 - Wholesale order
        so2 = create_sales_order({
            "customer_id": cust2["id"],
            "warehouse_id": wh2["id"] if wh2 else wh1["id"],
            "items": [
                {"product_id": product5["id"], "quantity": 25, "unit_price": 79.99, "discount": 200},
                {"product_id": product9["id"], "quantity": 50, "unit_price": 17.99, "discount": 100}
            ],
            "shipping_address": "456 Buyer Ave, Chicago, IL 60601",
            "notes": "Wholesale discount applied"
        })
        if so2 and "order_id" in so2:
            # time.sleep(1)
            dispatch_sales_order(so2["order_id"])

        # SO 3 - Corporate order (pending)
        so3 = create_sales_order({
            "customer_id": cust3["id"],
            "warehouse_id": wh1["id"],
            "items": [
                {"product_id": product4["id"], "quantity": 3, "unit_price": 2499.99, "discount": 0}
            ],
            "shipping_address": "789 Business Rd, Dallas, TX 75201",
            "notes": "Corporate account - Net 30"
        })
        if so3:
            print("  ℹ Sales order 3 created (pending dispatch)")

    print("\n--- Creating Stock Transfers ---")
    if len(warehouses) >= 2 and len(products) >= 4 and wh1 and wh2:
        # Transfer XPS laptops from WH1 to WH2 (now has stock)
        transfer1 = create_transfer_order({
            "from_warehouse_id": wh1["id"],
            "to_warehouse_id": wh2["id"],
            "product_id": product4["id"],
            "quantity": 5
        })
        if transfer1 and "transfer_id" in transfer1:
            # time.sleep(1)
            complete_transfer(transfer1["transfer_id"])

        # Transfer T-shirts from WH2 to WH1
        transfer2 = create_transfer_order({
            "from_warehouse_id": wh2["id"],
            "to_warehouse_id": wh1["id"],
            "product_id": product9["id"],
            "quantity": 50
        })
        if transfer2 and "transfer_id" in transfer2:
            # time.sleep(1)
            complete_transfer(transfer2["transfer_id"])

        # Transfer headphones from WH1 to WH3
        transfer3 = create_transfer_order({
            "from_warehouse_id": wh1["id"],
            "to_warehouse_id": wh3["id"],
            "product_id": product6["id"],
            "quantity": 20
        })
        if transfer3 and "transfer_id" in transfer3:
            # time.sleep(1)
            complete_transfer(transfer3["transfer_id"])

    print("\n" + "="*60)
    print("DATABASE SEEDING COMPLETE!")
    print("="*60)

    print(f"\n📊 Summary:")
    print(f"  • Categories: 10")
    print(f"  • Products: {len(products)}")
    print(f"  • Warehouses: {len(warehouses)}")
    print(f"  • Suppliers: {len(suppliers)}")
    print(f"  • Customers: {len(customers)}")

    return True


def verify_seeding():
    """Verify that data was seeded correctly"""
    print("\n--- Verifying Seeded Data ---")

    endpoints = [
        ("/products", "Products"),
        ("/warehouses", "Warehouses"),
        ("/suppliers", "Suppliers"),
        ("/customers", "Customers"),
        ("/categories", "Categories"),
        ("/stock", "Stock Records")
    ]

    for endpoint, name in endpoints:
        response = requests.get(f"{API_BASE_URL}{endpoint}", headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 1
            print(f"  ✓ {name}: {count} records")
        else:
            print(f"  ✗ {name}: Failed to fetch")

    response = requests.get(f"{API_BASE_URL}/dashboard/stats", headers=get_headers())
    if response.status_code == 200:
        stats = response.json()
        print(f"  ✓ Dashboard: Total Products: {stats.get('total_products', 0)}")
        print(f"  ✓ Low Stock Alerts: {stats.get('low_stock_alerts', 0)}")
        print(f"  ✓ Total Warehouses: {stats.get('total_warehouses', 0)}")
        print(f"  ✓ Total Suppliers: {stats.get('total_suppliers', 0)}")
        print(f"  ✓ Total Customers: {stats.get('total_customers', 0)}")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     Inventory System Database Seeder (API Version)       ║
    ║                                                          ║
    ║  This script will seed the database using the REST API   ║
    ║  Make sure the API server is running on port 8000       ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ API server is not responding. Please start the API server first.")
            print("   Run: python app.py")
            exit(1)

        print("✓ API server is running\n")

        if seed_database():
            verify_seeding()
            print("\n✅ Seeding completed successfully!")
            print("\nYou can now log in to the React app with:")
            print("  Username: admin")
            print("  Password: admin123")
            print("\n📦 Sample data created:")
            print("  • 9 products with stock levels")
            print("  • 3 warehouses with locations")
            print("  • 3 suppliers and 4 customers")
            print("  • Purchase orders with received stock")
            print("  • Sales orders (some dispatched, some pending)")
            print("  • Stock transfers between warehouses")
        else:
            print("\n❌ Seeding failed. Please check the errors above.")

    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to the API server.")
        print("   Please make sure the API server is running on http://localhost:8000")
        print("   Run: python app.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()