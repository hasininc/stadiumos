from typing import List, Dict, Optional
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Maps zone_id -> list of active websockets subscribing to it
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Global connection pool
        self.global_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, zone_id: Optional[str] = None):
        await websocket.accept()
        self.global_connections.append(websocket)
        
        if zone_id:
            if zone_id not in self.active_connections:
                self.active_connections[zone_id] = []
            self.active_connections[zone_id].append(websocket)

    def disconnect(self, websocket: WebSocket, zone_id: Optional[str] = None):
        if websocket in self.global_connections:
            self.global_connections.remove(websocket)
        
        if zone_id and zone_id in self.active_connections:
            if websocket in self.active_connections[zone_id]:
                self.active_connections[zone_id].remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_global(self, message: dict):
        for connection in self.global_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Handle dead/closed connection cleanups
                self.global_connections.remove(connection)

    async def broadcast_to_zone(self, zone_id: str, message: dict):
        if zone_id in self.active_connections:
            for connection in self.active_connections[zone_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    self.active_connections[zone_id].remove(connection)

# Singleton Instance
ws_manager = ConnectionManager()
