import pytest
from fastapi import status
from app.models.auth import User, Role
from app.models.crowd import Stadium, Zone
from app.models.navigation import MapNode, MapEdge
from app.api.deps import get_current_user

@pytest.fixture
def mock_ops_manager(db_session):
    ops_role = Role(name="Operations Manager", description="Operations Coordinator")
    db_session.add(ops_role)
    db_session.commit()

    user = User(
        id="usr-ops-2",
        email="coordinator@stadiumos.com",
        password_hash="hashedpassword",
        is_active=True,
        is_verified=True
    )
    user.roles.append(ops_role)
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def seed_e2e_nodes_and_edges(db_session):
    stadium = Stadium(id="stad-01", name="MetLife Stadium", location="NJ", total_capacity=80000)
    zone1 = Zone(id="ZONE_GATE_A", name="Entrance Gate A", stadium_id="stad-01", max_capacity=2000, status="Normal")
    zone2 = Zone(id="ZONE_SEC_104", name="Concourse Section 104", stadium_id="stad-01", max_capacity=2000, status="Normal")
    
    db_session.add(stadium)
    db_session.add(zone1)
    db_session.add(zone2)
    
    n1 = MapNode(id="NODE-GATE-A", name="Entrance Gate A", zone_id="ZONE_GATE_A", type="Gate", x=0.0, y=0.0, floor="1", is_wheelchair_accessible=True)
    n2 = MapNode(id="NODE-CONC-1", name="Concourse Section 104", zone_id="ZONE_SEC_104", type="Concourse", x=10.0, y=10.0, floor="1", is_wheelchair_accessible=True)
    
    db_session.add(n1)
    db_session.add(n2)
    
    e1 = MapEdge(source_node_id="NODE-GATE-A", target_node_id="NODE-CONC-1", distance=15.0, base_weight=1.0, current_weight=1.0, is_wheelchair_accessible=True)
    db_session.add(e1)
    
    db_session.commit()
    return stadium, zone1, zone2

def test_full_operational_cognitive_loop_e2e(client, mock_ops_manager, seed_e2e_nodes_and_edges, mock_redis_and_kafka):
    client.app.dependency_overrides[get_current_user] = lambda: mock_ops_manager

    # 1. Computer Vision detects overcrowding -> uploads snapshot
    snapshot_response = client.post(
        "/api/v1/crowd/snapshot",
        json={"zone_id": "ZONE_GATE_A", "headcount": 1950} # 97.5% occupancy -> Critical
    )
    assert snapshot_response.status_code == status.HTTP_201_CREATED
    assert snapshot_response.json()["occupancy_pct"] == 97.5
    
    # 2. Assert Crowd Service has broadcasted a threshold breach event
    published_topics = [e["topic"] for e in mock_redis_and_kafka]
    assert "stadiumos.crowd.threshold-exceeded" in published_topics

    # 3. AI Gateway receives query from Fan asking for help
    ai_chat_response = client.post(
        "/api/v1/ai/chat",
        json={
            "message": "Crowd is too packed at Gate A. What is the least crowded gate?",
            "session_id": "test_e2e_chat_session"
        }
    )
    assert ai_chat_response.status_code == status.HTTP_200_OK
    assert "Gate" in ai_chat_response.json()["response_text"]

    # 4. Dispatcher logs an active emergency incident
    incident_response = client.post(
        "/api/v1/emergencies/",
        json={
            "title": "Gate Congestion Overcrowding",
            "description": "Heavy crowding bottlenecks at Entrance Gate A.",
            "type": "Crowd Stampede Risk",
            "severity": "Critical",
            "zone_id": "ZONE_GATE_A"
        }
    )
    assert incident_response.status_code == status.HTTP_201_CREATED
    assert incident_response.json()["status"] == "Reported"

    # 5. Navigation recalculates routes avoiding congested/emergency zones
    reroute_response = client.post(
        "/api/v1/navigation/reroute",
        json={
            "current_node_id": "NODE-GATE-A",
            "end_node_id": "NODE-CONC-1",
            "avoid_zones": ["ZONE_GATE_A"]
        }
    )
    assert reroute_response.status_code == status.HTTP_200_OK
    assert reroute_response.json()["routing_profile"] == "Rerouted"
    
    client.app.dependency_overrides.clear()
