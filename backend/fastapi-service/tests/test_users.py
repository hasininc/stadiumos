import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_user_and_login(email: str, password: str, account_type: str = "fan") -> str:
    # Helper to register and login a user, returning access token
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "account_type": account_type
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    return res.json()["access_token"]

def test_user_profile_management():
    # 1. Setup standard fan user and login
    fan_id = str(uuid.uuid4())[:8]
    fan_email = f"fan_{fan_id}@stadiumos.dev"
    fan_token = create_user_and_login(fan_email, "SecurePassword123!", "fan")
    fan_headers = {"Authorization": f"Bearer {fan_token}"}

    # 2. Setup operator user and login
    op_id = str(uuid.uuid4())[:8]
    op_email = f"op_{op_id}@stadiumos.dev"
    op_token = create_user_and_login(op_email, "SecurePassword123!", "operator")
    op_headers = {"Authorization": f"Bearer {op_token}"}

    # 3. Retrieve own profile
    response = client.get("/api/v1/users/me", headers=fan_headers)
    assert response.status_code == 200
    profile = response.json()
    assert profile["email"] == fan_email
    assert "profile" in profile
    assert "accessibility" in profile

    # 4. Update profile details
    update_payload = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "555-1234",
        "address": "123 Stadium Way"
    }
    response = client.put("/api/v1/users/me", json=update_payload, headers=fan_headers)
    assert response.status_code == 200
    updated_profile = response.json()
    assert updated_profile["profile"]["first_name"] == "John"
    assert updated_profile["profile"]["last_name"] == "Doe"

    # 5. Update accessibility preferences
    access_payload = {
        "requires_wheelchair": True,
        "audio_assistance": False,
        "special_requirements": "Need close seating"
    }
    response = client.put("/api/v1/users/me/accessibility", json=access_payload, headers=fan_headers)
    assert response.status_code == 200
    updated_access = response.json()
    assert updated_access["accessibility"]["requires_wheelchair"] is True
    assert updated_access["accessibility"]["special_requirements"] == "Need close seating"

    # 6. Manage Emergency Contacts
    contact_payload = {
        "contact_name": "Jane Doe",
        "relationship": "Spouse",
        "phone_number": "555-5678"
    }
    response = client.post("/api/v1/users/me/emergency-contacts", json=contact_payload, headers=fan_headers)
    assert response.status_code == 200
    contact_data = response.json()
    assert contact_data["contact_name"] == "Jane Doe"
    contact_id = contact_data["id"]

    # Delete emergency contact
    response = client.delete(f"/api/v1/users/me/emergency-contacts/{contact_id}", headers=fan_headers)
    assert response.status_code == 204

    # 7. Access search endpoint
    # Fan user should get 403 Forbidden
    response = client.get("/api/v1/users/search", headers=fan_headers)
    assert response.status_code == 403
    
    # Operator user should get 200 OK
    response = client.get("/api/v1/users/search", headers=op_headers)
    assert response.status_code == 200
    users_list = response.json()
    assert len(users_list) > 0

    # 8. Access activity logs
    response = client.get("/api/v1/users/activity", headers=fan_headers)
    assert response.status_code == 200
    activity_logs = response.json()
    # Profile update action should be logged
    assert any(log["action"] == "UPDATE_PROFILE" for log in activity_logs)

    # 9. Get user by ID (unauthorized vs authorized)
    fan_profile_res = client.get("/api/v1/users/me", headers=fan_headers).json()
    fan_user_uuid = fan_profile_res["id"]
    
    response = client.get(f"/api/v1/users/{fan_user_uuid}", headers=fan_headers)
    assert response.status_code == 403
    
    response = client.get(f"/api/v1/users/{fan_user_uuid}", headers=op_headers)
    assert response.status_code == 200
    assert response.json()["email"] == fan_email

    # 10. Update user status and role (unauthorized vs authorized)
    # Fan user cannot deactivate or change roles
    response = client.patch(f"/api/v1/users/{fan_user_uuid}/status", json={"is_active": False}, headers=fan_headers)
    assert response.status_code == 403

    response = client.patch(f"/api/v1/users/{fan_user_uuid}/role", json={"role_name": "Operations Manager"}, headers=fan_headers)
    assert response.status_code == 403

    # Operator user can deactivate
    response = client.patch(f"/api/v1/users/{fan_user_uuid}/status", json={"is_active": False}, headers=op_headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Operator user can change role
    response = client.patch(f"/api/v1/users/{fan_user_uuid}/role", json={"role_name": "Operations Manager"}, headers=op_headers)
    assert response.status_code == 200
    assert any(r["name"] == "Operations Manager" for r in response.json()["roles"])

    # 11. Delete user account (soft delete)
    # Fan cannot delete
    response = client.delete(f"/api/v1/users/{fan_user_uuid}", headers=fan_headers)
    assert response.status_code == 403

    # Operator can soft delete
    response = client.delete(f"/api/v1/users/{fan_user_uuid}", headers=op_headers)
    assert response.status_code == 204
