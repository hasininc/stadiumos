"""
PredictionService — Thread-safe singleton that wraps the trained
CatBoost crowd-density forecasting model.

Loads model artifacts once at startup and exposes a .predict() method
that maps the dashboard's PredictionInput schema to the ML feature
space, runs inference, and returns both new ML fields and legacy
dashboard fields.
"""

import logging
import threading
from pathlib import Path
from typing import Any, Iterable, Mapping

import joblib
import pandas as pd

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Paths to trained model artifacts
# ──────────────────────────────────────────────
_ML_DIR = Path(__file__).resolve().parents[4] / "ml"
_MODEL_PATH = _ML_DIR / "models" / "crowd_forecast_model.pkl"
_PREPROCESSOR_PATH = _ML_DIR / "models" / "preprocessor.pkl"
_DEFAULT_STADIUM_CAPACITY = 80_000
_MIN_CONFIDENCE = 0.60
_MAX_CONFIDENCE = 0.95
_VOLATILITY_CONFIDENCE_DIVISOR = 1500.0
_MAX_QUEUE_WAIT_MINUTES = 60

# The feature columns expected by the preprocessor (must match training order)
_EXPECTED_COLS = (
    "zone_id", "event_phase", "weather", "day_of_week",
    "gate_status", "security_level", "current_occupancy",
    "entry_rate", "exit_rate", "hour",
)


def _event_phase_for_match_minute(match_minute: float) -> str:
    if match_minute < 0:
        return "pre-match"
    if match_minute <= 45:
        return "first-half"
    if match_minute <= 60:
        return "halftime"
    if match_minute <= 105:
        return "second-half"
    return "post-match"


def _weather_for_conditions(temperature: float, rain_probability: float) -> str:
    if rain_probability > 50:
        return "rain"
    if temperature > 35:
        return "hot"
    if rain_probability > 20:
        return "cloudy"
    return "clear"


def _gate_status_for_open_count(open_gate_count: int) -> str:
    if open_gate_count == 0:
        return "closed"
    if open_gate_count < 5:
        return "restricted"
    return "open"


def _security_level_for_queue_length(queue_length: float) -> str:
    if queue_length > 300:
        return "high"
    if queue_length > 100:
        return "medium"
    return "low"


def _congestion_score(predicted_occupancy: float, capacity: Any) -> float:
    stadium_capacity = float(capacity or _DEFAULT_STADIUM_CAPACITY)
    stadium_capacity = max(stadium_capacity, 1.0)
    score = (max(0.0, predicted_occupancy) / stadium_capacity) * 100.0
    return round(min(100.0, score), 1)


def _risk_level_for_congestion(congestion_score: float) -> str:
    if congestion_score < 35:
        return "LOW"
    if congestion_score < 65:
        return "MEDIUM"
    if congestion_score < 85:
        return "HIGH"
    return "CRITICAL"


def _confidence_for_volatility(entry_rate: float, exit_rate: float) -> float:
    volatility = entry_rate + exit_rate
    confidence = 1.0 - (volatility / _VOLATILITY_CONFIDENCE_DIVISOR)
    bounded_confidence = max(_MIN_CONFIDENCE, min(_MAX_CONFIDENCE, confidence))
    return round(bounded_confidence, 2)


def _queue_prediction_for_congestion(congestion_score: float) -> int:
    queue_minutes = congestion_score * 0.25
    return int(min(_MAX_QUEUE_WAIT_MINUTES, max(1, queue_minutes)))


def _top_factors_from_importances(
    importances: Iterable[float] | None,
) -> list[dict[str, float | str]]:
    if importances is None:
        return []

    importances_by_feature = [
        (feature_name, float(importance))
        for feature_name, importance in zip(_EXPECTED_COLS, importances)
    ]
    total_importance = (
        sum(importance for _, importance in importances_by_feature) or 1.0
    )

    ranked_importances = sorted(
        importances_by_feature,
        key=lambda item: item[1],
        reverse=True,
    )[:3]

    return [
        {
            "feature": feature_name.replace("_", " "),
            "impact": round((importance / total_importance) * 100.0, 1),
        }
        for feature_name, importance in ranked_importances
    ]


class PredictionService:
    """Thread-safe singleton that loads the trained model once and
    serves predictions for the lifetime of the process."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._inference_lock = threading.Lock()
        self._model = None
        self._preprocessor = None
        self._model_loaded = False

        self._load_artifacts()
        self._initialized = True

    # ── Artifact Loading ──────────────────────────

    def _load_artifacts(self) -> None:
        """Load the trained model and preprocessor from disk."""
        logger.info("Loading ML model artifacts from %s …", _ML_DIR)

        if not _MODEL_PATH.exists():
            logger.warning(
                "Model file not found at %s — predictions will be unavailable.",
                _MODEL_PATH,
            )
            return
        if not _PREPROCESSOR_PATH.exists():
            logger.warning(
                "Preprocessor file not found at %s — predictions will be unavailable.",
                _PREPROCESSOR_PATH,
            )
            return

        try:
            self._model = joblib.load(_MODEL_PATH)
            self._preprocessor = joblib.load(_PREPROCESSOR_PATH)
            self._model_loaded = True
            logger.info("ML model artifacts loaded successfully.")
        except Exception as exc:
            logger.error("Failed to load ML artifacts: %s", exc, exc_info=True)

    @property
    def is_ready(self) -> bool:
        """Check whether the model artifacts are loaded and ready."""
        return self._model_loaded

    # ── Feature Mapping ───────────────────────────

    @staticmethod
    def _map_dashboard_input_to_ml_features(raw: Mapping[str, Any]) -> dict[str, Any]:
        """
        Maps the dashboard's PredictionInput schema (22 fields like
        attendance, match_minute, etc.) into the 10 features expected
        by the trained ML model.

        This is a deterministic, heuristic mapping — no information is
        lost, but the representation changes to match the training data.
        """
        return {
            "zone_id": raw.get("zone_id", "ZONE_A"),
            "current_occupancy": int(raw.get("attendance", 0)),
            "entry_rate": int(raw.get("entry_rate_per_min", 0)),
            "exit_rate": int(raw.get("exit_rate_per_min", 0)),
            "event_phase": _event_phase_for_match_minute(
                raw.get("match_minute", 0)
            ),
            "weather": _weather_for_conditions(
                raw.get("temperature", 25),
                raw.get("rain_probability", 0),
            ),
            "day_of_week": raw.get("weekday", "Monday"),
            "gate_status": _gate_status_for_open_count(
                raw.get("gate_open_count", 10)
            ),
            "security_level": _security_level_for_queue_length(
                raw.get("security_queue_length", 0)
            ),
            "hour": 12,  # Not available from the dashboard input; safe default
        }

    # ── Inference ─────────────────────────────────

    def predict(self, raw_input: Mapping[str, Any]) -> dict[str, Any]:
        """
        Thread-safe inference.  Accepts a dict matching the dashboard's
        PredictionInput fields and returns a composite result containing
        both the new ML fields and legacy dashboard fields.

        Raises RuntimeError if the model was not loaded.
        """
        if not self._model_loaded:
            raise RuntimeError(
                "ML model is not loaded. Ensure model artifacts exist "
                f"at {_MODEL_PATH} and {_PREPROCESSOR_PATH}."
            )

        ml_features = self._map_dashboard_input_to_ml_features(raw_input)

        with self._inference_lock:
            df = pd.DataFrame([ml_features])

            # Ensure column order matches preprocessor expectations
            X_prep = self._preprocessor.transform(df[list(_EXPECTED_COLS)])

            predicted_occupancy = float(self._model.predict(X_prep)[0])
            predicted_occupancy = max(0.0, predicted_occupancy)

        # ── Derived metrics for dashboard backward compatibility ────
        congestion_score = _congestion_score(
            predicted_occupancy,
            raw_input.get("stadium_capacity", _DEFAULT_STADIUM_CAPACITY),
        )

        return {
            "predicted_occupancy": int(round(predicted_occupancy)),
            "congestion_score": congestion_score,
            "queue_prediction": _queue_prediction_for_congestion(congestion_score),
            "risk_level": _risk_level_for_congestion(congestion_score),
            "confidence": _confidence_for_volatility(
                ml_features["entry_rate"],
                ml_features["exit_rate"],
            ),
            "top_factors": _top_factors_from_importances(
                getattr(self._model, "feature_importances_", None),
            ),
        }


# Module-level singleton — imported by the endpoint router
prediction_service = PredictionService()
