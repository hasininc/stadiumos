from fastapi import FastAPI, Request, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import time
from app.core.config import settings
from app.api.v1.endpoints import auth, users, crowd, notifications, emergencies, navigation, vendors, prediction
from app.core.security_layer import SecureHeadersMiddleware
from app.db.session import engine, Base
from app.db.seed import seed_database
from shared.utils.error_handlers import ApplicationError
from app.core.websocket import live_ws_manager
import logging

# Ensure database tables exist (Development fallbacks)
Base.metadata.create_all(bind=engine)
seed_database()

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

# Global Zero-Trust Secure Headers and Rate Limiter Middleware
app.add_middleware(SecureHeadersMiddleware)

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
app.include_router(crowd.router, prefix=f"{settings.API_V1_STR}/crowd", tags=["crowd"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])
app.include_router(emergencies.router, prefix=f"{settings.API_V1_STR}/emergencies", tags=["emergencies"])
app.include_router(navigation.router, prefix=f"{settings.API_V1_STR}/navigation", tags=["navigation"])
app.include_router(vendors.router, prefix=f"{settings.API_V1_STR}/vendors", tags=["vendors"])
app.include_router(prediction.router, prefix=f"{settings.API_V1_STR}/predict", tags=["prediction"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    await live_ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type")
                if msg_type == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": time.time()})
                elif msg_type == "SimulationStarted":
                    await live_ws_manager.start_simulation()
                    await live_ws_manager.broadcast({"type": "SimulationStarted", "data": {}})
                elif msg_type == "SimulationStopped":
                    await live_ws_manager.stop_simulation()
                    await live_ws_manager.broadcast({"type": "SimulationStopped", "data": {}})
                elif msg_type == "SimulationReset":
                    await live_ws_manager.broadcast({"type": "SimulationReset", "data": {}})
            except Exception:
                await websocket.send_json({"pong": True, "received": data})
    except WebSocketDisconnect:
        await live_ws_manager.disconnect(websocket)
        logger.info("Live WebSocket client disconnected")
