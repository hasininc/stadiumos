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

def test_notification_endpoints():
    headers = get_operator_headers()
    
    # 1. Create a notification (for current user)
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    user_id = response.json()["id"]

    notify_payload = {
        "title": "Welcome Alert",
        "message": "Welcome to StadiumOS command console",
        "type": "AIRecommendation",
        "priority": "Normal",
        "user_id": user_id
    }
    response = client.post("/api/v1/notifications/", json=notify_payload, headers=headers)
    assert response.status_code == 201
    notification = response.json()
    notification_id = notification["id"]
    assert notification["title"] == "Welcome Alert"
    
    # 2. Get my notifications
    response = client.get("/api/v1/notifications/", headers=headers)
    assert response.status_code == 200
    my_notif = response.json()
    assert len(my_notif) > 0
    
    # 3. Get notification history
    response = client.get("/api/v1/notifications/history", headers=headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history) > 0
    
    # 4. Get specific notification
    response = client.get(f"/api/v1/notifications/{notification_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == notification_id
    
    # 5. Mark notification as read
    response = client.patch(f"/api/v1/notifications/{notification_id}/read", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_read"] is True
    
    # 6. Delete notification
    response = client.delete(f"/api/v1/notifications/{notification_id}", headers=headers)
    assert response.status_code == 204
    
    # 7. Verify deletion (404)
    response = client.get(f"/api/v1/notifications/{notification_id}", headers=headers)
    assert response.status_code == 404
    
    # 8. Broadcast notification to specific role
    broadcast_payload = {
        "title": "Evacuation Drill",
        "message": "This is a simulated fire drill announcement.",
        "roles": ["Operations Manager"],
        "type": "Emergency",
        "priority": "High"
    }
    response = client.post("/api/v1/notifications/broadcast", json=broadcast_payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Role broadcast completed"
    
    # 9. Get preferences
    response = client.get("/api/v1/notifications/preferences", headers=headers)
    assert response.status_code == 200
    prefs = response.json()
    assert len(prefs) > 0
    
    # 10. Update preferences
    pref_payload = {
        "preferences": [
            {
                "channel": "Email",
                "is_enabled": False
            }
        ]
    }
    response = client.patch("/api/v1/notifications/preferences", json=pref_payload, headers=headers)
    assert response.status_code == 200
    updated_prefs = response.json()
    email_pref = next(p for p in updated_prefs if p["channel"] == "Email")
    assert email_pref["is_enabled"] is False
