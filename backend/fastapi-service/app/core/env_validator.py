import os
import sys
import logging

logger = logging.getLogger("fastapi")

def validate_environment():
    """
    Validates required environment variables on startup.
    Prevents the application from booting into a degraded or insecure state.
    """
    environment = os.getenv("ENVIRONMENT", "development")
    
    # 1. Validate Secrets in Production
    if environment == "production":
        secret_key = os.getenv("STADIUMOS_GATEWAY_JWT_SECRET")
        if not secret_key or secret_key == "super-secret-key-development-value-change-me-in-production":
            logger.critical("CRITICAL ERROR: STADIUMOS_GATEWAY_JWT_SECRET is using the default development value in PRODUCTION!")
            sys.exit(1)
            
        db_pass = os.getenv("STADIUMOS_PG_PASS")
        if not db_pass or db_pass == "local_dev_password_change_me":
            logger.critical("CRITICAL ERROR: STADIUMOS_PG_PASS is using the default development value in PRODUCTION!")
            sys.exit(1)
            
    # 2. Validate Copilot Requirements
    llm_provider = (os.getenv("COPILOT_LLM_PROVIDER") or os.getenv("LLM_PROVIDER") or "gemini").lower()
    if llm_provider == "google" or llm_provider == "gemini":
        if not os.getenv("GEMINI_API_KEY"):
            logger.warning("WARNING: GEMINI_API_KEY is not set. The AI Copilot will fail to answer queries.")
    elif llm_provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("WARNING: OPENAI_API_KEY is not set. The AI Copilot will fail to answer queries.")
            
    logger.info(f"Environment validation passed. Running in {environment} mode.")
