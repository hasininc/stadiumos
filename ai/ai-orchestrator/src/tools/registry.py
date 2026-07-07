import logging
from typing import Dict, Any, List

logger = logging.getLogger("ai-orchestrator")

class ToolRegistry:
    def __init__(self):
        self.tools_meta = {
            "get_crowd_status": "Retrieves real-time headcount and occupancy percentages for a specific stadium zone.",
            "get_predictions": "Queries the ML service for forecasted queue wait durations and bottleneck congestion metrics.",
            "get_camera_events": "Fetches YOLO detection records from cameras (e.g. falls, object violations).",
            "get_medical_alerts": "Fetches current active medical alarms from emergency response centers.",
            "get_vendor_inventory": "Checks stock availability and inventory counts at specific concession booths.",
            "get_transport_status": "Checks bus arrival timings and loop route delays.",
            "assign_volunteer": "Coordinates and maps a volunteer assignment request to a target area.",
            "trigger_notification": "Dispatches localized mobile app alerts to specific seating rows/staff.",
            "generate_route": "Generates evacuation paths or optimal transit maps for crowd redirects.",
            "fetch_knowledge_base": "Retrieves matches, security manuals, and FIFA regulations from RAG indices."
        }

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Executing tool '{tool_name}' with parameters: {params}")
        
        if tool_name == "get_crowd_status":
            zone_id = params.get("zone_id", "ZONE_GENERAL")
            return {"status": "success", "zone_id": zone_id, "headcount": 1450, "occupancy_pct": 72.5, "state": "Busy"}
            
        elif tool_name == "get_predictions":
            zone_id = params.get("zone_id", "ZONE_GENERAL")
            return {"status": "success", "zone_id": zone_id, "predicted_wait_seconds": 240.0, "confidence": 0.94}
            
        elif tool_name == "get_camera_events":
            camera_id = params.get("camera_id", "CAM-01")
            return {"status": "success", "camera_id": camera_id, "detections": [{"type": "QueueLength", "length": 18}]}
            
        elif tool_name == "get_medical_alerts":
            return {"status": "success", "active_alerts": [{"id": "MED-903", "zone_id": "ZONE_SEC_104", "type": "Heat Exhaustion", "severity": "High"}]}
            
        elif tool_name == "get_vendor_inventory":
            vendor_id = params.get("vendor_id", "VENDOR_KIOSK_4")
            return {"status": "success", "vendor_id": vendor_id, "inventory": {"ponchos": 12, "water_bottles": 400}, "alert": "Ponchos stock critical"}
            
        elif tool_name == "get_transport_status":
            return {"status": "success", "active_routes": [{"loop_id": "LOOP_EAST", "active_shuttles": 4, "traffic_delay_seconds": 120}]}
            
        elif tool_name == "assign_volunteer":
            vol_id = params.get("volunteer_id", "VOL-702")
            zone_id = params.get("zone_id", "ZONE_GATE_A")
            return {"status": "success", "volunteer_id": vol_id, "assigned_zone": zone_id, "task": "Direct crowd at Gate A"}
            
        elif tool_name == "trigger_notification":
            topic = params.get("topic", "crowd_redirect")
            msg = params.get("message", "")
            return {"status": "success", "dispatched_topic": topic, "recipients_count": 450}
            
        elif tool_name == "generate_route":
            from_zone = params.get("from_zone")
            to_zone = params.get("to_zone")
            return {"status": "success", "path": [from_zone, "CONCOURSE_EAST", "PARKING_LOT_C"], "est_evac_time_mins": 6.5}
            
        elif tool_name == "fetch_knowledge_base":
            query = params.get("query", "")
            return {"status": "success", "context": "FIFA World Cup Regulations Section 4.2 states that gate queues exceeding 15 minutes trigger voluntary redirect recommendations."}
            
        else:
            return {"status": "error", "message": f"Tool '{tool_name}' is not registered in the system."}

    def list_tools(self) -> List[dict]:
        return [
            {"name": k, "description": v}
            for k, v in self.tools_meta.items()
        ]

# Singleton instance
tool_registry = ToolRegistry()
