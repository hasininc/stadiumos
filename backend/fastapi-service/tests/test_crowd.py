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

def test_crowd_endpoints():
    headers = get_operator_headers()
    
    # 1. Get all zones
    response = client.get("/api/v1/crowd/zones", headers=headers)
    assert response.status_code == 200
    zones = response.json()
    assert len(zones) > 0
    target_zone = zones[0]["id"]
    
    # 2. Get specific zone by ID
    response = client.get(f"/api/v1/crowd/zones/{target_zone}", headers=headers)
    assert response.status_code == 200
    zone_detail = response.json()
    assert zone_detail["id"] == target_zone
    
    # 3. Create a crowd snapshot
    snapshot_payload = {
        "zone_id": target_zone,
        "headcount": 500
    }
    response = client.post("/api/v1/crowd/snapshot", json=snapshot_payload, headers=headers)
    assert response.status_code == 201
    snapshot_data = response.json()
    assert snapshot_data["zone_id"] == target_zone
    assert snapshot_data["headcount"] == 500
    
    # 4. Create custom crowd alert
    alert_payload = {
        "zone_id": target_zone,
        "severity": "Critical",
        "message": "High density bottleneck at turnstiles"
    }
    response = client.post("/api/v1/crowd/alert", json=alert_payload, headers=headers)
    assert response.status_code == 201
    alert_data = response.json()
    assert alert_data["zone_id"] == target_zone
    assert alert_data["severity"] == "Critical"
    
    # 5. Get active live alerts
    response = client.get("/api/v1/crowd/live", headers=headers)
    assert response.status_code == 200
    live_alerts = response.json()
    assert len(live_alerts) > 0
    assert any(a["zone_id"] == target_zone for a in live_alerts)
    
    # 6. Update zone threshold
    threshold_payload = {
        "busy_pct": 75.0,
        "critical_pct": 90.0
    }
    response = client.patch(f"/api/v1/crowd/zones/{target_zone}/threshold", json=threshold_payload, headers=headers)
    assert response.status_code == 200
    assert "updated successfully" in response.json()["message"]
    
    # 7. Get crowd heatmap
    response = client.get("/api/v1/crowd/heatmap", headers=headers)
    assert response.status_code == 200
    heatmap = response.json()
    assert len(heatmap) > 0
    
    # 8. Get historical logs
    response = client.get(f"/api/v1/crowd/history?zone_id={target_zone}", headers=headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history) > 0

def test_websocket_endpoint():
    with client.websocket_connect("/api/v1/crowd/ws?zone_id=ZONE_GATE_A") as websocket:
        websocket.send_text("ping")
        data = websocket.receive_json()
        assert data == {"pong": True, "received": "ping"}
