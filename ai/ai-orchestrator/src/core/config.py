import os
from pydantic_settings import BaseSettings

class AISettings(BaseSettings):
    PROJECT_NAME: str = "StadiumOS-AI-Orchestrator"
    API_V1_STR: str = "/api/v1"
    
    # JWT Security Configurations
    SECRET_KEY: str = os.getenv("STADIUMOS_GATEWAY_JWT_SECRET", "super-secret-key-development-value-change-me-in-production")
    
    # OpenAI Configurations
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "mock-openai-key-for-dev")
    OPENAI_MODEL_NAME: str = os.getenv("STADIUMOS_OPENAI_MODEL", "gpt-4o")

    # Redis Configurations
    REDIS_HOST: str = os.getenv("STADIUMOS_REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("STADIUMOS_REDIS_PORT", "6379"))
    
    # Kafka Configurations
    KAFKA_BROKERS: str = os.getenv("STADIUMOS_KAFKA_BROKERS", "localhost:9092")

    # CORS Configurations
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://*.fifa2026.org"]

    class Config:
        case_sensitive = True

settings = AISettings()
