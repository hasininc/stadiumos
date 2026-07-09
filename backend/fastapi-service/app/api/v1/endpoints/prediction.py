import time
import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.services.prediction_service import prediction_service

logger = logging.getLogger("fastapi")
router = APIRouter()

# ──────────────────────────────────────────────
# Pydantic Schemas with Range Validations
# ──────────────────────────────────────────────
class PredictionInput(BaseModel):
    attendance: int = Field(..., ge=0, le=100000, description="Current match attendance", json_schema_extra={"example": 64200})
    stadium_capacity: int = Field(..., ge=10000, le=120000, description="Total seating capacity", json_schema_extra={"example": 80000})
    match_minute: int = Field(..., ge=-90, le=150, description="Match clock minute", json_schema_extra={"example": 58})
    entry_rate_per_min: float = Field(..., ge=0.0, le=2000.0, description="Gate entries per minute", json_schema_extra={"example": 420.0})
    exit_rate_per_min: float = Field(..., ge=0.0, le=2000.0, description="Gate exits per minute", json_schema_extra={"example": 115.0})
    temperature: float = Field(..., ge=-20.0, le=55.0, description="Air temperature in degrees Celsius", json_schema_extra={"example": 31.0})
    humidity: float = Field(..., ge=0.0, le=100.0, description="Humidity percentage", json_schema_extra={"example": 63.0})
    rain_probability: float = Field(..., ge=0.0, le=100.0, description="Rain probability percentage", json_schema_extra={"example": 10.0})
    parking_occupancy: float = Field(..., ge=0.0, le=100.0, description="Parking occupancy rate percentage", json_schema_extra={"example": 74.0})
    metro_arrivals: int = Field(..., ge=0, le=10000, description="Metro arrival rate in passengers/min", json_schema_extra={"example": 890})
    bus_arrivals: int = Field(..., ge=0, le=10000, description="Bus arrival rate in passengers/min", json_schema_extra={"example": 410})
    ticket_scan_rate: float = Field(..., ge=0.0, le=2000.0, description="Ticket validation scans per minute", json_schema_extra={"example": 370.0})
    security_queue_length: float = Field(..., ge=0.0, le=5000.0, description="Security queues count across checkpoints", json_schema_extra={"example": 185.0})
    food_court_density: float = Field(..., ge=0.0, le=100.0, description="Food concourse queue occupancy percentage", json_schema_extra={"example": 67.0})
    restroom_density: float = Field(..., ge=0.0, le=100.0, description="Restroom corridors occupancy percentage", json_schema_extra={"example": 49.0})
    medical_incidents: int = Field(..., ge=0, le=100, description="Active dispatcher medical events", json_schema_extra={"example": 2})
    previous_congestion: float = Field(..., ge=0.0, le=100.0, description="Past window congestion score", json_schema_extra={"example": 71.0})
    gate_open_count: int = Field(..., ge=1, le=100, description="Count of open entry gates", json_schema_extra={"example": 14})
    vip_event: bool = Field(..., description="VIP attendance security active flag", json_schema_extra={"example": False})
    special_event: bool = Field(..., description="Special high-interest match flag", json_schema_extra={"example": True})
    holiday: bool = Field(..., description="Holiday matchday schedule indicator", json_schema_extra={"example": False})
    weekday: str = Field(..., description="Name of the day of the week", json_schema_extra={"example": "Sunday"})

    @field_validator('weekday')
    @classmethod
    def validate_weekday(cls, v: str) -> str:
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if v.lower() not in days:
            raise ValueError("Weekday must be a valid day name (e.g. 'Monday', 'Sunday').")
        return v

class FactorImpact(BaseModel):
    feature: str = Field(..., description="Input feature name")
    impact: float = Field(..., description="Relative local percentage contribution")

class PredictionOutput(BaseModel):
    risk_level: str = Field(..., description="Predicted risk band: LOW, MEDIUM, HIGH, CRITICAL", json_schema_extra={"example": "HIGH"})
    congestion_score: float = Field(..., description="Predicted continuous congestion level", json_schema_extra={"example": 91.4})
    queue_prediction: int = Field(..., description="Predicted average security wait time in minutes", json_schema_extra={"example": 18})
    confidence: float = Field(..., description="Prediction confidence score probability", json_schema_extra={"example": 0.95})
    top_factors: List[FactorImpact] = Field(..., description="Features that contributed most to the prediction")
    timestamp: str = Field(..., description="Timestamp of inference execution", json_schema_extra={"example": "2026-07-09T01:32:00Z"})

# ──────────────────────────────────────────────
# API Route Endpoint
# ──────────────────────────────────────────────
@router.post(
    "/crowd",
    response_model=PredictionOutput,
    status_code=status.HTTP_200_OK,
    summary="Predict Stadium Crowd Congestion Metrics",
    description="Feed live matchday indicators into the ML model to receive congestion scores, queue waiting predictions, and local impact factors."
)
async def predict_crowd(payload: PredictionInput):
    start_time = time.time()
    try:
        raw_dict = payload.model_dump()
        res = prediction_service.predict(raw_dict)
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Log metric analytics
        logger.info(
            f"Prediction finished in {duration_ms:.2f}ms | "
            f"Risk Level: {res['risk_level']} | "
            f"Congestion Score: {res['congestion_score']} | "
            f"Confidence: {res['confidence']}"
        )
        
        return {
            "risk_level": res["risk_level"],
            "congestion_score": res["congestion_score"],
            "queue_prediction": res["queue_prediction"],
            "confidence": res["confidence"],
            "top_factors": res["top_factors"],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Inference prediction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Predictive pipeline failure: {str(e)}"
        )
