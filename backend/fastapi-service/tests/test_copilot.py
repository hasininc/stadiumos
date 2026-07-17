import uuid
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.copilot_service import CopilotStructuredResponse

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

@pytest.mark.asyncio
async def test_copilot_endpoints():
    headers = get_operator_headers()
    session_id = f"session-{uuid.uuid4()}"
    
    mock_copilot_response = CopilotStructuredResponse(
        summary="Concourse A and Gate areas are operating with normal flow density.",
        risk="LOW",
        confidence=0.95,
        recommendations=[
            {
                "priority": "LOW",
                "action": "Maintain routine perimeter patrol schedules",
                "expected_impact": "Ensure continuing perimeter security"
            }
        ],
        reasoning=[
            "Occupancy at all gates is below 35%",
            "No active medical or safety incidents reported"
        ]
    )
    
    # 1. Query copilot (mocked)
    with patch("app.api.v1.endpoints.copilot.copilot_service.query", new_callable=AsyncMock) as mock_query:
        mock_query.return_value = mock_copilot_response
        
        query_payload = {
            "message": "What is the current crowd flow status at Gate A?",
            "session_id": session_id,
            "scenario": None
        }
        response = client.post("/api/v1/copilot/query", json=query_payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == mock_copilot_response.summary
        assert data["risk"] == "LOW"
        assert len(data["recommendations"]) == 1
        
    # 2. Clear copilot session (mocked/simulated)
    with patch("app.api.v1.endpoints.copilot.copilot_service.clear_session", new_callable=AsyncMock) as mock_clear:
        response = client.delete(f"/api/v1/copilot/session/{session_id}", headers=headers)
        assert response.status_code == 204
        mock_clear.assert_called_once_with(session_id)
