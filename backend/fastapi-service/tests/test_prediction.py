import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_prediction_api_success():
    payload = {
      "attendance": 64200,
      "stadium_capacity": 80000,
      "match_minute": 58,
      "entry_rate_per_min": 420,
      "exit_rate_per_min": 115,
      "temperature": 31,
      "humidity": 65,
      "rain_probability": 10,
      "parking_occupancy": 85,
      "metro_arrivals": 2100,
      "bus_arrivals": 500,
      "ticket_scan_rate": 800,
      "security_queue_length": 150,
      "food_court_density": 65,
      "restroom_density": 40,
      "medical_incidents": 2,
      "previous_congestion": 4,
      "gate_open_count": 8,
      "vip_event": 1,
      "special_event": 0,
      "holiday": 0,
      "weekday": "Friday"
    }
    
    # Send a unique Request ID to test tracing
    req_id = str(uuid.uuid4())
    headers = {"X-Request-ID": req_id}
    
    response = client.post("/api/v1/predict/crowd", json=payload, headers=headers)
    
    # Verify the response
    assert response.status_code == 200, f"Error: {response.text}"
    data = response.json()
    assert "congestion_score" in data
    assert "risk_level" in data
    
    # Verify the middleware appended the request ID
    assert response.headers.get("X-Request-ID") == req_id

def test_prediction_api_validation_error():
    # Missing required fields
    payload = {
      "attendance": 64200,
      "stadium_capacity": 80000
    }
    
    response = client.post("/api/v1/predict/crowd", json=payload)
    # FastAPI automatically rejects invalid Pydantic models with 422
    assert response.status_code == 422
