"""Inference engine that combines all StadiumOS operations ML modules."""

from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from .config import FEATURE_COLUMNS, FRIENDLY_FEATURE_NAMES
from .feature_engineering import (
    attendance_feature_rows,
    clamp,
    emergency_feature_row,
    ensure_feature_frame,
    gate_feature_rows,
    parking_feature_rows,
    traffic_feature_rows,
    vendor_feature_rows,
    zone_feature_rows,
)
from .training import StadiumOpsModelBundle, train_stadium_ops_models


def _as_percent(value: float) -> float:
    return round(clamp(value, 0.0, 100.0), 1)


def _risk_to_legacy(risk_level: str) -> str:
    return {
        "Safe": "LOW",
        "Moderate": "MEDIUM",
        "High": "HIGH",
        "Critical": "CRITICAL",
    }.get(risk_level, "MEDIUM")


def _traffic_label(score: float) -> str:
    if score >= 82:
        return "Severe"
    if score >= 62:
        return "Heavy"
    if score >= 38:
        return "Moderate"
    return "Free Flow"


def _regression_confidence(model: Any, X: pd.DataFrame, scale: float = 100.0) -> list[float]:
    if isinstance(model, RandomForestRegressor):
        feature_values = X.to_numpy()
        tree_predictions = np.vstack(
            [tree.predict(feature_values) for tree in model.estimators_]
        )
        std = tree_predictions.std(axis=0)
        return [_as_percent(96.0 - (float(item) / scale) * 100.0) for item in std]
    return [_as_percent(88.0 - row_penalty(row)) for _, row in X.iterrows()]


def row_penalty(row: pd.Series) -> float:
    weather_penalty = float(row.get("rain_probability", 0)) * 0.045
    incident_penalty = float(row.get("incident_count", 0)) * 1.4
    closed_gate_penalty = float(row.get("closed_gate_count", 0)) * 2.2
    return min(18.0, weather_penalty + incident_penalty + closed_gate_penalty)


def _classification_confidence(model: Any, X: pd.DataFrame) -> tuple[list[str], list[float]]:
    labels = list(model.predict(X))
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)
        confidence = [_as_percent(float(row.max()) * 100.0) for row in probabilities]
        return labels, confidence
    return labels, [82.0 for _ in labels]


def _feature_importances(model: Any) -> np.ndarray:
    if hasattr(model, "feature_importances_"):
        return np.asarray(model.feature_importances_, dtype=float)
    if hasattr(model, "estimators_"):
        estimators = getattr(model, "estimators_", [])
        importances = [
            getattr(estimator, "feature_importances_", None)
            for estimator in estimators
        ]
        importances = [item for item in importances if item is not None]
        if importances:
            return np.mean(np.asarray(importances, dtype=float), axis=0)
    return np.ones(len(FEATURE_COLUMNS), dtype=float)


def _top_factors(model: Any, limit: int = 3) -> list[dict[str, float | str]]:
    importances = _feature_importances(model)
    total = float(importances.sum()) or 1.0
    ranked = sorted(
        zip(FEATURE_COLUMNS, importances / total),
        key=lambda item: item[1],
        reverse=True,
    )[:limit]
    return [
        {
            "feature": FRIENDLY_FEATURE_NAMES.get(feature, feature),
            "impact": round(float(importance) * 100.0, 1),
        }
        for feature, importance in ranked
    ]


def _explanation(subject: str, value_text: str, factors: list[dict[str, Any]]) -> str:
    if not factors:
        return f"{subject} prediction is based on the current live simulation state."
    lead = factors[0]["feature"]
    supporting = ", ".join(str(factor["feature"]) for factor in factors[1:])
    if supporting:
        return f"{subject} is {value_text}; primary driver is {lead}, supported by {supporting}."
    return f"{subject} is {value_text}; primary driver is {lead}."


class StadiumOperationsInferenceEngine:
    """Lazy sklearn model registry for live stadium operations predictions."""

    def __init__(self) -> None:
        self._bundle: StadiumOpsModelBundle | None = None
        self._lock = threading.Lock()

    @property
    def bundle(self) -> StadiumOpsModelBundle:
        if self._bundle is None:
            with self._lock:
                if self._bundle is None:
                    self._bundle = train_stadium_ops_models()
        return self._bundle

    def predict(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        bundle = self.bundle
        generated_at = datetime.now(timezone.utc)
        forecast_hours = int(clamp(float(payload.get("forecast_hours", 6)), 1, 12))

        crowd_congestion = self._predict_crowd_congestion(bundle, payload)
        queue_times = self._predict_queue_times(bundle, payload)
        attendance_forecast = self._predict_attendance(bundle, payload, forecast_hours)
        crowd_risk = self._predict_crowd_risk(bundle, payload)
        emergency_severity = self._predict_emergency(bundle, payload)
        security_recommendation = self._predict_security(bundle, payload, crowd_congestion)
        medical_demand = self._predict_medical(bundle, payload)
        vendor_demand = self._predict_vendor(bundle, payload)
        parking_occupancy = self._predict_parking(bundle, payload)
        traffic_flow = self._predict_traffic(bundle, payload)
        weather_impact = self._predict_weather(bundle, payload)
        recommendations = self._recommend(
            payload,
            crowd_congestion,
            queue_times,
            emergency_severity,
            security_recommendation,
            medical_demand,
            parking_occupancy,
            traffic_flow,
            weather_impact,
        )

        legacy_crowd = self._legacy_crowd_response(
            payload,
            crowd_congestion,
            queue_times,
            crowd_risk,
            generated_at,
        )

        return {
            "status": "ready",
            "source": "sklearn-synthetic-ops-registry",
            "generated_at": generated_at.isoformat(),
            "model_version": "stadium-ops-synthetic-v1",
            "training_rows": bundle.training_rows,
            "evaluations": {
                key: {"metric": value.metric, "value": round(value.value, 4)}
                for key, value in bundle.evaluations.items()
            },
            "legacy_crowd": legacy_crowd,
            "crowd_congestion": crowd_congestion,
            "queue_times": queue_times,
            "attendance_forecast": attendance_forecast,
            "crowd_risk": crowd_risk,
            "emergency_severity": emergency_severity,
            "security_recommendation": security_recommendation,
            "medical_demand": medical_demand,
            "vendor_demand": vendor_demand,
            "parking_occupancy": parking_occupancy,
            "traffic_flow": traffic_flow,
            "weather_impact": weather_impact,
            "recommendations": recommendations,
        }

    def _predict_crowd_congestion(
        self,
        bundle: StadiumOpsModelBundle,
        payload: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        rows = zone_feature_rows(payload)
        X = ensure_feature_frame([row["features"] for row in rows])
        predictions = bundle.congestion_model.predict(X)
        confidences = _regression_confidence(bundle.congestion_model, X)
        factors = _top_factors(bundle.congestion_model)

        output = []
        for row, prediction, confidence in zip(rows, predictions, confidences):
            score = _as_percent(float(prediction))
            meta = row["meta"]
            predicted_occupancy = int(round(float(meta["capacity"]) * score / 100.0))
            output.append(
                {
                    "zone_id": meta["zone_id"],
                    "zone_name": meta["zone_name"],
                    "predicted_occupancy": predicted_occupancy,
                    "congestion_score": score,
                    "confidence": confidence,
                    "top_factors": factors,
                    "explanation": _explanation(
                        str(meta["zone_name"]),
                        f"projected at {score}% congestion",
                        factors,
                    ),
                }
            )
        return output

    def _predict_queue_times(
        self,
        bundle: StadiumOpsModelBundle,
        payload: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        rows = gate_feature_rows(payload)
        X = ensure_feature_frame([row["features"] for row in rows])
        predictions = bundle.queue_model.predict(X)
        confidences = _regression_confidence(bundle.queue_model, X, scale=60.0)
        factors = _top_factors(bundle.queue_model)

        return [
            {
                "gate_id": row["meta"]["gate_id"],
                "gate_name": row["meta"]["gate_name"],
                "zone_id": row["meta"]["zone_id"],
                "estimated_wait_minutes": round(float(prediction), 1),
                "confidence": confidence,
                "top_factors": factors,
                "explanation": _explanation(
                    str(row["meta"]["gate_name"]),
                    f"forecast at {round(float(prediction), 1)} minutes",
                    factors,
                ),
            }
            for row, prediction, confidence in zip(rows, predictions, confidences)
        ]

    def _predict_attendance(
        self,
        bundle: StadiumOpsModelBundle,
        payload: Mapping[str, Any],
        forecast_hours: int,
    ) -> list[dict[str, Any]]:
        rows = attendance_feature_rows(payload, forecast_hours)
        X = ensure_feature_frame([row["features"] for row in rows])
        predictions = bundle.attendance_model.predict(X)
        confidences = _regression_confidence(bundle.attendance_model, X, scale=80_000.0)
        factors = _top_factors(bundle.attendance_model)
        now = datetime.now(timezone.utc)

        return [
            {
                "hour_offset": int(row["meta"]["hour_offset"]),
                "forecast_time": (now + timedelta(hours=int(row["meta"]["hour_offset"]))).isoformat(),
                "predicted_attendance": int(round(float(prediction))),
                "confidence": confidence,
                "top_factors": factors,
                "explanation": _explanation(
                    f"Attendance T+{int(row['meta']['hour_offset'])}h",
                    f"projected at {int(round(float(prediction))):,} spectators",
                    factors,
                ),
            }
            for row, prediction, confidence in zip(rows, predictions, confidences)
        ]

    def _predict_crowd_risk(
        self,
        bundle: StadiumOpsModelBundle,
        payload: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        rows = zone_feature_rows(payload)
        X = ensure_feature_frame([row["features"] for row in rows])
        labels, confidences = _classification_confidence(bundle.risk_model, X)
        factors = _top_factors(bundle.risk_model)

        return [
            {
                "zone_id": row["meta"]["zone_id"],
                "zone_name": row["meta"]["zone_name"],
                "risk_level": label,
                "confidence": confidence,
                "top_factors": factors,
                "explanation": _explanation(
                    str(row["meta"]["zone_name"]),
                    f"classified as {label}",
                    factors,
                ),
            }
            for row, label, confidence in zip(rows, labels, confidences)
        ]

    def _predict_emergency(
        self,
        bundle: StadiumOpsModelBundle,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        row = emergency_feature_row(payload)
        X = ensure_feature_frame([row["features"]])
        labels, confidences = _classification_confidence(bundle.emergency_model, X)
        factors = _top_factors(bundle.emergency_model)
        label = labels[0]

        return {
            "incident_type": row["meta"]["incident_type"],
            "predicted_severity": label,
            "confidence": confidences[0],
            "top_factors": factors,
            "explanation": _explanation(
                f"{row['meta']['incident_type']} severity",
                f"classified as {label}",
                factors,
            ),
        }

    def _predict_security(
        self,
        bundle: StadiumOpsModelBundle,
        payload: Mapping[str, Any],
        crowd_congestion: list[dict[str, Any]],
    ) -> dict[str, Any]:
        rows = zone_feature_rows(payload)
        X = ensure_feature_frame([row["features"] for row in rows])
        predictions = bundle.security_model.predict(X)
        confidences = _regression_confidence(bundle.security_model, X, scale=500.0)
        factors = _top_factors(bundle.security_model)

        deployments = []
        for row, prediction, confidence in zip(rows, predictions, confidences):
            deployments.append(
                {
                    "zone_id": row["meta"]["zone_id"],
                    "zone_name": row["meta"]["zone_name"],
                    "recommended_personnel": int(round(float(prediction) / len(rows))),
                    "confidence": confidence,
                    "top_factors": factors,
                    "explanation": _explanation(
                        str(row["meta"]["zone_name"]),
                        "staffing recommendation generated",
                        factors,
                    ),
                }
            )

        current_staff = int(payload.get("security_staff", 300))
        recommended_total = int(round(sum(float(prediction) for prediction in predictions) / 2.4))
        high_pressure_zones = [
            item["zone_name"]
            for item in crowd_congestion
            if float(item["congestion_score"]) >= 70
        ]

        return {
            "current_personnel": current_staff,
            "recommended_total_personnel": recommended_total,
            "delta": recommended_total - current_staff,
            "high_pressure_zones": high_pressure_zones,
            "deployments": deployments,
            "confidence": _as_percent(float(np.mean(confidences))),
            "top_factors": factors,
            "explanation": _explanation(
                "Security deployment",
                f"recommends {recommended_total} total personnel",
                factors,
            ),
        }

    def _predict_medical(
        self,
        bundle: StadiumOpsModelBundle,
        payload: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        rows = zone_feature_rows(payload)
        X = ensure_feature_frame([row["features"] for row in rows])
        predictions = bundle.medical_model.predict(X)
        confidences = _regression_confidence(bundle.medical_model, X, scale=30.0)
        factors = _top_factors(bundle.medical_model)

        return [
            {
                "zone_id": row["meta"]["zone_id"],
                "zone_name": row["meta"]["zone_name"],
                "expected_cases": round(float(prediction), 1),
                "confidence": confidence,
                "top_factors": factors,
                "explanation": _explanation(
                    str(row["meta"]["zone_name"]),
                    f"expects {round(float(prediction), 1)} medical cases",
                    factors,
                ),
            }
            for row, prediction, confidence in zip(rows, predictions, confidences)
        ]

    def _predict_vendor(
        self,
        bundle: StadiumOpsModelBundle,
        payload: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        rows = vendor_feature_rows(payload)
        X = ensure_feature_frame([row["features"] for row in rows])
        predictions = bundle.vendor_model.predict(X)
        factors = _top_factors(bundle.vendor_model)

        output = []
        for row, prediction in zip(rows, predictions):
            food, beverage, merch = [int(round(float(value))) for value in prediction]
            total = food + beverage + merch
            output.append(
                {
                    "vendor_zone_id": row["meta"]["vendor_zone_id"],
                    "vendor_zone_name": row["meta"]["name"],
                    "food_units": food,
                    "beverage_units": beverage,
                    "merchandise_units": merch,
                    "total_units": total,
                    "confidence": _as_percent(87.0 - row_penalty(pd.Series(row["features"]))),
                    "top_factors": factors,
                    "explanation": _explanation(
                        str(row["meta"]["name"]),
                        f"forecast demand is {total:,} units",
                        factors,
                    ),
                }
            )
        return output

    def _predict_parking(
        self,
        bundle: StadiumOpsModelBundle,
        payload: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        rows = parking_feature_rows(payload)
        X = ensure_feature_frame([row["features"] for row in rows])
        predictions = bundle.parking_model.predict(X)
        confidences = _regression_confidence(bundle.parking_model, X)
        factors = _top_factors(bundle.parking_model)

        return [
            {
                "parking_id": row["meta"]["parking_id"],
                "parking_name": row["meta"]["name"],
                "capacity": row["meta"]["capacity"],
                "predicted_occupancy_pct": _as_percent(float(prediction)),
                "available_spaces": max(
                    0,
                    int(round(float(row["meta"]["capacity"]) * (1 - float(prediction) / 100.0))),
                ),
                "confidence": confidence,
                "top_factors": factors,
                "explanation": _explanation(
                    str(row["meta"]["name"]),
                    f"projected at {_as_percent(float(prediction))}% occupied",
                    factors,
                ),
            }
            for row, prediction, confidence in zip(rows, predictions, confidences)
        ]

    def _predict_traffic(
        self,
        bundle: StadiumOpsModelBundle,
        payload: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        rows = traffic_feature_rows(payload)
        X = ensure_feature_frame([row["features"] for row in rows])
        predictions = bundle.traffic_model.predict(X)
        factors = _top_factors(bundle.traffic_model)

        output = []
        for row, prediction in zip(rows, predictions):
            incoming = _as_percent(float(prediction[0]))
            outgoing = _as_percent(float(prediction[1]))
            output.append(
                {
                    "corridor_id": row["meta"]["corridor_id"],
                    "corridor_name": row["meta"]["name"],
                    "incoming_congestion": incoming,
                    "outgoing_congestion": outgoing,
                    "incoming_level": _traffic_label(incoming),
                    "outgoing_level": _traffic_label(outgoing),
                    "confidence": _as_percent(86.0 - row_penalty(pd.Series(row["features"]))),
                    "top_factors": factors,
                    "explanation": _explanation(
                        str(row["meta"]["name"]),
                        f"inbound {incoming}% and outbound {outgoing}%",
                        factors,
                    ),
                }
            )
        return output

    def _predict_weather(
        self,
        bundle: StadiumOpsModelBundle,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        rows = [zone_feature_rows(payload)[0]["features"]]
        X = ensure_feature_frame(rows)
        prediction = bundle.weather_model.predict(X)[0]
        factors = _top_factors(bundle.weather_model)
        attendance, congestion, queue, risk = [_as_percent(float(value)) for value in prediction]

        return {
            "attendance_impact_pct": attendance,
            "congestion_impact_pct": congestion,
            "queue_impact_pct": queue,
            "operational_risk_impact_pct": risk,
            "confidence": _as_percent(88.0 - row_penalty(X.iloc[0])),
            "top_factors": factors,
            "explanation": _explanation(
                "Weather impact",
                f"adds {risk}% operational risk pressure",
                factors,
            ),
        }

    def _recommend(
        self,
        payload: Mapping[str, Any],
        crowd_congestion: list[dict[str, Any]],
        queue_times: list[dict[str, Any]],
        emergency_severity: dict[str, Any],
        security_recommendation: dict[str, Any],
        medical_demand: list[dict[str, Any]],
        parking_occupancy: list[dict[str, Any]],
        traffic_flow: list[dict[str, Any]],
        weather_impact: dict[str, Any],
    ) -> list[dict[str, Any]]:
        recommendations = []
        most_congested = max(crowd_congestion, key=lambda item: item["congestion_score"])
        slowest_gate = max(queue_times, key=lambda item: item["estimated_wait_minutes"])
        busiest_medical = max(medical_demand, key=lambda item: item["expected_cases"])
        fullest_parking = max(parking_occupancy, key=lambda item: item["predicted_occupancy_pct"])
        worst_traffic = max(
            traffic_flow,
            key=lambda item: max(item["incoming_congestion"], item["outgoing_congestion"]),
        )

        if most_congested["congestion_score"] >= 70:
            recommendations.append(
                {
                    "title": f"Relieve {most_congested['zone_name']}",
                    "priority": "CRITICAL" if most_congested["congestion_score"] >= 85 else "HIGH",
                    "action": "Open overflow routing and redirect arrivals to lower-pressure gates.",
                    "expected_impact": "-10 to -18 congestion points",
                    "confidence": most_congested["confidence"],
                    "explanation": most_congested["explanation"],
                    "top_factors": most_congested["top_factors"],
                }
            )

        if slowest_gate["estimated_wait_minutes"] >= 14:
            recommendations.append(
                {
                    "title": f"Reduce wait at {slowest_gate['gate_name']}",
                    "priority": "HIGH",
                    "action": "Add manual scan lanes and publish wayfinding prompts to nearby spectators.",
                    "expected_impact": "-4 to -9 wait minutes",
                    "confidence": slowest_gate["confidence"],
                    "explanation": slowest_gate["explanation"],
                    "top_factors": slowest_gate["top_factors"],
                }
            )

        if security_recommendation["delta"] > 0:
            recommendations.append(
                {
                    "title": "Rebalance security deployment",
                    "priority": "MEDIUM",
                    "action": f"Move {security_recommendation['delta']} additional staff into pressure zones.",
                    "expected_impact": "+staffing coverage",
                    "confidence": security_recommendation["confidence"],
                    "explanation": security_recommendation["explanation"],
                    "top_factors": security_recommendation["top_factors"],
                }
            )

        if emergency_severity["predicted_severity"] in {"High", "Critical"}:
            recommendations.append(
                {
                    "title": "Pre-stage emergency response",
                    "priority": emergency_severity["predicted_severity"].upper(),
                    "action": "Dispatch response leads and reserve a clear access corridor.",
                    "expected_impact": "-response latency",
                    "confidence": emergency_severity["confidence"],
                    "explanation": emergency_severity["explanation"],
                    "top_factors": emergency_severity["top_factors"],
                }
            )

        if busiest_medical["expected_cases"] >= 5:
            recommendations.append(
                {
                    "title": f"Stage medics near {busiest_medical['zone_name']}",
                    "priority": "MEDIUM",
                    "action": "Move roving medical team and hydration support into the zone.",
                    "expected_impact": "-medical response time",
                    "confidence": busiest_medical["confidence"],
                    "explanation": busiest_medical["explanation"],
                    "top_factors": busiest_medical["top_factors"],
                }
            )

        if fullest_parking["predicted_occupancy_pct"] >= 88:
            recommendations.append(
                {
                    "title": f"Divert parking from {fullest_parking['parking_name']}",
                    "priority": "MEDIUM",
                    "action": "Push app guidance toward alternate lots and metro park-and-ride.",
                    "expected_impact": "+available capacity",
                    "confidence": fullest_parking["confidence"],
                    "explanation": fullest_parking["explanation"],
                    "top_factors": fullest_parking["top_factors"],
                }
            )

        if max(worst_traffic["incoming_congestion"], worst_traffic["outgoing_congestion"]) >= 72:
            recommendations.append(
                {
                    "title": f"Coordinate traffic control on {worst_traffic['corridor_name']}",
                    "priority": "HIGH",
                    "action": "Activate signal priority and stagger outbound release windows.",
                    "expected_impact": "-road congestion",
                    "confidence": worst_traffic["confidence"],
                    "explanation": worst_traffic["explanation"],
                    "top_factors": worst_traffic["top_factors"],
                }
            )

        if weather_impact["operational_risk_impact_pct"] >= 15:
            recommendations.append(
                {
                    "title": "Activate weather mitigation plan",
                    "priority": "HIGH",
                    "action": "Open covered concourses, adjust queue barriers, and increase hydration notices.",
                    "expected_impact": "-weather risk exposure",
                    "confidence": weather_impact["confidence"],
                    "explanation": weather_impact["explanation"],
                    "top_factors": weather_impact["top_factors"],
                }
            )

        if not recommendations:
            recommendations.append(
                {
                    "title": "Maintain current operations posture",
                    "priority": "LOW",
                    "action": "Continue monitoring live telemetry and keep reserve teams on standby.",
                    "expected_impact": "stable operations",
                    "confidence": 88.0,
                    "explanation": "No model is currently projecting a severe operating constraint.",
                    "top_factors": [],
                }
            )

        return recommendations[:8]

    def _legacy_crowd_response(
        self,
        payload: Mapping[str, Any],
        crowd_congestion: list[dict[str, Any]],
        queue_times: list[dict[str, Any]],
        crowd_risk: list[dict[str, Any]],
        generated_at: datetime,
    ) -> dict[str, Any]:
        average_congestion = float(
            np.mean([item["congestion_score"] for item in crowd_congestion])
        )
        average_wait = float(np.mean([item["estimated_wait_minutes"] for item in queue_times]))
        highest_risk = max(
            crowd_risk,
            key=lambda item: ["Safe", "Moderate", "High", "Critical"].index(item["risk_level"]),
        )
        confidence = float(
            np.mean(
                [item["confidence"] for item in crowd_congestion]
                + [item["confidence"] for item in queue_times]
            )
        )
        predicted_occupancy = int(
            round(
                min(
                    float(payload.get("stadium_capacity", 80_000)),
                    float(payload.get("attendance", 0)) * (1 + average_congestion / 600.0),
                )
            )
        )

        return {
            "predicted_occupancy": predicted_occupancy,
            "confidence": round(confidence / 100.0, 2),
            "risk_level": _risk_to_legacy(str(highest_risk["risk_level"])),
            "congestion_score": round(average_congestion, 1),
            "queue_prediction": int(round(average_wait)),
            "top_factors": crowd_congestion[0]["top_factors"],
            "timestamp": generated_at.isoformat(),
        }
