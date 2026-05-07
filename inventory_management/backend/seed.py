import requests
import time

base_url = 'http://localhost:8000/api/v1'
headers_json = {'Content-Type': 'application/json'}
headers_form = {'Content-Type': 'application/x-www-form-urlencoded'}

print('=== Database Seeding 10 Records Per Table ===')

# Step 1: Register seeduser
print('\n1. Register seeduser...')
try:
    r = requests.post(f'{base_url}/auth/register', json={'username': 'seeduser',
                                                         'email': 'seed@example.com', 'password': 'seedpass'}, headers=headers_json)
    print('Register:', r.status_code, r.json() if r.ok else r.text)
except Exception as e:
    print('Register error:', str(e))
time.sleep(1)

# Step 2: Login
print('\n2. Login...')
login_r = requests.post(f'{base_url}/auth/token', data={'username': 'seeduser',
                                                        'password': 'seedpass'}, headers=headers_form)
print('Login:', login_r.status_code, login_r.json()
      if login_r.ok else login_r.text)
token = login_r.json()['access_token'] if login_r.ok else None
if not token:
    print('Failed to get token')
    exit()
auth_headers = {'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'}

# Step 3: Create 3 Warehouses
warehouse_ids = []
print('\n3. Create 3 Warehouses...')
warehouse_names = ['Main Warehouse', 'Secondary Warehouse', 'Storage Facility']
for i, name in enumerate(warehouse_names):
    warehouse_data = {'name': f'Seed {name}',
                      'location': f'Location {i+1}', 'address': f'{i+1} Seed St'}
    w_r = requests.post(f'{base_url}/warehouses/',
                        json=warehouse_data, headers=auth_headers)
    print(f'Warehouse {i+1}:', w_r.status_code,
          w_r.json() if w_r.ok else w_r.text)
    if w_r.ok:
        warehouse_ids.append(w_r.json()['id'])
time.sleep(1)

# Step 4: Create 10 Categories
category_ids = []
print('\n4. Create 10 Categories...')
for i in range(1, 11):
    cat_data = {'name': f'Seed Category {i}',
                'description': f'Test category {i}'}
    cat_r = requests.post(f'{base_url}/products/categories',
                          json=cat_data, headers=auth_headers)
    print(f'Category {i}:', cat_r.status_code,
          cat_r.json() if cat_r.ok else cat_r.text)
    if cat_r.ok:
        category_ids.append(cat_r.json()['id'])
time.sleep(1)

# Step 5: Create 10 Products
product_ids = []
print('\n5. Create 10 Products...')
for i in range(1, 11):
    cat_id = category_ids[0] if category_ids else 1
    product_data = {'name': f'Seed Product {i}', 'sku': f'SEED{i:03d}',
                    'category_id': cat_id, 'uom': 'pcs', 'min_stock_level': 10}
    p_r = requests.post(f'{base_url}/products/',
                        json=product_data, headers=auth_headers)
    print(f'Product {i}:', p_r.status_code, p_r.json() if p_r.ok else p_r.text)
    if p_r.ok:
        product_ids.append(p_r.json()['id'])
time.sleep(1)

# Step 6: Create 10 Stock entries
print('\n6. Create 10 Stock...')
for i in range(1, 11):
    wh_id = warehouse_ids[0] if warehouse_ids else 1
    prod_id = product_ids[i-1] if i <= len(product_ids) else product_ids[0]
    stock_data = {'product_id': prod_id,
                  'warehouse_id': wh_id, 'available_qty': 100 * i}
    s_r = requests.post(f'{base_url}/stock/',
                        json=stock_data, headers=auth_headers)
    print(f'Stock {i}:', s_r.status_code, s_r.json() if s_r.ok else s_r.text)
time.sleep(1)

# Step 7: Create 10 Batches
print('\n7. Create 10 Batches...')
for i in range(1, 11):
    prod_id = product_ids[i-1] if i <= len(product_ids) else product_ids[0]
    batch_data = {'product_id': prod_id,
                  'batch_number': f'BATCH-SEED-{i:03d}', 'quantity': 50 * i}
    b_r = requests.post(f'{base_url}/batches/',
                        json=batch_data, headers=auth_headers)
    print(f'Batch {i}:', b_r.status_code, b_r.json() if b_r.ok else b_r.text)
time.sleep(1)

# Step 8: Create 10 Suppliers
print('\n8. Create 10 Suppliers...')
for i in range(1, 11):
    sup_data = {'name': f'Seed Supplier {i}', 'contact_email': f'sup{i}@seed.com',
                'phone': f'555-{i:04d}', 'address': f'Supplier {i} St'}
    sup_r = requests.post(f'{base_url}/procurement/suppliers',
                          json=sup_data, headers=auth_headers)
    print(f'Supplier {i}:', sup_r.status_code,
          sup_r.json() if sup_r.ok else sup_r.text)
time.sleep(1)

# Step 9: Create 10 Purchase Orders
print('\n9. Create 10 PO...')
for i in range(1, 11):
    sup_id = 1  # First supplier
    po_data = {'supplier_id': sup_id, 'status': 'pending',
               'expected_date': '2024-12-31', 'total_amount': 1000 * i}
    po_r = requests.post(
        f'{base_url}/procurement/purchase-orders', json=po_data, headers=auth_headers)
    print(f'PO {i}:', po_r.status_code, po_r.json() if po_r.ok else po_r.text)
time.sleep(1)

# Step 10: Create 10 Goods Receipts
print('\n10. Create 10 Goods Receipts...')
po_id = 1  # First PO
prod_id = product_ids[0] if product_ids else 1
stock_id = 1  # First stock
for i in range(1, 11):
    gr_data = {'po_id': po_id, 'product_id': prod_id, 'stock_id': stock_id,
               'received_qty': 20 * i, 'quality_passed': True, 'unit_cost': 100.0}
    gr_r = requests.post(
        f'{base_url}/procurement/goods-receipts', json=gr_data, headers=auth_headers)
    print(f'GR {i}:', gr_r.status_code, gr_r.json() if gr_r.ok else gr_r.text)
time.sleep(1)

# Step 11: Create 10 Sales Orders
print('\n11. Create 10 Sales...')
stock_id = 1
prod_id = product_ids[0] if product_ids else 1
for i in range(1, 11):
    sales_data = {'customer_name': f'Seed Customer {i}', 'line_items': [
        {'product_id': prod_id, 'stock_id': stock_id, 'qty': 5 * i, 'price': 100.0}]}
    sales_r = requests.post(f'{base_url}/sales/',
                            json=sales_data, headers=auth_headers)
    print(f'Sales {i}:', sales_r.status_code,
          sales_r.json() if sales_r.ok else sales_r.text)

print('\\n=== Seeding complete! 10+ records per table. Login: seeduser/seedpass ===')
