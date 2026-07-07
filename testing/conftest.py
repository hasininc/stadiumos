import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Register FastAPI backend path to system modules locator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/fastapi-service')))

from app.main import app
from app.db.session import Base, get_db

# Create testing sqlite memory database engine pool
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_redis_and_kafka(monkeypatch):
    # Simulated Cache Index mapping
    cache_store = {}

    def mock_set(key, value, ttl=300):
        cache_store[key] = value

    def mock_get(key):
        return cache_store.get(key)

    def mock_delete(key):
        if key in cache_store:
            del cache_store[key]

    # Patch Redis operations
    from app.core.redis_client import redis_client
    monkeypatch.setattr(redis_client, "set_cache", mock_set)
    monkeypatch.setattr(redis_client, "get_cache", mock_get)
    monkeypatch.setattr(redis_client, "delete_cache", mock_delete)

    # Patch Kafka operations (capture published events in list)
    published_events = []

    def mock_publish(topic, key, payload):
        published_events.append({"topic": topic, "key": key, "payload": payload})

    from app.core.kafka_client import kafka_client
    monkeypatch.setattr(kafka_client, "publish_event", mock_publish)
    monkeypatch.setattr(kafka_client, "producer", True) # Mock loaded producer

    yield published_events
