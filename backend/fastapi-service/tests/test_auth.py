import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_flow_complete():
    # 1. Register a new user
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
    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert "roles" in data
    assert data["roles"][0]["name"] == "Operations Manager"

    # 2. Register duplicate email should return error
    response = client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 422
    assert "already exists" in response.json()["detail"]

    # 3. Login with invalid credentials
    login_invalid = {
        "email": email,
        "password": "WrongPassword!"
    }
    response = client.post("/api/v1/auth/login", json=login_invalid)
    assert response.status_code == 422
    assert "Invalid email or password" in response.json()["detail"]

    # 4. Login with valid credentials
    login_valid = {
        "email": email,
        "password": password
    }
    response = client.post("/api/v1/auth/login", json=login_valid)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    # Check that HTTP-only refresh token cookie is set
    assert "stadiumos_refresh_token" in response.cookies
    
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    # 5. Access profile info via /me
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    profile_data = response.json()
    assert profile_data["email"] == email

    # 6. Request profile without authorization header should return 401
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

    # 7. Refresh token rotation
    response = client.post(
        f"/api/v1/auth/refresh?refresh_token={refresh_token}"
    )
    assert response.status_code == 200
    new_token_data = response.json()
    assert "access_token" in new_token_data
    assert "refresh_token" in new_token_data
    
    # 8. Logout session
    response = client.post(
        f"/api/v1/auth/logout?refresh_token={new_token_data['refresh_token']}"
    )
    assert response.status_code == 204
    # Refresh token cookie should be cleared (or deleted)
    assert "stadiumos_refresh_token" in response.cookies or response.headers.get("set-cookie")
