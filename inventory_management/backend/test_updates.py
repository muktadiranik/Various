import urllib.request
import urllib.parse
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

base_url = 'http://localhost:8000/api/v1'

headers_json = {'Content-Type': 'application/json'}


def post_json(url, data):
    req = urllib.request.Request(url, data=json.dumps(
        data).encode('utf-8'), headers=headers_json, method='POST')
    with urllib.request.urlopen(req) as response:
        return response.getcode(), json.loads(response.read().decode())


def post_form(url, data):
    data_encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data_encoded, headers={
                                 'Content-Type': 'application/x-www-form-urlencoded'}, method='POST')
    with urllib.request.urlopen(req) as response:
        return response.getcode(), json.loads(response.read().decode())


def put_auth(url, data, auth_headers):
    req = urllib.request.Request(url, data=json.dumps(
        data).encode('utf-8'), headers=auth_headers, method='PUT')
    with urllib.request.urlopen(req) as response:
        return response.getcode(), json.loads(response.read().decode())


def get_auth(url, auth_headers):
    req = urllib.request.Request(url, headers=auth_headers)
    with urllib.request.urlopen(req) as response:
        return response.getcode(), json.loads(response.read().decode())


print('=== Testing all UPDATE (PUT) endpoints ===')

# Login first
print('\\nLogin for token...')
status_login, resp_login = post_form(
    f'{base_url}/auth/token', {'username': 'testbb', 'password': 'testpass123'})
print('Login status:', status_login)
token = resp_login['access_token']
auth_headers = {'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'}

# 1. Test Warehouse PUT /warehouses/{id}
print('\\n1. GET /warehouses/ to find ID')
status_gw, resp_gw = get_auth(f'{base_url}/warehouses/', auth_headers)
print('GET status:', status_gw)
if status_gw == 200 and resp_gw:
    warehouse_id = resp_gw[0]['id'] if isinstance(
        resp_gw, list) else resp_gw['id']
    print('Using warehouse_id:', warehouse_id)
    print('\\nPUT /warehouses/{warehouse_id}')
    update_data = {'name': 'Updated Test Warehouse'}
    status_uw, resp_uw = put_auth(
        f'{base_url}/warehouses/{warehouse_id}', update_data, auth_headers)
    print('PUT status:', status_uw)
    print('PUT response:', resp_uw)

# 2. Test Sales PUT /sales/{so_id}
print('\\n2. GET /sales/')
status_gs, resp_gs = get_auth(f'{base_url}/sales/', auth_headers)
if status_gs == 200 and resp_gs:
    so_id = resp_gs[0]['id']
    print('Using so_id:', so_id)
    print('\\nPUT /sales/{so_id}')
    update_data_sales = {'customer_name': 'Updated Customer'}
    status_us, resp_us = put_auth(
        f'{base_url}/sales/{so_id}', update_data_sales, auth_headers)
    print('PUT status:', status_us)
    print('PUT response:', resp_us)

# 3. Test Batches PUT /batches/{batch_id}
print('\\n3. GET /batches/')
status_gb, resp_gb = get_auth(f'{base_url}/batches/', auth_headers)
if status_gb == 200 and resp_gb:
    batch_id = resp_gb[0]['id']
    print('Using batch_id:', batch_id)
    print('\\nPUT /batches/{batch_id}')
    update_data_batch = {'quantity': 100}
    status_ub, resp_ub = put_auth(
        f'{base_url}/batches/{batch_id}', update_data_batch, auth_headers)
    print('PUT status:', status_ub)
    print('PUT response:', resp_ub)

print('\\nAll update endpoints tested.')
