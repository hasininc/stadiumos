"""Training registry for StadiumOS operations ML models."""

from __future__ import annotations

from dataclasses import dataclass

from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.multioutput import MultiOutputRegressor

from .config import FEATURE_COLUMNS
from .generator import generate_synthetic_stadium_dataset


@dataclass(frozen=True)
class ModelEvaluation:
    metric: str
    value: float


@dataclass(frozen=True)
class StadiumOpsModelBundle:
    congestion_model: RandomForestRegressor
    queue_model: GradientBoostingRegressor
    attendance_model: GradientBoostingRegressor
    risk_model: RandomForestClassifier
    emergency_model: GradientBoostingClassifier
    security_model: RandomForestRegressor
    medical_model: GradientBoostingRegressor
    vendor_model: MultiOutputRegressor
    parking_model: GradientBoostingRegressor
    traffic_model: MultiOutputRegressor
    weather_model: MultiOutputRegressor
    evaluations: dict[str, ModelEvaluation]
    training_rows: int


def train_stadium_ops_models(
    n_samples: int = 2400,
    random_state: int = 42,
) -> StadiumOpsModelBundle:
    """Train deterministic sklearn models on generated stadium data."""
    frame = generate_synthetic_stadium_dataset(
        n_samples=n_samples,
        random_state=random_state,
    )
    X = frame[FEATURE_COLUMNS]

    congestion_model = RandomForestRegressor(
        n_estimators=64,
        max_depth=12,
        min_samples_leaf=3,
        random_state=random_state,
        n_jobs=1,
    )
    queue_model = GradientBoostingRegressor(random_state=random_state)
    attendance_model = GradientBoostingRegressor(random_state=random_state + 1)
    risk_model = RandomForestClassifier(
        n_estimators=72,
        max_depth=12,
        min_samples_leaf=3,
        random_state=random_state,
        n_jobs=1,
    )
    emergency_model = GradientBoostingClassifier(random_state=random_state)
    security_model = RandomForestRegressor(
        n_estimators=56,
        max_depth=11,
        min_samples_leaf=3,
        random_state=random_state + 2,
        n_jobs=1,
    )
    medical_model = GradientBoostingRegressor(random_state=random_state + 3)
    vendor_model = MultiOutputRegressor(
        RandomForestRegressor(
            n_estimators=48,
            max_depth=12,
            min_samples_leaf=3,
            random_state=random_state + 4,
            n_jobs=1,
        )
    )
    parking_model = GradientBoostingRegressor(random_state=random_state + 5)
    traffic_model = MultiOutputRegressor(
        RandomForestRegressor(
            n_estimators=48,
            max_depth=12,
            min_samples_leaf=3,
            random_state=random_state + 6,
            n_jobs=1,
        )
    )
    weather_model = MultiOutputRegressor(
        RandomForestRegressor(
            n_estimators=48,
            max_depth=12,
            min_samples_leaf=3,
            random_state=random_state + 7,
            n_jobs=1,
        )
    )

    congestion_model.fit(X, frame["congestion_score"])
    queue_model.fit(X, frame["queue_wait_minutes"])
    attendance_model.fit(X, frame["attendance_forecast"])
    risk_model.fit(X, frame["risk_level"])
    emergency_model.fit(X, frame["emergency_severity"])
    security_model.fit(X, frame["security_required"])
    medical_model.fit(X, frame["medical_cases"])
    vendor_model.fit(
        X,
        frame[["vendor_food_units", "vendor_beverage_units", "vendor_merch_units"]],
    )
    parking_model.fit(X, frame["parking_utilization"])
    traffic_model.fit(
        X,
        frame[["traffic_in_congestion", "traffic_out_congestion"]],
    )
    weather_model.fit(
        X,
        frame[
            [
                "weather_attendance_impact",
                "weather_congestion_impact",
                "weather_queue_impact",
                "weather_risk_impact",
            ]
        ],
    )

    evaluations = {
        "congestion_mae": ModelEvaluation(
            "MAE",
            float(mean_absolute_error(frame["congestion_score"], congestion_model.predict(X))),
        ),
        "queue_mae": ModelEvaluation(
            "MAE",
            float(mean_absolute_error(frame["queue_wait_minutes"], queue_model.predict(X))),
        ),
        "risk_accuracy": ModelEvaluation(
            "accuracy",
            float(accuracy_score(frame["risk_level"], risk_model.predict(X))),
        ),
        "emergency_accuracy": ModelEvaluation(
            "accuracy",
            float(accuracy_score(frame["emergency_severity"], emergency_model.predict(X))),
        ),
    }

    return StadiumOpsModelBundle(
        congestion_model=congestion_model,
        queue_model=queue_model,
        attendance_model=attendance_model,
        risk_model=risk_model,
        emergency_model=emergency_model,
        security_model=security_model,
        medical_model=medical_model,
        vendor_model=vendor_model,
        parking_model=parking_model,
        traffic_model=traffic_model,
        weather_model=weather_model,
        evaluations=evaluations,
        training_rows=len(frame),
    )
