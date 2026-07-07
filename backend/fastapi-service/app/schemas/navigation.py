from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class RouteRequest(BaseModel):
    start_node_id: str
    end_node_id: str
    routing_profile: str = Field("Shortest", pattern="^(Shortest|Fastest|Safest|LeastCrowded)$")
    requires_accessibility: bool = False

class RouteNodeResponse(BaseModel):
    id: str
    name: str
    zone_id: str
    type: str
    floor: str

class RouteResponse(BaseModel):
    path_nodes: List[RouteNodeResponse]
    total_distance_meters: float
    estimated_time_seconds: float
    routing_profile: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    timestamp: str

class RerouteRequest(BaseModel):
    current_node_id: str
    end_node_id: str
    avoid_zones: List[str] = []
    requires_accessibility: bool = False

class MapNodeResponse(BaseModel):
    id: str
    name: str
    zone_id: str
    type: str
    x: float
    y: float
    floor: str
    is_wheelchair_accessible: bool

    class Config:
        from_attributes = True

class MapEdgeResponse(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    distance: float
    base_weight: float
    current_weight: float
    is_wheelchair_accessible: bool

    class Config:
        from_attributes = True

class MapGraphResponse(BaseModel):
    nodes: List[MapNodeResponse]
    edges: List[MapEdgeResponse]
