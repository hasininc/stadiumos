from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from src.api.deps import RoleChecker
from src.schemas.ai import ChatRequest, ChatResponse, QueryRequest, DecisionRequest, AgentResponse, ToolResponse
from src.services.orchestrator import agent_orchestrator
from src.tools.registry import tool_registry
from src.core.redis_client import redis_client
from typing import List, Optional
import logging

logger = logging.getLogger("ai-orchestrator")

router = APIRouter()

# RBAC permission groups
security_or_ops = RoleChecker(["Security Staff", "Operations Manager", "Administrator"])

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_orchestrator(req: ChatRequest, roles: List[str] = Depends(security_or_ops)):
    return agent_orchestrator.run_orchestration(req.message, req.session_id)

@router.post("/query", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def query_orchestrator(req: QueryRequest, roles: List[str] = Depends(security_or_ops)):
    return agent_orchestrator.run_orchestration(req.query, "generic_query_session")

@router.post("/decision", status_code=status.HTTP_200_OK)
def evaluate_decision(req: DecisionRequest, roles: List[str] = Depends(security_or_ops)):
    return agent_orchestrator.evaluate_decision_scenario(req)

@router.get("/history")
def get_session_history(session_id: str = Query(..., description="Target Session ID"), roles: List[str] = Depends(security_or_ops)):
    cached = redis_client.get_cache(f"ai:history:{session_id}")
    if cached:
        return cached
    return []

@router.get("/agents", response_model=List[AgentResponse])
def list_agents(roles: List[str] = Depends(security_or_ops)):
    return agent_orchestrator.get_agent_directory()

@router.get("/tools", response_model=List[ToolResponse])
def list_tools(roles: List[str] = Depends(security_or_ops)):
    tools = tool_registry.list_tools()
    formatted = []
    for t in tools:
        formatted.append(
            ToolResponse(
                name=t["name"],
                description=t["description"],
                parameters={}
            )
        )
    return formatted

@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "langgraph_loaded": True,
        "agents_count": len(agent_orchestrator.get_agent_directory()),
        "tools_count": len(tool_registry.list_tools())
    }

# Live WS Conversation feed broadcast
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            try:
                res = agent_orchestrator.run_orchestration(message, session_id)
                await websocket.send_json(res.dict())
            except Exception as e:
                await websocket.send_json({"error": str(e)})
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from conversational session {session_id}")
