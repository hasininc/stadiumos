import os
from typing import Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "StadiumOS"
    API_V1_STR: str = "/api/v1"
    
    # Security Configurations
    SECRET_KEY: str = os.getenv("STADIUMOS_GATEWAY_JWT_SECRET", "super-secret-key-development-value-change-me-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database Configurations
    PG_HOST: str = Field(default="localhost", validation_alias="STADIUMOS_PG_HOST")
    PG_PORT: str = Field(default="5432", validation_alias="STADIUMOS_PG_PORT")
    PG_DB: str = Field(default="stadiumos_db", validation_alias="STADIUMOS_PG_DB")
    PG_USER: str = Field(default="stadiumos_app_user", validation_alias="STADIUMOS_PG_USER")
    PG_PASS: str = Field(default="local_dev_password_change_me", validation_alias="STADIUMOS_PG_PASS")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    # Redis Configurations
    REDIS_HOST: str = os.getenv("STADIUMOS_REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("STADIUMOS_REDIS_PORT", "6379"))

    # Kafka Configurations
    STADIUMOS_KAFKA_BROKERS: str = os.getenv("STADIUMOS_KAFKA_BROKERS", "localhost:9092")

    # CORS Configurations
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=True,
    extra="ignore",
)
settings = Settings()
