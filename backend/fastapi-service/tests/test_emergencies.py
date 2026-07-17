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

def test_emergency_endpoints():
    headers = get_operator_headers()
    
    # 1. Create a new emergency incident
    incident_payload = {
        "title": "Medical emergency at gate A",
        "description": "Visitor in cardiac arrest near security scanner A2",
        "type": "Medical Emergency",
        "severity": "Critical",
        "zone_id": "ZONE_GATE_A"
    }
    response = client.post("/api/v1/emergencies/", json=incident_payload, headers=headers)
    assert response.status_code == 201
    incident = response.json()
    incident_id = incident["id"]
    assert incident["title"] == "Medical emergency at gate A"
    assert incident["status"] == "Reported"
    
    # 2. Get dashboard aggregates
    response = client.get("/api/v1/emergencies/dashboard", headers=headers)
    assert response.status_code == 200
    dashboard = response.json()
    assert "active_incidents_count" in dashboard
    assert "severity_distribution" in dashboard
    
    # 3. List incidents
    response = client.get("/api/v1/emergencies/", headers=headers)
    assert response.status_code == 200
    incidents = response.json()
    assert len(incidents) > 0
    assert any(i["id"] == incident_id for i in incidents)
    
    # 4. Get specific incident
    response = client.get(f"/api/v1/emergencies/{incident_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == incident_id
    
    # 5. Assign responder
    assign_payload = {
        "responder_name": "Dr. Sarah Adams",
        "dispatch_notes": "Dispatched EMT squad 3"
    }
    response = client.patch(f"/api/v1/emergencies/{incident_id}/assign", json=assign_payload, headers=headers)
    assert response.status_code == 200
    assigned_incident = response.json()
    assert assigned_incident["status"] == "Dispatched"
    assert assigned_incident["assigned_responder"] == "Dr. Sarah Adams"
    
    # 6. Escalate incident
    escalate_payload = {
        "escalation_reason": "Required backup cardiac monitor"
    }
    response = client.patch(f"/api/v1/emergencies/{incident_id}/escalate", json=escalate_payload, headers=headers)
    assert response.status_code == 200
    escalated_incident = response.json()
    # It remains "Dispatched" but logs to history or changes parameters
    
    # 7. Update status manually
    status_payload = {
        "status": "In Progress"
    }
    response = client.patch(f"/api/v1/emergencies/{incident_id}/status", json=status_payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"
    
    # 8. Resolve incident
    resolve_payload = {
        "resolution_notes": "Patient stabilized and loaded into ambulance."
    }
    response = client.patch(f"/api/v1/emergencies/{incident_id}/resolve", json=resolve_payload, headers=headers)
    assert response.status_code == 200
    resolved_incident = response.json()
    assert resolved_incident["status"] == "Resolved"
    assert resolved_incident["resolved_at"] is not None
    
    # 9. Get incident audit history
    response = client.get(f"/api/v1/emergencies/{incident_id}/history", headers=headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history) > 0
    actions = [h["action"] for h in history]
    assert "ASSIGN" in actions
    assert "RESOLVE" in actions
