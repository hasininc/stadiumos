import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_operator_headers():
    random_id = str(uuid.uuid4())[:8]
    email = f"operator_{random_id}@stadiumos.dev"
    password = "SecurePassword123!"
    
    register_payload = {
        "email": email,
        "password": password,
        "account_type": "operator"
    }
    
    response = client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201
    
    login_payload = {
        "email": email,
        "password": password
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    token_data = response.json()
    access_token = token_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

def test_vendor_endpoints():
    headers = get_operator_headers()
    
    # 1. List all vendors
    response = client.get("/api/v1/vendors/", headers=headers)
    assert response.status_code == 200
    vendors = response.json()
    assert len(vendors) > 0
    target_vendor_id = vendors[0]["id"]
    
    # 2. Register a new vendor
    vendor_payload = {
        "name": "East Stand Pretzels",
        "type": "Food",
        "zone_id": "ZONE_GATE_B"
    }
    response = client.post("/api/v1/vendors/", json=vendor_payload, headers=headers)
    assert response.status_code == 201
    new_vendor = response.json()
    new_vendor_id = new_vendor["id"]
    
    # 3. Get vendor by ID
    response = client.get(f"/api/v1/vendors/{new_vendor_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "East Stand Pretzels"
    
    # 4. Get active inventories to extract a valid product_id
    response = client.get("/api/v1/vendors/inventory", headers=headers)
    assert response.status_code == 200
    inventories = response.json()
    assert len(inventories) > 0
    existing_product_id = inventories[0]["product_id"]
    
    inventory_payload = {
        "vendor_id": new_vendor_id,
        "product_id": existing_product_id,
        "current_stock": 20,
        "min_threshold": 30,
        "max_capacity": 500
    }
    response = client.post("/api/v1/vendors/inventory", json=inventory_payload, headers=headers)
    assert response.status_code == 201
    linked_inventory = response.json()
    inventory_id = linked_inventory["id"]
    product_id = linked_inventory["product_id"]
    
    # 5. List inventory
    response = client.get("/api/v1/vendors/inventory", headers=headers)
    assert response.status_code == 200
    inventories = response.json()
    assert len(inventories) > 0
    
    # 6. Update inventory stock
    update_payload = {
        "current_stock": 25
    }
    response = client.patch(f"/api/v1/vendors/inventory/{inventory_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["current_stock"] == 25
    
    # 7. Get low stock inventory
    response = client.get("/api/v1/vendors/inventory/low-stock", headers=headers)
    assert response.status_code == 200
    low_stock = response.json()
    # The glazed pretzels has 25 stock which is below warning_threshold (30)
    assert len(low_stock) > 0
    assert any(item["id"] == inventory_id for item in low_stock)
    
    # 8. Trigger restocking order
    restock_payload = {
        "vendor_id": new_vendor_id,
        "product_id": product_id,
        "quantity": 50
    }
    response = client.post("/api/v1/vendors/restock", json=restock_payload, headers=headers)
    assert response.status_code == 201
    restock_order = response.json()
    restock_order_id = restock_order["id"]
    assert restock_order["status"] == "Requested"
    
    # 9. Complete restocking order
    response = client.post(f"/api/v1/vendors/restock/{restock_order_id}/complete", headers=headers)
    assert response.status_code == 200
    completed_order = response.json()
    assert completed_order["status"] == "Completed"
    
    # 10. Get vendor analytics
    response = client.get(f"/api/v1/vendors/analytics/vendor?vendor_id={new_vendor_id}", headers=headers)
    assert response.status_code == 200
    analytics = response.json()
    assert "total_revenue" in analytics
    
    # 11. Get product analytics
    response = client.get("/api/v1/vendors/analytics/products", headers=headers)
    assert response.status_code == 200
    prod_analytics = response.json()
    assert "most_purchased_category" in prod_analytics

def test_vendor_websocket():
    with client.websocket_connect("/api/v1/vendors/ws") as websocket:
        websocket.send_text("vendor_ping")
        data = websocket.receive_json()
        assert data == {"ping": "received", "data": "vendor_ping"}
