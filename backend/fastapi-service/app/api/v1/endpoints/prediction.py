"""
Prediction endpoint — POST /api/v1/predict/crowd

Accepts live matchday indicators from the ops dashboard, runs them
through the trained CatBoost crowd-density model, and returns
congestion metrics, risk level, confidence, and contributing factors.
"""

import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.services.prediction_service import prediction_service
from ml.stadium_ops import StadiumOperationsInferenceEngine

logger = logging.getLogger("fastapi")
router = APIRouter()
stadium_ops_engine = StadiumOperationsInferenceEngine()


# ──────────────────────────────────────────────
# Pydantic Request / Response Schemas
# ──────────────────────────────────────────────

class PredictionInput(BaseModel):
    """Live matchday telemetry sent by the ops dashboard."""

    attendance: int = Field(
        ..., ge=0, le=100000,
        description="Current match attendance",
        json_schema_extra={"example": 64200},
    )
    stadium_capacity: int = Field(
        ..., ge=10000, le=120000,
        description="Total seating capacity",
        json_schema_extra={"example": 80000},
    )
    match_minute: int = Field(
        ..., ge=-90, le=150,
        description="Match clock minute (negative = pre-match)",
        json_schema_extra={"example": 58},
    )
    entry_rate_per_min: float = Field(
        ..., ge=0.0, le=2000.0,
        description="Gate entries per minute",
        json_schema_extra={"example": 420.0},
    )
    exit_rate_per_min: float = Field(
        ..., ge=0.0, le=2000.0,
        description="Gate exits per minute",
        json_schema_extra={"example": 115.0},
    )
    temperature: float = Field(
        ..., ge=-20.0, le=55.0,
        description="Air temperature in degrees Celsius",
        json_schema_extra={"example": 31.0},
    )
    humidity: float = Field(
        ..., ge=0.0, le=100.0,
        description="Humidity percentage",
        json_schema_extra={"example": 63.0},
    )
    rain_probability: float = Field(
        ..., ge=0.0, le=100.0,
        description="Rain probability percentage",
        json_schema_extra={"example": 10.0},
    )
    parking_occupancy: float = Field(
        ..., ge=0.0, le=100.0,
        description="Parking occupancy rate percentage",
        json_schema_extra={"example": 74.0},
    )
    metro_arrivals: int = Field(
        ..., ge=0, le=10000,
        description="Metro arrival rate in passengers/min",
        json_schema_extra={"example": 890},
    )
    bus_arrivals: int = Field(
        ..., ge=0, le=10000,
        description="Bus arrival rate in passengers/min",
        json_schema_extra={"example": 410},
    )
    ticket_scan_rate: float = Field(
        ..., ge=0.0, le=2000.0,
        description="Ticket validation scans per minute",
        json_schema_extra={"example": 370.0},
    )
    security_queue_length: float = Field(
        ..., ge=0.0, le=5000.0,
        description="Security queues count across checkpoints",
        json_schema_extra={"example": 185.0},
    )
    food_court_density: float = Field(
        ..., ge=0.0, le=100.0,
        description="Food concourse queue occupancy percentage",
        json_schema_extra={"example": 67.0},
    )
    restroom_density: float = Field(
        ..., ge=0.0, le=100.0,
        description="Restroom corridors occupancy percentage",
        json_schema_extra={"example": 49.0},
    )
    medical_incidents: int = Field(
        ..., ge=0, le=100,
        description="Active dispatcher medical events",
        json_schema_extra={"example": 2},
    )
    previous_congestion: float = Field(
        ..., ge=0.0, le=100.0,
        description="Past window congestion score",
        json_schema_extra={"example": 71.0},
    )
    gate_open_count: int = Field(
        ..., ge=1, le=100,
        description="Count of open entry gates",
        json_schema_extra={"example": 14},
    )
    vip_event: bool = Field(
        ...,
        description="VIP attendance security active flag",
        json_schema_extra={"example": False},
    )
    special_event: bool = Field(
        ...,
        description="Special high-interest match flag",
        json_schema_extra={"example": True},
    )
    holiday: bool = Field(
        ...,
        description="Holiday matchday schedule indicator",
        json_schema_extra={"example": False},
    )
    weekday: str = Field(
        ...,
        description="Name of the day of the week",
        json_schema_extra={"example": "Sunday"},
    )
    security_staff: int = Field(
        300,
        ge=0,
        le=1000,
        description="Security personnel currently deployed",
        json_schema_extra={"example": 342},
    )
    gate_capacity: float = Field(
        100.0,
        ge=0.0,
        le=120.0,
        description="Overall gate throughput percentage from what-if simulation",
        json_schema_extra={"example": 92.0},
    )
    closed_gates: List[str] = Field(
        default_factory=list,
        description="Gate IDs that are offline or closed",
        json_schema_extra={"example": ["GATE_C"]},
    )
    incident_count: int = Field(
        0,
        ge=0,
        le=500,
        description="Count of active operational incidents",
        json_schema_extra={"example": 3},
    )
    incident_type: str = Field(
        "Operational",
        description="Primary incident type when severity prediction is requested",
        json_schema_extra={"example": "Crowd Congestion"},
    )
    forecast_hours: int = Field(
        6,
        ge=1,
        le=12,
        description="Number of hourly attendance forecast steps to return",
        json_schema_extra={"example": 6},
    )

    @field_validator("weekday")
    @classmethod
    def validate_weekday(cls, v: str) -> str:
        valid = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
        if v.lower() not in valid:
            raise ValueError("Weekday must be a valid day name (e.g. 'Monday', 'Sunday').")
        return v


class FactorImpact(BaseModel):
    """Single feature's contribution to the prediction."""

    feature: str = Field(..., description="Input feature name")
    impact: float = Field(..., description="Relative percentage contribution")


class PredictionOutput(BaseModel):
    """Composite response containing both new ML fields and legacy
    dashboard-compatible fields."""

    # New ML fields
    predicted_occupancy: int = Field(
        ...,
        description="Predicted crowd occupancy after 10 minutes",
        json_schema_extra={"example": 68500},
    )
    confidence: float = Field(
        ...,
        description="Prediction confidence score (0.0–1.0)",
        json_schema_extra={"example": 0.92},
    )

    # Legacy dashboard fields
    risk_level: str = Field(
        ...,
        description="Predicted risk band: LOW, MEDIUM, HIGH, CRITICAL",
        json_schema_extra={"example": "HIGH"},
    )
    congestion_score: float = Field(
        ...,
        description="Predicted congestion level (0–100)",
        json_schema_extra={"example": 85.6},
    )
    queue_prediction: int = Field(
        ...,
        description="Predicted average security wait time in minutes",
        json_schema_extra={"example": 18},
    )
    top_factors: List[FactorImpact] = Field(
        ...,
        description="Features that contributed most to the prediction",
    )
    timestamp: str = Field(
        ...,
        description="ISO-8601 timestamp of inference execution",
        json_schema_extra={"example": "2026-07-09T13:10:00Z"},
    )


class OperationsPredictionOutput(BaseModel):
    """Full AI stadium operations prediction bundle."""

    status: str
    source: str
    generated_at: str
    model_version: str
    training_rows: int
    evaluations: Dict[str, Dict[str, Any]]
    legacy_crowd: PredictionOutput
    crowd_congestion: List[Dict[str, Any]]
    queue_times: List[Dict[str, Any]]
    attendance_forecast: List[Dict[str, Any]]
    crowd_risk: List[Dict[str, Any]]
    emergency_severity: Dict[str, Any]
    security_recommendation: Dict[str, Any]
    medical_demand: List[Dict[str, Any]]
    vendor_demand: List[Dict[str, Any]]
    parking_occupancy: List[Dict[str, Any]]
    traffic_flow: List[Dict[str, Any]]
    weather_impact: Dict[str, Any]
    recommendations: List[Dict[str, Any]]


# ──────────────────────────────────────────────
# API Route
# ──────────────────────────────────────────────

@router.post(
    "/crowd",
    response_model=PredictionOutput,
    status_code=status.HTTP_200_OK,
    summary="Predict Stadium Crowd Congestion Metrics",
    description=(
        "Feed live matchday indicators into the trained CatBoost model "
        "to receive predicted occupancy, congestion scores, queue wait "
        "estimates, risk level, confidence, and top contributing factors."
    ),
)
async def predict_crowd(payload: PredictionInput):
    """Run inference against the trained crowd-density model."""
    start = time.time()

    if not prediction_service.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model is not loaded. The prediction service is temporarily unavailable.",
        )

    try:
        result = prediction_service.predict(payload.model_dump())
        duration_ms = (time.time() - start) * 1000

        logger.info(
            "Prediction completed in %.2fms | Risk: %s | Congestion: %.1f | Confidence: %.2f",
            duration_ms,
            result["risk_level"],
            result["congestion_score"],
            result["confidence"],
        )

        return {
            **result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except RuntimeError as exc:
        logger.error("Model runtime error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error("Inference error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction pipeline failure: {exc}",
        )


def _predict_operations(payload: PredictionInput) -> dict[str, Any]:
    try:
        return stadium_ops_engine.predict(payload.model_dump())
    except Exception as exc:
        logger.error("Operations ML inference error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Operations ML inference failure: {exc}",
        )


@router.post(
    "/operations",
    response_model=OperationsPredictionOutput,
    status_code=status.HTTP_200_OK,
    summary="Predict Full Stadium Operations State",
    description=(
        "Runs all AI operations models: congestion, queue times, attendance, "
        "risk, emergency severity, staffing, medical demand, vendors, parking, "
        "traffic, weather impact, and recommendations."
    ),
)
async def predict_operations(payload: PredictionInput):
    return _predict_operations(payload)


@router.post("/crowd/zones", status_code=status.HTTP_200_OK)
async def predict_zone_congestion(payload: PredictionInput):
    return _predict_operations(payload)["crowd_congestion"]


@router.post("/queues/gates", status_code=status.HTTP_200_OK)
async def predict_gate_queues(payload: PredictionInput):
    return _predict_operations(payload)["queue_times"]


@router.post("/attendance/forecast", status_code=status.HTTP_200_OK)
async def predict_attendance_forecast(payload: PredictionInput):
    return _predict_operations(payload)["attendance_forecast"]


@router.post("/risk/zones", status_code=status.HTTP_200_OK)
async def predict_zone_risk(payload: PredictionInput):
    return _predict_operations(payload)["crowd_risk"]


@router.post("/emergency/severity", status_code=status.HTTP_200_OK)
async def predict_emergency_severity(payload: PredictionInput):
    return _predict_operations(payload)["emergency_severity"]


@router.post("/security/resources", status_code=status.HTTP_200_OK)
async def predict_security_resources(payload: PredictionInput):
    return _predict_operations(payload)["security_recommendation"]


@router.post("/medical/demand", status_code=status.HTTP_200_OK)
async def predict_medical_demand(payload: PredictionInput):
    return _predict_operations(payload)["medical_demand"]


@router.post("/vendors/demand", status_code=status.HTTP_200_OK)
async def predict_vendor_demand(payload: PredictionInput):
    return _predict_operations(payload)["vendor_demand"]


@router.post("/parking/occupancy", status_code=status.HTTP_200_OK)
async def predict_parking_occupancy(payload: PredictionInput):
    return _predict_operations(payload)["parking_occupancy"]


@router.post("/traffic/flow", status_code=status.HTTP_200_OK)
async def predict_traffic_flow(payload: PredictionInput):
    return _predict_operations(payload)["traffic_flow"]


@router.post("/weather/impact", status_code=status.HTTP_200_OK)
async def predict_weather_impact(payload: PredictionInput):
    return _predict_operations(payload)["weather_impact"]


@router.post("/recommendations", status_code=status.HTTP_200_OK)
async def predict_recommendations(payload: PredictionInput):
    return _predict_operations(payload)["recommendations"]
