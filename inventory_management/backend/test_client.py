import urllib.request
import urllib.parse
import json
import ssl

# Disable SSL for localhost
ssl._create_default_https_context = ssl._create_unverified_context

base_url = 'http://localhost:8000/api/v1'
headers_json = {'Content-Type': 'application/json'}


def post_json(url, data):
    req = urllib.request.Request(url, data=json.dumps(
        data).encode('utf-8'), headers=headers_json, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode(), json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def post_form(url, data):
    data_encoded = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=data_encoded, headers={
                                 'Content-Type': 'application/x-www-form-urlencoded'}, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode(), json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


print('=== Testing all POST endpoints ===')

# 1. Register
print('\\n1. POST /auth/register')
status, resp = post_json(f'{base_url}/auth/register', {'username': 'testbb',
                         'email': 'testbb@example.com', 'password': 'testpass123'})
print('Status:', status)
print('Response:', resp)

# 2. Superuser (placeholder)
print('\\n2. POST /auth/superuser')
status2, resp2 = post_json(f'{base_url}/auth/superuser', {})
print('Status:', status2)
print('Response:', resp2)

# 3. Login
print('\\n3. POST /auth/token')
status3, resp3 = post_form(
    f'{base_url}/auth/token', {'username': 'testbb', 'password': 'testpass123'})
print('Status:', status3)
print('Response:', resp3)

if status3 == 200:
    token = resp3['access_token']
    print('Token obtained')
    auth_headers = {'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'}

    def post_auth(url, data):
        req = urllib.request.Request(url, data=json.dumps(
            data).encode('utf-8'), headers=auth_headers, method='POST')
        try:
            with urllib.request.urlopen(req) as response:
                return response.getcode(), json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode())

    # 4. Warehouse
    print('\\n4. POST /warehouses/')
    status4, resp4 = post_auth(
        f'{base_url}/warehouses/', {'name': 'Test Warehouse'})
    print('Status:', status4)
    print('Response:', resp4)

    # 5. Category
    print('\\n5. POST /products/categories')
    status5, resp5 = post_auth(
        f'{base_url}/products/categories', {'name': 'Test Category'})
    print('Status:', status5)
    print('Response:', resp5)

    # 6. Product (needs category_id)
    if status5 == 201:
        cat_id = resp5['id']
        print('\\n6. POST /products/')
        status6, resp6 = post_auth(
            f'{base_url}/products/', {'name': 'Test Product', 'sku': 'TEST001', 'category_id': cat_id})
        print('Status:', status6)
        print('Response:', resp6)

        # 7. Stock (needs warehouse_id, product_id)
        if status4 == 201 and status6 == 201:
            wh_id = resp4['id']
            prod_id = resp6['id']
            print('\\n7. POST /stock/')
            status7, resp7 = post_auth(
                f'{base_url}/stock/', {'product_id': prod_id, 'warehouse_id': wh_id, 'available_qty': 100})
            print('Status:', status7)
            print('Response:', resp7)

            # Continue for others...
            print('\\n8. POST /stock/movements')
            status8, resp8 = post_auth(f'{base_url}/stock/movements', {
                                       'type': 'adjustment', 'quantity': 10, 'stock_id': resp7['id'], 'product_id': prod_id})
            print('Status:', status8)
            print('Response:', resp8)

            # Batches
            print('\\n9. POST /batches/')
            status9, resp9 = post_auth(
                f'{base_url}/batches/', {'product_id': prod_id, 'batch_number': 'BATCH001', 'quantity': 50})
            print('Status:', status9)
            print('Response:', resp9)

            # Procurement supplier
            print('\\n10. POST /procurement/suppliers')
            status10, resp10 = post_auth(f'{base_url}/procurement/suppliers', {
                                         'name': 'Test Supplier', 'contact_email': 'sup@example.com', 'phone': '123'})
            print('Status:', status10)
            print('Response:', resp10)

            # Purchase order (needs supplier_id)
            if status10 == 201:
                sup_id = resp10['id']
                print('\\n11. POST /procurement/purchase-orders')
                status11, resp11 = post_auth(
                    f'{base_url}/procurement/purchase-orders', {'supplier_id': sup_id})
                print('Status:', status11)
                print('Response:', resp11)

                # Goods receipt (needs po_id, product_id, stock_id)
                print('\\n12. POST /procurement/goods-receipts')
                status12, resp12 = post_auth(f'{base_url}/procurement/goods-receipts', {
                                             'po_id': resp11['id'], 'product_id': prod_id, 'stock_id': resp7['id'], 'received_qty': 20, 'quality_passed': True})
                print('Status:', status12)
                print('Response:', resp12)

            # Sales (line_items needs stock_ids etc)
            print('\\n13. POST /sales/')
            sales_data = {'customer_name': 'Test Customer', 'line_items': [
                {'product_id': prod_id, 'stock_id': resp7['id'], 'qty': 5, 'price': 10.0}]}
            status13, resp13 = post_auth(f'{base_url}/sales/', sales_data)
            print('Status:', status13)
            print('Response:', resp13)
else:
    print('Auth failed')
