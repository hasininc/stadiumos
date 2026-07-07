import pytest
from fastapi import status

def test_user_registration(client):
    # Verify account creation
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "fan@stadiumos.com", "password": "securepassword123"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "fan@stadiumos.com"
    assert response.json()["is_active"] is True

def test_duplicate_user_registration_fails(client):
    # Register once
    client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@stadiumos.com", "password": "securepassword123"}
    )
    
    # Attempt duplicate register
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@stadiumos.com", "password": "securepassword123"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_user_login(client):
    # Onboard test user
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@stadiumos.com", "password": "securepassword123"}
    )

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@stadiumos.com", "password": "securepassword123"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_login_invalid_credentials_fails(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@stadiumos.com", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
