import os
from pydantic_settings import BaseSettings

class EdgeSettings(BaseSettings):
    PROJECT_NAME: str = "StadiumOS-CV-Edge"
    
    # Model Configurations
    YOLO_MODEL: str = os.getenv("EDGE_YOLO_MODEL", "yolov8n.pt")  # YOLOv8 nano model
    CONFIDENCE_THRESHOLD: float = float(os.getenv("EDGE_CONF_THRESHOLD", "0.25"))
    IOU_THRESHOLD: float = float(os.getenv("EDGE_IOU_THRESHOLD", "0.45"))
    FORCE_CPU: bool = False
    
    # Camera Source Configurations
    # USB webcam -> '0', RTSP stream -> 'rtsp://...', local MP4 -> 'path/to/file.mp4'
    CAMERA_SOURCE: str = os.getenv("EDGE_CAMERA_SOURCE", "0")
    RESOLUTION_WIDTH: int = int(os.getenv("EDGE_RES_WIDTH", "640"))
    RESOLUTION_HEIGHT: int = int(os.getenv("EDGE_RES_HEIGHT", "480"))
    TARGET_FPS: int = int(os.getenv("EDGE_TARGET_FPS", "30"))
    FRAME_SKIP: int = int(os.getenv("EDGE_FRAME_SKIP", "2")) # Process every Nth frame if overloaded
    
    # Backend REST & WS Gateway Configurations
    BACKEND_API_URL: str = os.getenv("EDGE_BACKEND_API_URL", "http://localhost:8000")
    BACKEND_WS_URL: str = os.getenv("EDGE_BACKEND_WS_URL", "ws://localhost:8000/ws/live")
    
    CAMERA_ID: str = os.getenv("EDGE_CAMERA_ID", "gate_b_01")
    ZONE_ID: str = os.getenv("EDGE_ZONE_ID", "ZONE_GATE_B")
    
    class Config:
        case_sensitive = True

settings = EdgeSettings()
