from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
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
    "previous_congestion": 40,
    "gate_open_count": 14,
    "vip_event": True,
    "special_event": False,
    "holiday": False,
    "weekday": "Friday",
    "security_staff": 342,
    "gate_capacity": 95,
    "closed_gates": [],
    "incident_count": 3,
    "incident_type": "Crowd Congestion",
    "forecast_hours": 4,
}


def test_operations_prediction_returns_all_ml_modules():
    response = client.post("/api/v1/predict/operations", json=VALID_PAYLOAD)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "ready"
    assert data["legacy_crowd"]["risk_level"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert data["crowd_congestion"]
    assert data["queue_times"]
    assert len(data["attendance_forecast"]) == VALID_PAYLOAD["forecast_hours"] + 1
    assert data["crowd_risk"]
    assert data["emergency_severity"]["predicted_severity"] in {
        "Low",
        "Medium",
        "High",
        "Critical",
    }
    assert data["security_recommendation"]["recommended_total_personnel"] > 0
    assert data["medical_demand"]
    assert data["vendor_demand"]
    assert data["parking_occupancy"]
    assert data["traffic_flow"]
    assert data["weather_impact"]["operational_risk_impact_pct"] >= 0
    assert data["recommendations"]


def test_predictions_include_confidence_explanations_and_factors():
    data = client.post("/api/v1/predict/operations", json=VALID_PAYLOAD).json()
    sample_predictions = [
        data["crowd_congestion"][0],
        data["queue_times"][0],
        data["attendance_forecast"][0],
        data["crowd_risk"][0],
        data["medical_demand"][0],
        data["vendor_demand"][0],
        data["parking_occupancy"][0],
        data["traffic_flow"][0],
        data["weather_impact"],
    ]

    for prediction in sample_predictions:
        assert 0 <= prediction["confidence"] <= 100
        assert prediction["explanation"]
        assert "top_factors" in prediction


def test_individual_model_endpoints_are_exposed():
    endpoints = [
        "/api/v1/predict/crowd/zones",
        "/api/v1/predict/queues/gates",
        "/api/v1/predict/attendance/forecast",
        "/api/v1/predict/risk/zones",
        "/api/v1/predict/emergency/severity",
        "/api/v1/predict/security/resources",
        "/api/v1/predict/medical/demand",
        "/api/v1/predict/vendors/demand",
        "/api/v1/predict/parking/occupancy",
        "/api/v1/predict/traffic/flow",
        "/api/v1/predict/weather/impact",
        "/api/v1/predict/recommendations",
    ]

    for endpoint in endpoints:
        response = client.post(endpoint, json=VALID_PAYLOAD)
        assert response.status_code == 200, endpoint
        assert response.json()


def test_simulation_changes_update_predictions_dynamically():
    baseline = client.post("/api/v1/predict/operations", json=VALID_PAYLOAD).json()
    disrupted_payload = {
        **VALID_PAYLOAD,
        "gate_capacity": 45,
        "gate_open_count": 8,
        "closed_gates": ["GATE_C"],
        "rain_probability": 100,
        "humidity": 92,
        "temperature": 21,
        "security_staff": 240,
        "security_queue_length": 480,
    }
    disrupted = client.post("/api/v1/predict/operations", json=disrupted_payload).json()

    baseline_gate_c = next(
        gate for gate in baseline["queue_times"] if gate["gate_id"] == "GATE_C"
    )
    disrupted_gate_c = next(
        gate for gate in disrupted["queue_times"] if gate["gate_id"] == "GATE_C"
    )

    assert disrupted_gate_c["estimated_wait_minutes"] > baseline_gate_c["estimated_wait_minutes"]
    assert (
        disrupted["weather_impact"]["operational_risk_impact_pct"]
        > baseline["weather_impact"]["operational_risk_impact_pct"]
    )
