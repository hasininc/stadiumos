from fastapi import APIRouter, Depends, status
from src.api.deps import RoleChecker
from src.schemas.prediction import (
    CrowdPredictionRequest, CrowdPredictionResponse,
    QueuePredictionRequest, QueuePredictionResponse,
    VendorPredictionRequest, VendorPredictionResponse,
    ParkingPredictionRequest, ParkingPredictionResponse,
    TransportPredictionRequest, TransportPredictionResponse,
    EmergencyPredictionRequest, EmergencyPredictionResponse
)
from src.services.inference import InferenceService
from src.core.model_registry import model_registry
from typing import List

router = APIRouter()

# RBAC permission group checks
allowed_roles = RoleChecker(["Operations Manager", "Administrator", "Analytics Service", "AI Gateway"])

@router.post("/crowd", response_model=CrowdPredictionResponse, status_code=status.HTTP_200_OK)
def predict_crowd(req: CrowdPredictionRequest, roles: List[str] = Depends(allowed_roles)):
    service = InferenceService()
    return service.predict_crowd_congestion(req)

@router.post("/queue", response_model=QueuePredictionResponse, status_code=status.HTTP_200_OK)
def predict_queue(req: QueuePredictionRequest, roles: List[str] = Depends(allowed_roles)):
    service = InferenceService()
    return service.predict_queue_wait(req)

@router.post("/vendor", response_model=VendorPredictionResponse, status_code=status.HTTP_200_OK)
def predict_vendor(req: VendorPredictionRequest, roles: List[str] = Depends(allowed_roles)):
    service = InferenceService()
    return service.predict_vendor_demand(req)

@router.post("/parking", response_model=ParkingPredictionResponse, status_code=status.HTTP_200_OK)
def predict_parking(req: ParkingPredictionRequest, roles: List[str] = Depends(allowed_roles)):
    service = InferenceService()
    return service.predict_parking_occupancy(req)

@router.post("/transport", response_model=TransportPredictionResponse, status_code=status.HTTP_200_OK)
def predict_transport(req: TransportPredictionRequest, roles: List[str] = Depends(allowed_roles)):
    service = InferenceService()
    return service.predict_transport_delay(req)

@router.post("/emergency", response_model=EmergencyPredictionResponse, status_code=status.HTTP_200_OK)
def predict_emergency(req: EmergencyPredictionRequest, roles: List[str] = Depends(allowed_roles)):
    service = InferenceService()
    return service.predict_emergency_risk(req)

@router.get("/models")
def get_loaded_models(roles: List[str] = Depends(allowed_roles)):
    return model_registry.list_models()

@router.get("/latest")
def get_latest_predictions(roles: List[str] = Depends(allowed_roles)):
    # Returns mock latest predictions summary
    return {
        "status": "success",
        "latest": {
            "crowd_risk": "Low",
            "average_wait_seconds": 120,
            "gate_congestion": "Normal"
        }
    }

@router.get("/history")
def get_predictions_history(roles: List[str] = Depends(allowed_roles)):
    # Returns mock historical predictions list
    return [
        {"model": "crowd_congestion", "value": 1500, "confidence": 0.94, "timestamp": "2026-07-07T12:00:00Z"},
        {"model": "queue_wait", "value": 300, "confidence": 0.92, "timestamp": "2026-07-07T12:05:00Z"}
    ]

@router.get("/health")
def get_health():
    return {"status": "healthy", "service": "ML Prediction Service"}
