import pytest
from datetime import datetime
from fastapi import status
from app.models.auth import User, Role
from app.models.emergency import Incident
from app.api.deps import get_current_user

@pytest.fixture
def mock_responder_roles(db_session):
    med_role = Role(name="Medical Staff", description="Emergency Responder")
    sec_role = Role(name="Security Staff", description="Security Patrol")
    admin_role = Role(name="Administrator", description="Full Access")
    
    db_session.add(med_role)
    db_session.add(sec_role)
    db_session.add(admin_role)
    db_session.commit()
    return med_role, sec_role, admin_role

@pytest.fixture
def mock_medical_staff(db_session, mock_responder_roles):
    med_role = mock_responder_roles[0]
    user = User(id="med-1", email="medic@stadiumos.com", password_hash="hashed", is_active=True)
    user.roles.append(med_role)
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def mock_admin_user(db_session, mock_responder_roles):
    admin_role = mock_responder_roles[2]
    user = User(id="admin-1", email="admin@stadiumos.com", password_hash="hashed", is_active=True)
    user.roles.append(admin_role)
    db_session.add(user)
    db_session.commit()
    return user

def test_create_incident_computes_correct_sla(client, mock_admin_user):
    client.app.dependency_overrides[get_current_user] = lambda: mock_admin_user
    
    response = client.post(
        "/api/v1/emergencies/",
        json={
            "title": "Heat Stroke at Concourse A",
            "description": "Spectator collapsed on stairs due to heat stress.",
            "type": "Medical Emergency",
            "severity": "Critical",
            "zone_id": "ZONE_GATE_A"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["status"] == "Reported"
    assert response.json()["severity"] == "Critical"
    assert "sla_due_at" in response.json()
    
    client.app.dependency_overrides.clear()

def test_assign_medical_incident_to_non_medical_staff_fails(client, mock_admin_user, db_session):
    client.app.dependency_overrides[get_current_user] = lambda: mock_admin_user

    # Onboard security user (non-medical)
    sec_role = db_session.query(Role).filter(Role.name == "Security Staff").first()
    sec_user = User(id="sec-1", email="guard@stadiumos.com", password_hash="hashed", is_active=True)
    sec_user.roles.append(sec_role)
    db_session.add(sec_user)
    db_session.commit()

    # Create medical incident
    incident = Incident(
        id="inc-99",
        title="Heat Stroke",
        description="Spectator collapsed",
        type="Medical Emergency",
        severity="Critical",
        zone_id="ZONE_GATE_A",
        sla_due_at=datetime.utcnow()
    )
    db_session.add(incident)
    db_session.commit()

    # Attempt to assign medical incident to security guard
    response = client.patch(
        f"/api/v1/emergencies/{incident.id}/assign",
        json={"assigned_user_id": "sec-1"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    client.app.dependency_overrides.clear()
