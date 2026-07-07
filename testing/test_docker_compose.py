import os
import yaml

def test_docker_compose_files_exist():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docker-compose.yml'))
    override_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docker-compose.override.yml'))
    
    assert os.path.exists(base_path) is True
    assert os.path.exists(override_path) is True

def test_docker_compose_override_syntax_and_services():
    override_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docker-compose.override.yml'))
    
    with open(override_path, 'r') as f:
        config = yaml.safe_load(f)
        
    assert "services" in config
    services = config["services"]
    
    # Check that crucial applications are defined
    expected_services = ["fastapi-service", "ai-orchestrator", "ml-service", "cv-service", "ops-dashboard"]
    for s in expected_services:
        assert s in services
        
    # Check security credentials constraints (non-root permissions check)
    fastapi = services["fastapi-service"]
    assert fastapi["user"] == "10001:10001"
    assert "no-new-privileges:true" in fastapi["security_opt"]
    
    # Check that dependency hierarchies are set up
    assert "postgres" in fastapi["depends_on"]
    assert "redis" in fastapi["depends_on"]
    assert "kafka" in fastapi["depends_on"]
