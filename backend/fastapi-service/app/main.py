from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.endpoints import auth, users
from app.db.session import engine, Base
from shared.utils.error_handlers import ApplicationError
import logging

# Ensure database tables exist (Development fallbacks)
Base.metadata.create_all(bind=engine)

logger = logging.getLogger("fastapi")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Policy Mapping
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers mapping
@app.exception_handler(ApplicationError)
async def application_error_handler(request: Request, exc: ApplicationError):
    logger.error(f"Application exception error: {exc.message} - Code: {exc.code}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.code, "message": exc.message}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled server exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error_code": "INTERNAL_SERVER_ERROR", "message": "An unhandled server exception has occurred."}
    )

# Routers mounting
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}
