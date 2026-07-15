"""Feature engineering for live StadiumOS simulation telemetry."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

import pandas as pd

from .config import (
    FEATURE_COLUMNS,
    GATE_PROFILES,
    INCIDENT_TYPE_CODES,
    PARKING_AREAS,
    TRAFFIC_CORRIDORS,
    VENDOR_ZONES,
    ZONE_PROFILES,
)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def phase_code(match_minute: float) -> int:
    if match_minute < 0:
        return 0
    if match_minute <= 45:
        return 1
    if match_minute <= 60:
        return 2
    if match_minute <= 105:
        return 3
    return 4


def phase_intensity(match_minute: float) -> float:
    code = phase_code(match_minute)
    return [0.82, 0.78, 1.0, 0.86, 1.18][code]


def normalize_closed_gates(raw_closed_gates: Any) -> set[str]:
    if raw_closed_gates is None:
        return set()
    if isinstance(raw_closed_gates, str):
        return {raw_closed_gates.upper()}
    if isinstance(raw_closed_gates, Iterable):
        return {str(gate).upper() for gate in raw_closed_gates}
    return set()


def base_features_from_payload(payload: Mapping[str, Any]) -> dict[str, float]:
    attendance = float(payload.get("attendance", 0))
    capacity = float(payload.get("stadium_capacity", 80_000)) or 80_000.0
    match_minute = float(payload.get("match_minute", 58))
    gate_open_count = float(payload.get("gate_open_count", 12))
    gate_throughput_pct = float(payload.get("gate_capacity", 100))
    closed_gate_count = len(normalize_closed_gates(payload.get("closed_gates", [])))

    if "gate_capacity" not in payload:
        gate_throughput_pct = clamp((gate_open_count / 20.0) * 100.0, 35.0, 110.0)

    incident_count = float(
        payload.get("incident_count", payload.get("active_incidents", 0))
    )
    incident_count = max(incident_count, float(payload.get("medical_incidents", 0)))

    return {
        "attendance": attendance,
        "stadium_capacity": capacity,
        "attendance_ratio": clamp(attendance / capacity, 0.0, 1.25),
        "match_minute": match_minute,
        "match_phase_code": float(phase_code(match_minute)),
        "entry_rate_per_min": float(payload.get("entry_rate_per_min", 0)),
        "exit_rate_per_min": float(payload.get("exit_rate_per_min", 0)),
        "gate_throughput_pct": gate_throughput_pct,
        "gate_open_count": gate_open_count,
        "closed_gate_count": float(closed_gate_count),
        "temperature": float(payload.get("temperature", 25)),
        "humidity": float(payload.get("humidity", 60)),
        "rain_probability": float(payload.get("rain_probability", 0)),
        "security_staff": float(payload.get("security_staff", 300)),
        "incident_count": incident_count,
        "medical_incidents": float(payload.get("medical_incidents", 0)),
        "vip_event": 1.0 if payload.get("vip_event", False) else 0.0,
        "special_event": 1.0 if payload.get("special_event", True) else 0.0,
        "holiday": 1.0 if payload.get("holiday", False) else 0.0,
        "parking_occupancy": float(payload.get("parking_occupancy", 65)),
        "metro_arrivals": float(payload.get("metro_arrivals", 0)),
        "bus_arrivals": float(payload.get("bus_arrivals", 0)),
        "ticket_scan_rate": float(payload.get("ticket_scan_rate", 0)),
        "security_queue_length": float(payload.get("security_queue_length", 0)),
        "food_court_density": float(payload.get("food_court_density", 40)),
        "restroom_density": float(payload.get("restroom_density", 35)),
        "previous_congestion": float(payload.get("previous_congestion", 45)),
        "incident_type_code": float(
            INCIDENT_TYPE_CODES.get(str(payload.get("incident_type", "Operational")), 0)
        ),
        "forecast_hour": float(payload.get("forecast_hour", 0)),
        "phase_intensity": phase_intensity(match_minute),
    }


def density_for_context(base: Mapping[str, float], zone_weight: float, gate_weight: float) -> float:
    ingress_pressure = base["entry_rate_per_min"] / max(base["gate_open_count"], 1.0)
    transport_pressure = (base["metro_arrivals"] + base["bus_arrivals"]) / 130.0
    weather_pressure = base["rain_probability"] * 0.13
    return clamp(
        base["attendance_ratio"] * 72.0 * zone_weight
        + ingress_pressure * 0.09 * gate_weight
        + transport_pressure
        + weather_pressure
        + base["previous_congestion"] * 0.18,
        0.0,
        140.0,
    )


def feature_row(
    payload: Mapping[str, Any],
    *,
    zone_code: float = 0,
    zone_capacity: float = 2000,
    zone_weight: float = 1.0,
    gate_code: float = 0,
    gate_weight: float = 1.0,
    forecast_hour: float | None = None,
    incident_type_code: float | None = None,
) -> dict[str, float]:
    base = base_features_from_payload(payload)
    if forecast_hour is not None:
        base["forecast_hour"] = float(forecast_hour)
    if incident_type_code is not None:
        base["incident_type_code"] = float(incident_type_code)

    row = {
        **base,
        "zone_code": float(zone_code),
        "zone_capacity": float(zone_capacity),
        "zone_weight": float(zone_weight),
        "gate_code": float(gate_code),
        "gate_weight": float(gate_weight),
    }
    row["crowd_density"] = density_for_context(row, zone_weight, gate_weight)
    return row


def zone_feature_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    gate_by_id = {gate["gate_id"]: gate for gate in GATE_PROFILES}

    for zone in ZONE_PROFILES:
        gate = gate_by_id.get(str(zone["gate_id"]), GATE_PROFILES[0])
        rows.append(
            {
                "meta": zone,
                "features": feature_row(
                    payload,
                    zone_code=float(zone["zone_code"]),
                    zone_capacity=float(zone["capacity"]),
                    zone_weight=float(zone["weight"]),
                    gate_code=float(gate["gate_code"]),
                    gate_weight=float(gate["weight"]),
                ),
            }
        )
    return rows


def gate_feature_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    closed_gates = normalize_closed_gates(payload.get("closed_gates", []))
    zone_by_id = {zone["zone_id"]: zone for zone in ZONE_PROFILES}
    rows = []

    for gate in GATE_PROFILES:
        zone = zone_by_id.get(str(gate["zone_id"]), ZONE_PROFILES[0])
        features = feature_row(
            payload,
            zone_code=float(zone["zone_code"]),
            zone_capacity=float(zone["capacity"]),
            zone_weight=float(zone["weight"]),
            gate_code=float(gate["gate_code"]),
            gate_weight=float(gate["weight"]),
        )
        if str(gate["gate_id"]).upper() in closed_gates:
            features["gate_throughput_pct"] = 8.0
            features["closed_gate_count"] = max(features["closed_gate_count"], 1.0)
            features["crowd_density"] = density_for_context(
                features,
                float(zone["weight"]) * 1.2,
                float(gate["weight"]) * 1.4,
            )
        rows.append({"meta": gate, "features": features})
    return rows


def attendance_feature_rows(
    payload: Mapping[str, Any],
    forecast_hours: int,
) -> list[dict[str, Any]]:
    hours = range(0, max(1, forecast_hours) + 1)
    return [
        {
            "meta": {"hour_offset": hour},
            "features": feature_row(payload, forecast_hour=float(hour)),
        }
        for hour in hours
    ]


def vendor_feature_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    zone_by_id = {zone["zone_id"]: zone for zone in ZONE_PROFILES}
    rows = []

    for vendor in VENDOR_ZONES:
        zone = zone_by_id.get(str(vendor["zone_id"]), ZONE_PROFILES[0])
        rows.append(
            {
                "meta": vendor,
                "features": feature_row(
                    payload,
                    zone_code=float(zone["zone_code"]),
                    zone_capacity=float(zone["capacity"]),
                    zone_weight=float(zone["weight"]),
                ),
            }
        )
    return rows


def parking_feature_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "meta": parking,
            "features": feature_row(
                payload,
                zone_code=float(index + 7),
                zone_capacity=float(parking["capacity"]),
                zone_weight=float(parking["weight"]),
            ),
        }
        for index, parking in enumerate(PARKING_AREAS)
    ]


def traffic_feature_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "meta": corridor,
            "features": feature_row(
                payload,
                zone_code=float(index + 10),
                zone_weight=float(corridor["weight"]),
            ),
        }
        for index, corridor in enumerate(TRAFFIC_CORRIDORS)
    ]


def emergency_feature_row(payload: Mapping[str, Any]) -> dict[str, Any]:
    incident_type = str(payload.get("incident_type", "Operational"))
    if payload.get("medical_incidents", 0) > 0:
        incident_type = "Medical Emergency"
    elif payload.get("rain_probability", 0) > 70:
        incident_type = "Weather Alert"
    elif payload.get("security_queue_length", 0) > 350:
        incident_type = "Crowd Congestion"

    return {
        "meta": {"incident_type": incident_type},
        "features": feature_row(
            payload,
            incident_type_code=float(INCIDENT_TYPE_CODES.get(incident_type, 0)),
        ),
    }


def ensure_feature_frame(rows: list[Mapping[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    for column in FEATURE_COLUMNS:
        if column not in frame:
            frame[column] = 0.0
    return frame[FEATURE_COLUMNS].fillna(0.0)
