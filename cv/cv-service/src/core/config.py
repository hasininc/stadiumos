import os
from pydantic_settings import BaseSettings

class CVSettings(BaseSettings):
    PROJECT_NAME: str = "StadiumOS-CV-Service"
    API_V1_STR: str = "/api/v1"
    
    # JWT Security Configurations
    SECRET_KEY: str = os.getenv("STADIUMOS_GATEWAY_JWT_SECRET", "super-secret-key-development-value-change-me-in-production")
    
    # Redis Configurations
    REDIS_HOST: str = os.getenv("STADIUMOS_REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("STADIUMOS_REDIS_PORT", "6379"))
    
    # Kafka Configurations
    KAFKA_BROKERS: str = os.getenv("STADIUMOS_KAFKA_BROKERS", "localhost:9092")

    # DB Configurations
    PG_HOST: str = os.getenv("STADIUMOS_PG_HOST", "localhost")
    PG_PORT: str = os.getenv("STADIUMOS_PG_PORT", "5432")
    PG_DB: str = os.getenv("STADIUMOS_PG_DB", "stadiumos_db")
    PG_USER: str = os.getenv("STADIUMOS_PG_USER", "stadiumos_app_user")
    PG_PASS: str = os.getenv("STADIUMOS_PG_PASS", "local_dev_password_change_me")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    # YOLO Configurations
    YOLO_MODEL_PATH: str = os.getenv("STADIUMOS_YOLO_MODEL_PATH", "yolo11n.pt")
    INFERENCE_CONFIDENCE_THRESHOLD: float = 0.25

    # CORS Configurations
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://*.fifa2026.org"]

    class Config:
        case_sensitive = True

settings = CVSettings()
