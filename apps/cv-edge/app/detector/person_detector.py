import logging
import torch
from ultralytics import YOLO
from typing import Any

logger = logging.getLogger("cv-edge")

class PersonDetector:
    def __init__(self, model_name: str = "yolov8n.pt", conf_thresh: float = 0.25, iou_thresh: float = 0.45, force_cpu: bool = False):
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        
        # 1. Automatic hardware accelerator query (MPS for Apple Silicon, CUDA, or CPU)
        if force_cpu:
            self.device = "cpu"
        else:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
                
        logger.info(f"Loading YOLO person detector '{model_name}' on target device: {self.device}...")
        self.model = YOLO(model_name)
        
    def detect_and_track(self, frame: Any) -> Any:
        """
        Runs YOLOv8 model object tracking (ByteTrack persistent tracking).
        Filters only class '0' (Person).
        """
        results = self.model.track(
            source=frame,
            classes=[0],          # 0 = Person class in COCO
            conf=self.conf_thresh,
            iou=self.iou_thresh,
            persist=True,        # Retain tracking states between sequential frames
            device=self.device,
            verbose=False
        )
        return results[0] if results else None
