import pytest
from fastapi import status
from app.models.auth import User, Role
from app.models.crowd import Stadium, Zone
from app.api.deps import get_current_user, PermissionChecker

@pytest.fixture
def mock_admin_user(db_session):
    admin_role = Role(name="Administrator", description="Full Access Admin")
    db_session.add(admin_role)
    db_session.commit()

    user = User(
        id="usr-admin-1",
        email="admin@stadiumos.com",
        password_hash="hashedpassword",
        is_active=True,
        is_verified=True
    )
    user.roles.append(admin_role)
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_stadium_and_zone(db_session):
    stadium = Stadium(id="stad-01", name="MetLife Stadium", location="NJ", total_capacity=80000)
    zone = Zone(id="ZONE_GATE_A", name="Entrance Gate A", stadium_id="stad-01", max_capacity=2000, status="Normal")
    db_session.add(stadium)
    db_session.add(zone)
    db_session.commit()
    return stadium, zone

def test_record_snapshot_calculates_occupancy_correctly(client, test_stadium_and_zone, mock_admin_user, monkeypatch):
    # Override get_current_user dependency injection
    def mock_get_current_user():
        return mock_admin_user
    client.app.dependency_overrides[get_current_user] = mock_get_current_user
    
    # Send snapshot: headcount 1000 out of max 2000 (50% occupancy)
    response = client.post(
        "/api/v1/crowd/snapshot",
        json={"zone_id": "ZONE_GATE_A", "headcount": 1000}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["occupancy_pct"] == 50.0
    client.app.dependency_overrides.clear()

def test_snapshot_threshold_breach_triggers_alert_status_transition(client, test_stadium_and_zone, mock_admin_user, mock_redis_and_kafka):
    def mock_get_current_user():
        return mock_admin_user
    client.app.dependency_overrides[get_current_user] = mock_get_current_user

    # Send snapshot: headcount 1900 out of max 2000 (95% occupancy -> Critical)
    client.post(
        "/api/v1/crowd/snapshot",
        json={"zone_id": "ZONE_GATE_A", "headcount": 1900}
    )
    
    # Assert threshold breach event published to Kafka
    published_topics = [e["topic"] for e in mock_redis_and_kafka]
    assert "stadiumos.crowd.threshold-exceeded" in published_topics
    client.app.dependency_overrides.clear()
