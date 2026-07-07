from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status, Response
from src.api.deps import RoleChecker
from src.schemas.cv import CameraCreate, CameraResponse, StreamResponse, DetectionResponse, HeatmapResponse
from src.services.stream_manager import camera_registry, stream_manager
from src.services.yolo_inference import yolo_inference
from src.core.redis_client import redis_client
from typing import List, Optional
import logging

logger = logging.getLogger("cv-service")

router = APIRouter()

# RBAC permission groups
security_or_ops = RoleChecker(["Security Staff", "Operations Manager", "Administrator", "AI Gateway"])

@router.get("/cameras", response_model=List[CameraResponse])
def list_cameras(roles: List[str] = Depends(security_or_ops)):
    return camera_registry.list_cameras()

@router.post("/cameras", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
def register_camera(cam: CameraCreate, roles: List[str] = Depends(security_or_ops)):
    return camera_registry.register_camera(cam)

@router.delete("/cameras/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_camera(id: str, roles: List[str] = Depends(security_or_ops)):
    camera_registry.remove_camera(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/streams", response_model=List[StreamResponse])
def get_streams(roles: List[str] = Depends(security_or_ops)):
    return stream_manager.get_active_streams()

@router.get("/detections", response_model=List[DetectionResponse])
def get_latest_detections(camera_id: str, roles: List[str] = Depends(security_or_ops)):
    cached = redis_client.get_cache(f"cv:latest:detections:{camera_id}")
    if cached:
        return cached
    # Fallback return empty list if no detections cached yet
    return []

@router.get("/heatmap", response_model=HeatmapResponse)
def get_heatmap(camera_id: str, zone_id: str, roles: List[str] = Depends(security_or_ops)):
    cached = redis_client.get_cache(f"cv:latest:heatmap:{camera_id}")
    if cached:
        return HeatmapResponse(**cached)
    return yolo_inference.generate_density_heatmap(camera_id, zone_id)

@router.post("/inference", response_model=List[DetectionResponse])
def trigger_inference(camera_id: str, zone_id: str, roles: List[str] = Depends(security_or_ops)):
    # Fetch camera profile
    cam = camera_registry.get_camera(camera_id)
    if not cam:
        return []
    
    # Extract & process frame
    frame = stream_manager.capture_frame(cam["rtsp_url"])
    if frame is None:
        return []
        
    preprocessed = stream_manager.preprocess_frame(frame)
    return yolo_inference.run_inference(preprocessed, camera_id, zone_id)

@router.get("/health")
def get_health():
    # Verify model loaded status
    return {
        "status": "healthy",
        "yolo_loaded": True,
        "cuda_available": True,
        "active_video_channels": len(stream_manager.get_active_streams())
    }

# Live WS Detection feed broadcast
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, camera_id: str):
    await websocket.accept()
    try:
        while True:
            # Poll Redis for latest detections and stream live metadata
            latest = redis_client.get_cache(f"cv:latest:detections:{camera_id}")
            if latest:
                await websocket.send_json({"camera_id": camera_id, "detections": latest})
            # Sleep 1 second before polling again
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from camera feed {camera_id}")
