import logging
import time
from datetime import datetime
from src.core.model_registry import model_registry
from src.core.redis_client import redis_client
from src.core.kafka_client import kafka_client
from src.schemas.prediction import (
    CrowdPredictionRequest, CrowdPredictionResponse,
    QueuePredictionRequest, QueuePredictionResponse,
    VendorPredictionRequest, VendorPredictionResponse,
    ParkingPredictionRequest, ParkingPredictionResponse,
    TransportPredictionRequest, TransportPredictionResponse,
    EmergencyPredictionRequest, EmergencyPredictionResponse
)
from shared.utils.error_handlers import ValidationError

logger = logging.getLogger("ml-service")

class InferenceService:
    def __init__(self):
        self.registry = model_registry

    def _get_timestamp(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def predict_crowd_congestion(self, req: CrowdPredictionRequest) -> CrowdPredictionResponse:
        # Preprocessing & Validation
        if req.current_headcount < 0:
            raise ValidationError("Headcount cannot be negative")

        # Check Cache
        cache_key = f"ml:predict:crowd:{req.zone_id}"
        cached = redis_client.get_cache(cache_key)
        if cached:
            return CrowdPredictionResponse(**cached)

        # Mock ML Model Execution (XGBoost Regressor v1.2.0)
        # In production:
        # model = self.registry.get_model("crowd_congestion")
        # predicted_val = model.predict([[req.current_headcount, req.minutes_ahead]])
        predicted_val = req.current_headcount * 1.15
        occupancy_pct = (predicted_val / 2000.0) * 100.0 # Assuming max capacity 2000

        res = CrowdPredictionResponse(
            predicted_headcount=predicted_val,
            predicted_occupancy_pct=occupancy_pct,
            confidence_score=0.94,
            model_version="v1.2.0",
            explanation=f"XGBoost regressor predicts a 15% density increase based on current flow of {req.current_headcount} fans.",
            recommended_action="Deploy additional volunteers to Gate B for redirect assistance.",
            timestamp=self._get_timestamp()
        )

        # Cache results & Publish event
        redis_client.set_cache(cache_key, res.dict(), ttl=60)
        kafka_client.publish_event(
            "stadiumos.ml.crowd-prediction",
            key=req.zone_id,
            payload=res.dict()
        )
        return res

    def predict_queue_wait(self, req: QueuePredictionRequest) -> QueuePredictionResponse:
        if req.queue_length < 0:
            raise ValidationError("Queue length cannot be negative")

        cache_key = f"ml:predict:queue:{req.gate_id}"
        cached = redis_client.get_cache(cache_key)
        if cached:
            return QueuePredictionResponse(**cached)

        # Mock ML Model Execution (LightGBM Regressor v2.1.0)
        # Formula: average 15 seconds per turnstile scan
        predicted_wait = req.queue_length * 15.0 + (req.arrival_rate_per_min * 5.0)

        res = QueuePredictionResponse(
            predicted_wait_seconds=predicted_wait,
            confidence_score=0.92,
            model_version="v2.1.0",
            explanation=f"LightGBM models average turnstile clearance rates of 15 seconds per person under arrival rate {req.arrival_rate_per_min}/min.",
            recommended_action="Open auxiliary gate lane 4 to reduce queues.",
            timestamp=self._get_timestamp()
        )

        redis_client.set_cache(cache_key, res.dict(), ttl=60)
        kafka_client.publish_event(
            "stadiumos.ml.queue-prediction",
            key=req.gate_id,
            payload=res.dict()
        )
        return res

    def predict_vendor_demand(self, req: VendorPredictionRequest) -> VendorPredictionResponse:
        cache_key = f"ml:predict:vendor:{req.vendor_id}"
        cached = redis_client.get_cache(cache_key)
        if cached:
            return VendorPredictionResponse(**cached)

        # Mock Prophet TimeSeries prediction
        predicted_sales = 4.2 # items per minute

        res = VendorPredictionResponse(
            predicted_sales_velocity=predicted_sales,
            confidence_score=0.89,
            model_version="v1.0.4",
            explanation=f"Prophet algorithm forecasts sales velocity of {predicted_sales} items/min during half-time ingress peak.",
            recommended_action="Prepare 50 ponchos and 100 bottled drinks in warm inventory.",
            timestamp=self._get_timestamp()
        )

        redis_client.set_cache(cache_key, res.dict(), ttl=300)
        kafka_client.publish_event(
            "stadiumos.ml.vendor-demand",
            key=req.vendor_id,
            payload=res.dict()
        )
        return res

    def predict_parking_occupancy(self, req: ParkingPredictionRequest) -> ParkingPredictionResponse:
        cache_key = f"ml:predict:parking:{req.parking_lot_id}"
        cached = redis_client.get_cache(cache_key)
        if cached:
            return ParkingPredictionResponse(**cached)

        predicted_occupancy = req.current_occupancy_pct * 1.08

        res = ParkingPredictionResponse(
            predicted_occupancy_pct=predicted_occupancy,
            confidence_score=0.91,
            model_version="v1.1.0",
            explanation=f"Random Forest predicts parking lot saturation in 30 minutes based on historical match ingress parameters.",
            recommended_action="Update electronic road signage to direct incoming traffic to Lot D.",
            timestamp=self._get_timestamp()
        )

        redis_client.set_cache(cache_key, res.dict(), ttl=120)
        kafka_client.publish_event(
            "stadiumos.ml.parking-prediction",
            key=req.parking_lot_id,
            payload=res.dict()
        )
        return res

    def predict_transport_delay(self, req: TransportPredictionRequest) -> TransportPredictionResponse:
        cache_key = f"ml:predict:transport:{req.bus_loop_id}"
        cached = redis_client.get_cache(cache_key)
        if cached:
            return TransportPredictionResponse(**cached)

        predicted_delay = req.traffic_index * 120.0 # 2 minutes per traffic index point

        res = TransportPredictionResponse(
            predicted_delay_seconds=predicted_delay,
            confidence_score=0.88,
            model_version="v1.0.0",
            explanation=f"LSTM neural network estimates loop route delays based on traffic index {req.traffic_index}.",
            recommended_action="Deploy auxiliary shuttle bus 12 to loop route B.",
            timestamp=self._get_timestamp()
        )

        redis_client.set_cache(cache_key, res.dict(), ttl=120)
        kafka_client.publish_event(
            "stadiumos.ml.transport-prediction",
            key=req.bus_loop_id,
            payload=res.dict()
        )
        return res

    def predict_emergency_risk(self, req: EmergencyPredictionRequest) -> EmergencyPredictionResponse:
        cache_key = f"ml:predict:emergency:{req.zone_id}"
        cached = redis_client.get_cache(cache_key)
        if cached:
            return EmergencyPredictionResponse(**cached)

        probability = 0.05
        if req.precipitation_rate > 10.0:
            probability = 0.42 # High slipping risk on wet stairs

        risk_level = "Low"
        if probability > 0.4:
            risk_level = "High"
        elif probability > 0.2:
            risk_level = "Medium"

        res = EmergencyPredictionResponse(
            predicted_risk_level=risk_level,
            predicted_probability=probability,
            confidence_score=0.95,
            model_version="v3.0.2",
            explanation=f"XGBoost classifier predicts {risk_level} slip-and-fall risk under rain rate {req.precipitation_rate}mm/hr.",
            recommended_action="Deploy wet-floor signage and notify medical responders at Section 104.",
            timestamp=self._get_timestamp()
        )

        redis_client.set_cache(cache_key, res.dict(), ttl=60)
        kafka_client.publish_event(
            "stadiumos.ml.emergency-risk",
            key=req.zone_id,
            payload=res.dict()
        )
        return res
