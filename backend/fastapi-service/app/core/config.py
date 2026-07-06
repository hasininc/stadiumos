import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "StadiumOS"
    API_V1_STR: str = "/api/v1"
    
    # Security Configurations
    SECRET_KEY: str = os.getenv("STADIUMOS_GATEWAY_JWT_SECRET", "super-secret-key-development-value-change-me-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database Configurations
    PG_HOST: str = os.getenv("STADIUMOS_PG_HOST", "localhost")
    PG_PORT: str = os.getenv("STADIUMOS_PG_PORT", "5432")
    PG_DB: str = os.getenv("STADIUMOS_PG_DB", "stadiumos_db")
    PG_USER: str = os.getenv("STADIUMOS_PG_USER", "stadiumos_app_user")
    PG_PASS: str = os.getenv("STADIUMOS_PG_PASS", "local_dev_password_change_me")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    # Redis Configurations
    REDIS_HOST: str = os.getenv("STADIUMOS_REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("STADIUMOS_REDIS_PORT", "6379"))

    # CORS Configurations
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://*.fifa2026.org"]

    class Config:
        case_sensitive = True

settings = Settings()
