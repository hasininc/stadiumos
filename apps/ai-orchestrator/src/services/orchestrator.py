import logging
from typing import Dict, List, Any, Optional
from src.core.redis_client import redis_client
from src.core.kafka_client import kafka_client
from src.tools.registry import tool_registry
from src.services.rag import rag_service
from src.schemas.ai import ChatResponse, DecisionRequest
from shared.utils.error_handlers import ValidationError, AuthorizationError

logger = logging.getLogger("ai-orchestrator")

# Definition of the graph state payload structure
class OrchestratorState:
    def __init__(self, message: str, session_id: str):
        self.message = message
        self.session_id = session_id
        self.history: List[dict] = []
        self.current_agent: str = "OperationsManagerAgent"
        self.context: str = ""
        self.citations: List[str] = []
        self.recommended_actions: List[str] = []
        self.execution_logs: List[str] = []

class MultiAgentOrchestrator:
    def __init__(self):
        # Configure specialized agents metadata parameters
        self.agents_directory = {
            "CrowdAgent": {
                "role": "Crowd Density Monitor",
                "responsibilities": ["Inspect zone headcount", "Assess bottleneck risks"],
                "tools": ["get_crowd_status", "get_predictions"]
            },
            "SecurityAgent": {
                "role": "Physical Threat Protection Coordinator",
                "responsibilities": ["Identify restricted intrusions", "Detect suspicious bags"],
                "tools": ["get_camera_events", "trigger_notification"]
            },
            "MedicalAgent": {
                "role": "First Aid Dispatcher",
                "responsibilities": ["Manage heat strokes", "Dispatch medical teams"],
                "tools": ["get_medical_alerts", "trigger_notification"]
            },
            "VendorAgent": {
                "role": "Concessions Inventory Logistics Manager",
                "responsibilities": ["Track stock velocities", "Dispatch refills"],
                "tools": ["get_vendor_inventory", "trigger_notification"]
            },
            "NavigationAgent": {
                "role": "Evacuation Route Planner",
                "responsibilities": ["Calculate evacuation paths", "Direct route signage"],
                "tools": ["generate_route"]
            },
            "TransportAgent": {
                "role": "Municipal Shuttle Dispatcher",
                "responsibilities": ["Monitor transit delays", "Coordinate shuttle dispatches"],
                "tools": ["get_transport_status"]
            },
            "VolunteerCoordinator": {
                "role": "Volunteer Staffing Allocations Coordinator",
                "responsibilities": ["Assign tasks", "Map personnel positioning"],
                "tools": ["assign_volunteer"]
            },
            "OperationsManagerAgent": {
                "role": "Central Chief Operations Coordinator",
                "responsibilities": ["Coordinate multi-agent decisions", "Authorize evacuations"],
                "tools": ["fetch_knowledge_base"]
            }
        }

    def _apply_safety_guardrails(self, message: str) -> None:
        # Prompt Injection Defense Checks
        payload_lower = message.lower()
        jailbreak_triggers = ["ignore original instructions", "system override", "bypass restrictions", "write system prompt"]
        for trigger in jailbreak_triggers:
            if trigger in payload_lower:
                logger.warning(f"Prompt injection pattern detected: '{trigger}'")
                raise ValidationError("Input message failed safety validation rules.")

    def run_orchestration(self, message: str, session_id: str) -> ChatResponse:
        self._apply_safety_guardrails(message)
        
        # Load conversation history from Redis Cache
        state = OrchestratorState(message, session_id)
        cached_history = redis_client.get_cache(f"ai:history:{session_id}")
        if cached_history:
            state.history = cached_history

        # 1. Routing / Decision Node: Determine target agent based on query intent
        state.current_agent = self._route_intent(message)
        state.execution_logs.append(f"Routing query to agent: {state.current_agent}")

        # 2. RAG Node: Search KB for context parameters
        matches = rag_service.search_kb(message)
        rag_context, citations = rag_service.build_context(matches)
        state.context = rag_context
        state.citations = citations

        # 3. Agent Execution Node
        response_text = self._execute_agent_node(state)

        # Update and save conversation history
        state.history.append({"user": message, "assistant": response_text})
        redis_client.set_cache(f"ai:history:{session_id}", state.history, ttl=1800)

        # Publish AIRecommendationGenerated event
        kafka_client.publish_event(
            "stadiumos.ai.recommendation",
            key=session_id,
            payload={
                "session_id": session_id,
                "agent": state.current_agent,
                "response": response_text,
                "citations": state.citations
            }
        )

        return ChatResponse(
            session_id=session_id,
            response_text=response_text,
            agent_name=state.current_agent,
            citations=state.citations,
            recommended_actions=state.recommended_actions
        )

    def evaluate_decision_scenario(self, req: DecisionRequest) -> dict:
        # Structured operations command orchestrator decisions
        zone = req.target_zone
        status = req.incident_context.get("status", "Normal")
        
        actions = []
        if status == "Critical":
            actions.append("Dispatch volunteer marshals to direct ingress paths.")
            actions.append("Send push notification redirect recommendations.")
            # Publish Emergency evacuation recommendation
            kafka_client.publish_event(
                "stadiumos.ai.emergency-response",
                key=zone,
                payload={"zone_id": zone, "status": "TriggerEvacuation", "reason": "Zone capacity overflow"}
            )
        else:
            actions.append("Maintain standard surveillance feeds.")
            
        return {
            "decision": "Orchestrator recommended redirect actions" if status == "Critical" else "Standard tracking",
            "actions": actions,
            "agent": "OperationsManagerAgent"
        }

    def _route_intent(self, msg: str) -> str:
        msg_lower = msg.lower()
        if "crowd" in msg_lower or "capacity" in msg_lower:
            return "CrowdAgent"
        elif "security" in msg_lower or "intrusion" in msg_lower or "bag" in msg_lower:
            return "SecurityAgent"
        elif "medical" in msg_lower or "heat" in msg_lower or "injury" in msg_lower:
            return "MedicalAgent"
        elif "vendor" in msg_lower or "concession" in msg_lower or "inventory" in msg_lower:
            return "VendorAgent"
        elif "route" in msg_lower or "evacuate" in msg_lower:
            return "NavigationAgent"
        elif "transport" in msg_lower or "bus" in msg_lower or "delay" in msg_lower:
            return "TransportAgent"
        elif "volunteer" in msg_lower or "assign" in msg_lower:
            return "VolunteerCoordinator"
        return "OperationsManagerAgent"

    def _execute_agent_node(self, state: OrchestratorState) -> str:
        agent = state.current_agent
        msg = state.message
        
        # Execute tool calls mapped to the target agent
        if agent == "CrowdAgent":
            res = tool_registry.execute_tool("get_crowd_status", {"zone_id": "ZONE_GATE_A"})
            pred = tool_registry.execute_tool("get_predictions", {"zone_id": "ZONE_GATE_A"})
            state.recommended_actions.append("Direct auxiliary volunteer teams to Section Gate A.")
            return f"Crowd Agent reports headcount of {res['headcount']} ({res['occupancy_pct']}%). Predictions estimate queues will reach {pred['predicted_wait_seconds']}s. Recommended action: Direct volunteers."
            
        elif agent == "SecurityAgent":
            res = tool_registry.execute_tool("get_camera_events", {"camera_id": "CAM-01"})
            state.recommended_actions.append("Dispatch security response team to Entrance A.")
            return f"Security Agent reports queue length of {res['detections'][0]['length']} at camera CAM-01. Recommended action: Deploy security responders."
            
        elif agent == "MedicalAgent":
            res = tool_registry.execute_tool("get_medical_alerts", {})
            state.recommended_actions.append("Deploy medical transport buggy to Section 104.")
            return f"Medical Agent reports heat exhaustion alarm: {res['active_alerts'][0]['type']} at section Section 104. Dispatching responders."
            
        elif agent == "VendorAgent":
            res = tool_registry.execute_tool("get_vendor_inventory", {"vendor_id": "VENDOR_4"})
            state.recommended_actions.append("Initiate reload shuttle transfer for poncho inventory.")
            return f"Vendor Agent reports low stock: {res['inventory']['ponchos']} ponchos at booth VENDOR_4. Reloading stock."
            
        elif agent == "NavigationAgent":
            res = tool_registry.execute_tool("generate_route", {"from_zone": "CONCOURSE_EAST", "to_zone": "LOT_C"})
            state.recommended_actions.append("Update digital exit sign boards to display route Path.")
            return f"Navigation Agent calculated evacuation route: {res['path']}. Estimated evacuation time: {res['est_evac_time_mins']} minutes."
            
        elif agent == "TransportAgent":
            res = tool_registry.execute_tool("get_transport_status", {})
            return f"Transport Agent reports bus delay on loop route: {res['active_routes'][0]['traffic_delay_seconds']}s delay."
            
        elif agent == "VolunteerCoordinator":
            res = tool_registry.execute_tool("assign_volunteer", {"volunteer_id": "VOL-802", "zone_id": "ZONE_GATE_A"})
            state.recommended_actions.append("Dispatch volunteer mapping tasks to volunteer app.")
            return f"Volunteer Coordinator assigned {res['volunteer_id']} to {res['assigned_zone']} ({res['task']})."
            
        else: # OperationsManagerAgent
            return f"Operations Manager Agent verified safety logs. FIFA Guidelines: Evacuation turnstile pulses should trigger if concourse bottlenecks are detected. Recommended action: Adjust gate turnstiles."

    def get_agent_directory(self) -> List[dict]:
        return [
            {
                "name": k,
                "role": v["role"],
                "responsibilities": v["responsibilities"],
                "available_tools": v["tools"]
            }
            for k, v in self.agents_directory.items()
        ]

# Singleton instance
agent_orchestrator = MultiAgentOrchestrator()
