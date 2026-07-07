from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to send to the orchestrator")
    session_id: str = Field(..., description="Active session context ID")

class ChatResponse(BaseModel):
    session_id: str
    response_text: str
    agent_name: str
    citations: Optional[List[str]] = None
    recommended_actions: Optional[List[str]] = None

class QueryRequest(BaseModel):
    query: str

class DecisionRequest(BaseModel):
    incident_context: Dict[str, Any]
    target_zone: str

class AgentResponse(BaseModel):
    name: str
    role: str
    responsibilities: List[str]
    available_tools: List[str]

class ToolResponse(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
