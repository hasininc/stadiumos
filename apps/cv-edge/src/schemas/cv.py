from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class CameraCreate(BaseModel):
    id: str
    name: str
    rtsp_url: str
    zone_id: str
    status: Optional[str] = "Active"

class CameraResponse(CameraCreate):
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class StreamResponse(BaseModel):
    camera_id: str
    rtsp_url: str
    status: str # "Streaming", "Disconnected", "Error"

class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float

class DetectionResponse(BaseModel):
    event_id: str
    camera_id: str
    zone_id: str
    timestamp: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    detection_type: str # "CrowdCount", "QueueLength", "Fall", "SuspiciousObject", "Intrusion"
    bounding_box_metadata: Optional[List[BoundingBox]] = None

class HeatmapResponse(BaseModel):
    camera_id: str
    zone_id: str
    heatmap_matrix: List[List[float]] # Grid representation of density values
    timestamp: str
