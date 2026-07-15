import threading

import pytest

from app.services.prediction_service import PredictionService, _EXPECTED_COLS


class FakePreprocessor:
    def __init__(self):
        self.seen_columns = None

    def transform(self, frame):
        self.seen_columns = tuple(frame.columns)
        return frame


class FixedPredictionModel:
    feature_importances_ = [
        0.0, 1.0, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0
    ]

    def predict(self, _features):
        return [72_000]


def build_service(model=None, preprocessor=None):
    service = object.__new__(PredictionService)
    service._inference_lock = threading.Lock()
    service._model = model or FixedPredictionModel()
    service._preprocessor = preprocessor or FakePreprocessor()
    service._model_loaded = True
    return service


@pytest.mark.parametrize(
    ("match_minute", "expected_phase"),
    [
        (-1, "pre-match"),
        (45, "first-half"),
        (46, "halftime"),
        (61, "second-half"),
        (106, "post-match"),
    ],
)
def test_maps_match_minute_to_event_phase(match_minute, expected_phase):
    features = PredictionService._map_dashboard_input_to_ml_features(
        {"match_minute": match_minute}
    )

    assert features["event_phase"] == expected_phase


@pytest.mark.parametrize(
    ("raw", "expected_features"),
    [
        ({"rain_probability": 51}, {"weather": "rain"}),
        ({"temperature": 36, "rain_probability": 10}, {"weather": "hot"}),
        ({"temperature": 24, "rain_probability": 21}, {"weather": "cloudy"}),
        ({"gate_open_count": 0}, {"gate_status": "closed"}),
        ({"gate_open_count": 4}, {"gate_status": "restricted"}),
        ({"security_queue_length": 301}, {"security_level": "high"}),
    ],
)
def test_maps_dashboard_heuristics_to_model_features(raw, expected_features):
    features = PredictionService._map_dashboard_input_to_ml_features(raw)

    for feature_name, expected_value in expected_features.items():
        assert features[feature_name] == expected_value


def test_predict_preserves_model_column_order_and_derives_dashboard_metrics():
    preprocessor = FakePreprocessor()
    service = build_service(preprocessor=preprocessor)

    result = service.predict(
        {
            "attendance": 64_200,
            "stadium_capacity": 80_000,
            "match_minute": 58,
            "entry_rate_per_min": 420,
            "exit_rate_per_min": 115,
            "temperature": 31,
            "rain_probability": 10,
            "gate_open_count": 8,
            "security_queue_length": 150,
            "weekday": "Friday",
        }
    )

    assert preprocessor.seen_columns == _EXPECTED_COLS
    assert result["predicted_occupancy"] == 72_000
    assert result["congestion_score"] == 90.0
    assert result["risk_level"] == "CRITICAL"
    assert result["queue_prediction"] == 22
    assert result["confidence"] == 0.64
    assert result["top_factors"] == [
        {"feature": "security level", "impact": 50.0},
        {"feature": "weather", "impact": 33.3},
        {"feature": "event phase", "impact": 16.7},
    ]


def test_predict_clamps_negative_model_output():
    class NegativePredictionModel:
        def predict(self, _features):
            return [-100]

    service = build_service(model=NegativePredictionModel())

    result = service.predict({"stadium_capacity": 80_000})

    assert result["predicted_occupancy"] == 0
    assert result["congestion_score"] == 0.0
    assert result["risk_level"] == "LOW"
    assert result["queue_prediction"] == 1
    assert result["top_factors"] == []
