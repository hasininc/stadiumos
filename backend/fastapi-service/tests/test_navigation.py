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

def test_navigation_endpoints():
    headers = get_operator_headers()
    
    # 1. Get stadium map topology
    response = client.get("/api/v1/navigation/map", headers=headers)
    assert response.status_code == 200
    map_data = response.json()
    assert "nodes" in map_data
    assert "edges" in map_data
    
    # 2. Get zone connectivity maps
    response = client.get("/api/v1/navigation/zones", headers=headers)
    assert response.status_code == 200
    zone_conn = response.json()
    assert zone_conn["status"] == "success"
    
    # 3. Get accessibility nodes
    response = client.get("/api/v1/navigation/accessibility", headers=headers)
    assert response.status_code == 200
    acc_nodes = response.json()
    assert "accessible_nodes" in acc_nodes
    
    # 4. Get evacuation routes
    response = client.get("/api/v1/navigation/evacuation", headers=headers)
    assert response.status_code == 200
    evac = response.json()
    assert evac["status"] == "success"
    
    # 5. Get navigation telemetry status
    response = client.get("/api/v1/navigation/status", headers=headers)
    assert response.status_code == 200
    nav_status = response.json()
    assert "active_navigation_sessions" in nav_status
    
    # 6. Generate route (Shortest)
    route_payload = {
        "start_node_id": "NODE-GATE-A",
        "end_node_id": "NODE-CONC-1",
        "routing_profile": "Shortest",
        "requires_accessibility": False
    }
    response = client.post("/api/v1/navigation/route", json=route_payload, headers=headers)
    assert response.status_code == 200
    route_data = response.json()
    assert len(route_data["path_nodes"]) > 0
    assert route_data["routing_profile"] == "Shortest"
    
    # 7. Generate reroute
    reroute_payload = {
        "current_node_id": "NODE-GATE-A",
        "end_node_id": "NODE-SEAT-1",
        "avoid_zones": ["ZONE_GATE_B"],
        "requires_accessibility": False
    }
    response = client.post("/api/v1/navigation/reroute", json=reroute_payload, headers=headers)
    assert response.status_code == 200
    reroute_data = response.json()
    assert len(reroute_data["path_nodes"]) > 0

def test_navigation_websocket():
    with client.websocket_connect("/api/v1/navigation/ws") as websocket:
        websocket.send_text("test_payload")
        data = websocket.receive_json()
        assert data == {"ping": "received", "data": "test_payload"}
