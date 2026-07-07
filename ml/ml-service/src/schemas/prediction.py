from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

# Base outputs DTO for all inference results
class PredictionBaseResponse(BaseModel):
    prediction_value: float
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime
    model_version: str
    feature_summary: Dict[str, Any]
    explanation: str
    recommended_action: str

# 1. Crowd predictions schemas
class CrowdPredictionRequest(BaseModel):
    stadium_id: str
    zone_id: str
    current_headcount: int = Field(..., ge=0)
    minutes_ahead: int = Field(15, ge=5, le=60)

class CrowdPredictionResponse(BaseModel):
    predicted_headcount: float
    predicted_occupancy_pct: float
    confidence_score: float
    model_version: str
    explanation: str
    recommended_action: str
    timestamp: str

# 2. Queue wait predictions schemas
class QueuePredictionRequest(BaseModel):
    gate_id: str
    queue_length: int = Field(..., ge=0)
    arrival_rate_per_min: float = Field(..., ge=0.0)

class QueuePredictionResponse(BaseModel):
    predicted_wait_seconds: float
    confidence_score: float
    model_version: str
    explanation: str
    recommended_action: str
    timestamp: str

# 3. Vendor demand predictions schemas
class VendorPredictionRequest(BaseModel):
    vendor_id: str
    kiosk_type: str # e.g. "Food", "Beverage", "Merchandise"
    minutes_ahead: int = Field(30, ge=10, le=120)

class VendorPredictionResponse(BaseModel):
    predicted_sales_velocity: float # items per min
    confidence_score: float
    model_version: str
    explanation: str
    recommended_action: str
    timestamp: str

# 4. Parking occupancy predictions schemas
class ParkingPredictionRequest(BaseModel):
    parking_lot_id: str
    current_occupancy_pct: float = Field(..., ge=0.0, le=100.0)

class ParkingPredictionResponse(BaseModel):
    predicted_occupancy_pct: float
    confidence_score: float
    model_version: str
    explanation: str
    recommended_action: str
    timestamp: str

# 5. Transport delay predictions schemas
class TransportPredictionRequest(BaseModel):
    bus_loop_id: str
    active_buses: int = Field(..., ge=1)
    traffic_index: float = Field(..., ge=0.0, le=10.0)

class TransportPredictionResponse(BaseModel):
    predicted_delay_seconds: float
    confidence_score: float
    model_version: str
    explanation: str
    recommended_action: str
    timestamp: str

# 6. Emergency risk predictions schemas
class EmergencyPredictionRequest(BaseModel):
    zone_id: str
    headcount: int = Field(..., ge=0)
    temperature_f: float
    precipitation_rate: float = Field(..., ge=0.0)

class EmergencyPredictionResponse(BaseModel):
    predicted_risk_level: str # "Low", "Medium", "High", "Critical"
    predicted_probability: float
    confidence_score: float
    model_version: str
    explanation: str
    recommended_action: str
    timestamp: str
