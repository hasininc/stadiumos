"""Reproducible synthetic stadium operations datasets."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import FEATURE_COLUMNS, INCIDENT_TYPE_CODES
from .feature_engineering import clamp


def _risk_label(score: np.ndarray) -> np.ndarray:
    labels = np.full(score.shape, "Safe", dtype=object)
    labels[score >= 38] = "Moderate"
    labels[score >= 64] = "High"
    labels[score >= 86] = "Critical"
    return labels


def _emergency_label(score: np.ndarray) -> np.ndarray:
    labels = np.full(score.shape, "Low", dtype=object)
    labels[score >= 34] = "Medium"
    labels[score >= 62] = "High"
    labels[score >= 84] = "Critical"
    return labels


def generate_synthetic_stadium_dataset(
    n_samples: int = 2400,
    random_state: int = 42,
) -> pd.DataFrame:
    """Create deterministic training data that mimics matchday operations."""
    rng = np.random.default_rng(random_state)

    stadium_capacity = rng.choice([72_000, 80_000, 86_000], size=n_samples)
    attendance_ratio = rng.beta(4.2, 1.8, size=n_samples) * 1.08
    attendance = np.clip(
        attendance_ratio * stadium_capacity + rng.normal(0, 1400, n_samples),
        0,
        stadium_capacity,
    )
    attendance_ratio = attendance / stadium_capacity

    match_minute = rng.integers(-120, 151, size=n_samples)
    match_phase_code = np.select(
        [
            match_minute < 0,
            match_minute <= 45,
            match_minute <= 60,
            match_minute <= 105,
        ],
        [0, 1, 2, 3],
        default=4,
    )
    phase_intensity = np.choose(match_phase_code, [0.82, 0.78, 1.0, 0.86, 1.18])

    rain_probability = rng.beta(1.6, 3.5, size=n_samples) * 100
    temperature = np.clip(rng.normal(29, 7, n_samples), -5, 48)
    humidity = np.clip(44 + rain_probability * 0.45 + rng.normal(0, 12, n_samples), 5, 100)

    gate_open_count = rng.integers(4, 23, size=n_samples)
    closed_gate_count = rng.binomial(3, 0.18, size=n_samples)
    gate_throughput_pct = np.clip(
        (gate_open_count / 20) * 100
        - closed_gate_count * 13
        - rain_probability * 0.12
        + rng.normal(0, 8, n_samples),
        20,
        112,
    )

    entry_rate_per_min = np.clip(
        attendance_ratio * 520 * phase_intensity
        + rain_probability * 1.4
        + rng.normal(0, 45, n_samples),
        0,
        2000,
    )
    exit_rate_per_min = np.clip(
        attendance_ratio * 95 * np.where(match_phase_code == 4, 4.2, 1.0)
        + rng.normal(0, 24, n_samples),
        0,
        2000,
    )

    security_staff = rng.integers(180, 461, size=n_samples)
    incident_count = rng.poisson(1.3 + attendance_ratio * 2.2, size=n_samples)
    medical_incidents = rng.poisson(
        0.2 + attendance_ratio * 1.2 + np.maximum(temperature - 32, 0) * 0.05,
        size=n_samples,
    )
    vip_event = rng.binomial(1, 0.16, size=n_samples)
    special_event = rng.binomial(1, 0.7, size=n_samples)
    holiday = rng.binomial(1, 0.18, size=n_samples)

    metro_arrivals = np.clip(attendance_ratio * 1450 + rng.normal(0, 190, n_samples), 0, 10_000)
    bus_arrivals = np.clip(attendance_ratio * 650 + rng.normal(0, 120, n_samples), 0, 10_000)
    ticket_scan_rate = np.clip(
        entry_rate_per_min * (gate_throughput_pct / 100) + rng.normal(0, 35, n_samples),
        0,
        2000,
    )
    security_queue_length = np.clip(
        entry_rate_per_min / np.maximum(gate_open_count, 1) * 16
        + closed_gate_count * 62
        + rain_probability * 1.1
        - security_staff * 0.12
        + rng.normal(0, 35, n_samples),
        0,
        5000,
    )
    food_court_density = np.clip(
        attendance_ratio * 80
        + (match_phase_code == 2) * 20
        + rain_probability * 0.08
        + rng.normal(0, 9, n_samples),
        0,
        100,
    )
    restroom_density = np.clip(
        attendance_ratio * 64
        + (match_phase_code == 2) * 18
        + rng.normal(0, 10, n_samples),
        0,
        100,
    )
    parking_occupancy = np.clip(
        attendance_ratio * 92 + rain_probability * 0.04 + rng.normal(0, 7, n_samples),
        0,
        100,
    )

    zone_code = rng.integers(1, 13, size=n_samples)
    zone_weight = np.clip(rng.normal(1.0, 0.18, n_samples), 0.55, 1.38)
    zone_capacity = rng.integers(800, 5200, size=n_samples)
    gate_code = rng.integers(1, 6, size=n_samples)
    gate_weight = np.clip(rng.normal(1.0, 0.2, n_samples), 0.5, 1.45)
    incident_type_code = rng.integers(0, len(INCIDENT_TYPE_CODES), size=n_samples)
    forecast_hour = rng.integers(0, 8, size=n_samples)

    previous_congestion = np.clip(
        attendance_ratio * 58
        + security_queue_length * 0.045
        + rain_probability * 0.08
        + rng.normal(0, 12, n_samples),
        0,
        100,
    )
    crowd_density = np.clip(
        attendance_ratio * 72 * zone_weight
        + entry_rate_per_min / np.maximum(gate_open_count, 1) * 0.09 * gate_weight
        + (metro_arrivals + bus_arrivals) / 130
        + rain_probability * 0.13
        + previous_congestion * 0.18,
        0,
        140,
    )

    congestion_score = np.clip(
        crowd_density * 0.48
        + previous_congestion * 0.22
        + (100 - gate_throughput_pct) * 0.24
        + rain_probability * 0.08
        + incident_count * 2.8
        + vip_event * 4.5
        - security_staff * 0.035
        + rng.normal(0, 4.5, n_samples),
        0,
        100,
    )
    queue_wait_minutes = np.clip(
        2
        + congestion_score * 0.34
        + entry_rate_per_min / np.maximum(gate_open_count, 1) * 0.028
        + closed_gate_count * 4.2
        + rain_probability * 0.045
        - security_staff * 0.018
        + rng.normal(0, 2.4, n_samples),
        1,
        90,
    )
    attendance_forecast = np.clip(
        attendance
        + forecast_hour * 60 * (entry_rate_per_min * (match_phase_code <= 2))
        - forecast_hour * 50 * (exit_rate_per_min * (match_phase_code >= 3))
        - rain_probability * 38 * forecast_hour
        + rng.normal(0, 950, n_samples),
        0,
        stadium_capacity,
    )
    risk_score = np.clip(
        congestion_score
        + incident_count * 3.2
        + medical_incidents * 2.6
        + rain_probability * 0.08
        + (100 - gate_throughput_pct) * 0.06,
        0,
        100,
    )
    emergency_score = np.clip(
        incident_type_code * 8
        + congestion_score * 0.45
        + medical_incidents * 8
        + rain_probability * 0.08
        + attendance_ratio * 12
        + rng.normal(0, 6, n_samples),
        0,
        100,
    )
    security_required = np.clip(
        130
        + congestion_score * 2.7
        + incident_count * 11
        + vip_event * 28
        + closed_gate_count * 18
        - gate_open_count * 1.7
        + rng.normal(0, 12, n_samples),
        80,
        650,
    )
    medical_cases = np.clip(
        0.4
        + attendance_ratio * 8.4
        + np.maximum(temperature - 31, 0) * 0.25
        + humidity * 0.025
        + congestion_score * 0.035
        + medical_incidents * 1.6
        + rng.normal(0, 1.1, n_samples),
        0,
        40,
    )
    vendor_food_units = np.clip(
        attendance_ratio * 2100
        + food_court_density * 22
        + (match_phase_code == 2) * 420
        + rng.normal(0, 120, n_samples),
        0,
        8000,
    )
    vendor_beverage_units = np.clip(
        attendance_ratio * 2400
        + np.maximum(temperature - 25, 0) * 80
        + humidity * 8
        + rng.normal(0, 150, n_samples),
        0,
        9000,
    )
    vendor_merch_units = np.clip(
        attendance_ratio * 760
        + vip_event * 120
        + special_event * 170
        + rng.normal(0, 80, n_samples),
        0,
        3000,
    )
    parking_utilization = np.clip(
        parking_occupancy * 0.72
        + attendance_ratio * 24
        + rain_probability * 0.035
        + rng.normal(0, 3.5, n_samples),
        0,
        100,
    )
    traffic_in = np.clip(
        attendance_ratio * 52
        + metro_arrivals * 0.012
        + bus_arrivals * 0.018
        + rain_probability * 0.12
        + (match_phase_code <= 1) * 12
        + rng.normal(0, 4, n_samples),
        0,
        100,
    )
    traffic_out = np.clip(
        attendance_ratio * 42
        + exit_rate_per_min * 0.04
        + rain_probability * 0.11
        + (match_phase_code >= 3) * 20
        + rng.normal(0, 5, n_samples),
        0,
        100,
    )
    weather_attendance_impact = np.clip(
        rain_probability * 0.23
        + np.maximum(temperature - 34, 0) * 1.2
        + np.maximum(6 - temperature, 0) * 0.9,
        0,
        45,
    )
    weather_congestion_impact = np.clip(rain_probability * 0.19 + humidity * 0.03, 0, 40)
    weather_queue_impact = np.clip(rain_probability * 0.21 + (100 - gate_throughput_pct) * 0.08, 0, 45)
    weather_risk_impact = np.clip(
        rain_probability * 0.16 + np.maximum(temperature - 33, 0) * 1.3,
        0,
        45,
    )

    frame = pd.DataFrame(
        {
            "attendance": attendance,
            "stadium_capacity": stadium_capacity,
            "attendance_ratio": attendance_ratio,
            "match_minute": match_minute,
            "match_phase_code": match_phase_code,
            "entry_rate_per_min": entry_rate_per_min,
            "exit_rate_per_min": exit_rate_per_min,
            "gate_throughput_pct": gate_throughput_pct,
            "gate_open_count": gate_open_count,
            "closed_gate_count": closed_gate_count,
            "temperature": temperature,
            "humidity": humidity,
            "rain_probability": rain_probability,
            "security_staff": security_staff,
            "incident_count": incident_count,
            "medical_incidents": medical_incidents,
            "vip_event": vip_event,
            "special_event": special_event,
            "holiday": holiday,
            "parking_occupancy": parking_occupancy,
            "metro_arrivals": metro_arrivals,
            "bus_arrivals": bus_arrivals,
            "ticket_scan_rate": ticket_scan_rate,
            "security_queue_length": security_queue_length,
            "food_court_density": food_court_density,
            "restroom_density": restroom_density,
            "previous_congestion": previous_congestion,
            "zone_code": zone_code,
            "zone_capacity": zone_capacity,
            "zone_weight": zone_weight,
            "gate_code": gate_code,
            "gate_weight": gate_weight,
            "incident_type_code": incident_type_code,
            "forecast_hour": forecast_hour,
            "crowd_density": crowd_density,
            "phase_intensity": phase_intensity,
            "congestion_score": congestion_score,
            "queue_wait_minutes": queue_wait_minutes,
            "attendance_forecast": attendance_forecast,
            "risk_level": _risk_label(risk_score),
            "emergency_severity": _emergency_label(emergency_score),
            "security_required": security_required,
            "medical_cases": medical_cases,
            "vendor_food_units": vendor_food_units,
            "vendor_beverage_units": vendor_beverage_units,
            "vendor_merch_units": vendor_merch_units,
            "parking_utilization": parking_utilization,
            "traffic_in_congestion": traffic_in,
            "traffic_out_congestion": traffic_out,
            "weather_attendance_impact": weather_attendance_impact,
            "weather_congestion_impact": weather_congestion_impact,
            "weather_queue_impact": weather_queue_impact,
            "weather_risk_impact": weather_risk_impact,
        }
    )

    for column in FEATURE_COLUMNS:
        frame[column] = frame[column].map(lambda value: clamp(float(value), -1_000_000, 1_000_000))

    return frame
