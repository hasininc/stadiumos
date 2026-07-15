"""Shared configuration for StadiumOS operations ML models."""

from __future__ import annotations

FEATURE_COLUMNS = [
    "attendance",
    "stadium_capacity",
    "attendance_ratio",
    "match_minute",
    "match_phase_code",
    "entry_rate_per_min",
    "exit_rate_per_min",
    "gate_throughput_pct",
    "gate_open_count",
    "closed_gate_count",
    "temperature",
    "humidity",
    "rain_probability",
    "security_staff",
    "incident_count",
    "medical_incidents",
    "vip_event",
    "special_event",
    "holiday",
    "parking_occupancy",
    "metro_arrivals",
    "bus_arrivals",
    "ticket_scan_rate",
    "security_queue_length",
    "food_court_density",
    "restroom_density",
    "previous_congestion",
    "zone_code",
    "zone_capacity",
    "zone_weight",
    "gate_code",
    "gate_weight",
    "incident_type_code",
    "forecast_hour",
    "crowd_density",
    "phase_intensity",
]

RISK_LABELS = ["Safe", "Moderate", "High", "Critical"]
EMERGENCY_LABELS = ["Low", "Medium", "High", "Critical"]

ZONE_PROFILES = [
    {
        "zone_id": "ZONE_GATE_A",
        "zone_name": "North Gate A",
        "zone_code": 1,
        "capacity": 2200,
        "weight": 1.18,
        "gate_id": "GATE_A",
    },
    {
        "zone_id": "ZONE_GATE_B",
        "zone_name": "South Gate B",
        "zone_code": 2,
        "capacity": 2100,
        "weight": 1.08,
        "gate_id": "GATE_B",
    },
    {
        "zone_id": "ZONE_VIP",
        "zone_name": "VIP Club Lounges",
        "zone_code": 3,
        "capacity": 900,
        "weight": 0.74,
        "gate_id": "GATE_VIP",
    },
    {
        "zone_id": "ZONE_FOOD_E",
        "zone_name": "East Food Concourse",
        "zone_code": 4,
        "capacity": 2400,
        "weight": 1.12,
        "gate_id": "GATE_D",
    },
    {
        "zone_id": "ZONE_PARK_C",
        "zone_name": "Parking Sector C",
        "zone_code": 5,
        "capacity": 2600,
        "weight": 0.95,
        "gate_id": "GATE_C",
    },
    {
        "zone_id": "ZONE_EXIT_4",
        "zone_name": "Northwest Exit 4 corridor",
        "zone_code": 6,
        "capacity": 1800,
        "weight": 0.86,
        "gate_id": "GATE_D",
    },
]

GATE_PROFILES = [
    {
        "gate_id": "GATE_A",
        "gate_name": "North Gate A",
        "gate_code": 1,
        "zone_id": "ZONE_GATE_A",
        "weight": 1.12,
    },
    {
        "gate_id": "GATE_B",
        "gate_name": "South Gate B",
        "gate_code": 2,
        "zone_id": "ZONE_GATE_B",
        "weight": 1.0,
    },
    {
        "gate_id": "GATE_C",
        "gate_name": "East Gate C",
        "gate_code": 3,
        "zone_id": "ZONE_PARK_C",
        "weight": 1.2,
    },
    {
        "gate_id": "GATE_D",
        "gate_name": "West Gate D",
        "gate_code": 4,
        "zone_id": "ZONE_EXIT_4",
        "weight": 0.86,
    },
    {
        "gate_id": "GATE_VIP",
        "gate_name": "VIP West Lobby",
        "gate_code": 5,
        "zone_id": "ZONE_VIP",
        "weight": 0.58,
    },
]

VENDOR_ZONES = [
    {"vendor_zone_id": "FOOD_E", "name": "East Food Court", "zone_id": "ZONE_FOOD_E"},
    {"vendor_zone_id": "FOOD_N", "name": "North Concourse Kiosks", "zone_id": "ZONE_GATE_A"},
    {"vendor_zone_id": "MERCH_VIP", "name": "VIP Merchandise", "zone_id": "ZONE_VIP"},
]

PARKING_AREAS = [
    {"parking_id": "PARK_A", "name": "North Parking A", "capacity": 4200, "weight": 0.92},
    {"parking_id": "PARK_B", "name": "South Parking B", "capacity": 5100, "weight": 1.05},
    {"parking_id": "PARK_C", "name": "East Parking C", "capacity": 3800, "weight": 1.16},
]

TRAFFIC_CORRIDORS = [
    {"corridor_id": "NORTH_ACCESS", "name": "North Access Road", "weight": 1.08},
    {"corridor_id": "SOUTH_RING", "name": "South Ring Road", "weight": 0.96},
    {"corridor_id": "METRO_LINK", "name": "Metro Link Road", "weight": 0.84},
]

INCIDENT_TYPE_CODES = {
    "Operational": 0,
    "Crowd Congestion": 1,
    "Medical Emergency": 2,
    "Security Alert": 3,
    "Fire Hazard": 4,
    "Weather Alert": 5,
    "System Error": 6,
}

FRIENDLY_FEATURE_NAMES = {
    "attendance": "attendance",
    "attendance_ratio": "stadium fill rate",
    "match_minute": "match phase",
    "match_phase_code": "match phase",
    "entry_rate_per_min": "entry rate",
    "exit_rate_per_min": "exit rate",
    "gate_throughput_pct": "gate throughput",
    "gate_open_count": "open gates",
    "closed_gate_count": "closed gates",
    "temperature": "temperature",
    "humidity": "humidity",
    "rain_probability": "rain probability",
    "security_staff": "security staff",
    "incident_count": "active incidents",
    "medical_incidents": "medical incidents",
    "vip_event": "VIP movement",
    "special_event": "event profile",
    "holiday": "holiday schedule",
    "parking_occupancy": "parking occupancy",
    "metro_arrivals": "metro arrivals",
    "bus_arrivals": "bus arrivals",
    "ticket_scan_rate": "ticket scan rate",
    "security_queue_length": "security queue length",
    "food_court_density": "food court density",
    "restroom_density": "restroom density",
    "previous_congestion": "previous congestion",
    "zone_code": "zone profile",
    "zone_capacity": "zone capacity",
    "zone_weight": "zone pressure profile",
    "gate_code": "gate profile",
    "gate_weight": "gate pressure profile",
    "incident_type_code": "incident type",
    "forecast_hour": "forecast horizon",
    "crowd_density": "crowd density",
    "phase_intensity": "phase intensity",
}
