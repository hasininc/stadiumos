import cv2
import numpy as np
import logging
from typing import Dict, List, Optional
from datetime import datetime
from src.schemas.cv import CameraCreate, CameraResponse
from shared.utils.error_handlers import ValidationError

logger = logging.getLogger("cv-service")

class CameraRegistry:
    def __init__(self):
        # Simulated database registry for CCTV feeds
        self.registry: Dict[str, dict] = {
            "CAM-01": {
                "id": "CAM-01",
                "name": "Entrance Gate A Camera",
                "rtsp_url": "rtsp://10.240.5.10/stream1",
                "zone_id": "ZONE_GATE_A",
                "status": "Active",
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            "CAM-02": {
                "id": "CAM-02",
                "name": "Concourse Section 104 Camera",
                "rtsp_url": "rtsp://10.240.5.11/stream1",
                "zone_id": "ZONE_SEC_104",
                "status": "Active",
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        }

    def register_camera(self, cam: CameraCreate) -> CameraResponse:
        if cam.id in self.registry:
            raise ValidationError("Camera ID already registered")
        
        cam_dict = cam.dict()
        cam_dict["is_active"] = True
        cam_dict["created_at"] = datetime.utcnow()
        
        self.registry[cam.id] = cam_dict
        return CameraResponse(**cam_dict)

    def remove_camera(self, cam_id: str) -> None:
        if cam_id not in self.registry:
            raise ValidationError("Camera not found")
        del self.registry[cam_id]

    def list_cameras(self) -> List[CameraResponse]:
        return [CameraResponse(**c) for c in self.registry.values()]

    def get_camera(self, cam_id: str) -> Optional[dict]:
        return self.registry.get(cam_id)

class StreamManager:
    def __init__(self, registry: CameraRegistry):
        self.registry = registry

    def get_active_streams(self) -> List[dict]:
        cameras = self.registry.list_cameras()
        streams = []
        for cam in cameras:
            streams.append({
                "camera_id": cam.id,
                "rtsp_url": cam.rtsp_url,
                "status": "Streaming" if cam.is_active else "Disconnected"
            })
        return streams

    def capture_frame(self, rtsp_url: str) -> Optional[np.ndarray]:
        logger.debug(f"Simulating OpenCV capture on RTSP: {rtsp_url}")
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(mock_frame, "StadiumOS CCTV Feed Mock", (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return mock_frame

    def preprocess_frame(self, frame: np.ndarray, target_size: tuple = (640, 640)) -> np.ndarray:
        resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
        normalized = resized.astype(np.float32) / 255.0
        return normalized

# Singleton instances
camera_registry = CameraRegistry()
stream_manager = StreamManager(camera_registry)
