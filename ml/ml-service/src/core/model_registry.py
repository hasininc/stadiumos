import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ml-service")

class ModelMetadata:
    def __init__(self, name: str, version: str, algorithm: str, accuracy: float, description: str):
        self.name = name
        self.version = version
        self.algorithm = algorithm
        self.accuracy = accuracy
        self.description = description

class ModelRegistry:
    def __init__(self):
        # Simulated registry index mapping
        self.models_meta: Dict[str, ModelMetadata] = {
            "crowd_congestion": ModelMetadata("Crowd Congestion Predictor", "v1.2.0", "XGBoost Regressor", 0.94, "Forecasts crowd bottleneck index per stadium zone"),
            "queue_wait": ModelMetadata("Queue Waiting Time Predictor", "v2.1.0", "LightGBM Regressor", 0.92, "Calculates turnstile queue durations"),
            "vendor_demand": ModelMetadata("Vendor Concessions Demand Predictor", "v1.0.4", "Prophet TimeSeries", 0.89, "Forecasts food and beverage sales velocity"),
            "parking_occupancy": ModelMetadata("Parking Lot Occupancy Predictor", "v1.1.0", "Random Forest Regressor", 0.91, "Predicts lot saturation percentages"),
            "transport_delay": ModelMetadata("Transit Bus Loop Delay Predictor", "v1.0.0", "LSTM Neural Network", 0.88, "Forecasts delay time in transit loops"),
            "emergency_risk": ModelMetadata("Section Emergency Incident Risk Predictor", "v3.0.2", "XGBoost Classifier", 0.95, "Predicts critical incident risks")
        }
        self.loaded_models: Dict[str, Any] = {}
        self._load_all_models()

    def _load_all_models(self) -> None:
        for model_key, meta in self.models_meta.items():
            try:
                # In production, this would execute:
                # self.loaded_models[model_key] = joblib.load(f"{settings.MODEL_REGISTRY_PATH}/{model_key}.joblib")
                logger.info(f"Successfully loaded model '{meta.name}' ({meta.version}) - Algorithm: {meta.algorithm}")
                self.loaded_models[model_key] = f"mocked_{model_key}_model"
            except Exception as e:
                logger.error(f"Failed to load model '{model_key}': {str(e)}")

    def get_model(self, key: str) -> Optional[Any]:
        return self.loaded_models.get(key)

    def get_model_metadata(self, key: str) -> Optional[ModelMetadata]:
        return self.models_meta.get(key)

    def list_models(self) -> list[dict]:
        return [
            {
                "key": k,
                "name": m.name,
                "version": m.version,
                "algorithm": m.algorithm,
                "accuracy": m.accuracy,
                "description": m.description
            }
            for k, m in self.models_meta.items()
        ]

# Singleton instance
model_registry = ModelRegistry()
