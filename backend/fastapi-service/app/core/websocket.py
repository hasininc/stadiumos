import asyncio
import json
import logging
import random
from typing import List, Dict, Any, Optional
from fastapi import WebSocket

logger = logging.getLogger("fastapi")

class LiveConnectionManager:
    def __init__(self):
        # Global connection pool
        self.active_connections: List[WebSocket] = []
        # Maps zone_id -> list of active websockets subscribing to it
        self.zone_connections: Dict[str, List[WebSocket]] = {}
        self._lock = asyncio.Lock()
        self.simulation_task: Optional[asyncio.Task] = None
        self.is_simulating = False
        
    async def connect(self, websocket: WebSocket, zone_id: Optional[str] = None):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
            if zone_id:
                if zone_id not in self.zone_connections:
                    self.zone_connections[zone_id] = []
                self.zone_connections[zone_id].append(websocket)
        logger.info(f"New client connected. Zone: {zone_id} | Total: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket, zone_id: Optional[str] = None):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            if zone_id and zone_id in self.zone_connections:
                if websocket in self.zone_connections[zone_id]:
                    self.zone_connections[zone_id].remove(websocket)
        logger.info(f"Client disconnected. Zone: {zone_id} | Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")

    async def broadcast(self, message: dict):
        await self.broadcast_global(message)

    async def broadcast_global(self, message: dict):
        async with self._lock:
            connections = list(self.active_connections)
            
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed broadcasting, removing active connection: {e}")
                async with self._lock:
                    if connection in self.active_connections:
                        self.active_connections.remove(connection)

    async def broadcast_to_zone(self, zone_id: str, message: dict):
        async with self._lock:
            if zone_id not in self.zone_connections:
                return
            connections = list(self.zone_connections[zone_id])
            
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed broadcasting to zone, removing active connection: {e}")
                async with self._lock:
                    if connection in self.zone_connections[zone_id]:
                        self.zone_connections[zone_id].remove(connection)

    # ──────────────────────────────────────────────
    # Simulation Event Loop
    # ──────────────────────────────────────────────
    async def start_simulation(self):
        if self.is_simulating:
            return
        self.is_simulating = True
        self.simulation_task = asyncio.create_task(self._run_simulation_loop())
        logger.info("Live simulation engine started in background task.")

    async def stop_simulation(self):
        self.is_simulating = False
        if self.simulation_task:
            self.simulation_task.cancel()
            self.simulation_task = None
        logger.info("Live simulation engine stopped.")

    async def _run_simulation_loop(self):
        event_types = [
            'PredictionUpdated', 'CrowdDensityUpdated', 'IncidentCreated',
            'GateStatusChanged', 'EmergencyAlert', 'WeatherUpdated',
            'NotificationCreated'
        ]
        gates = ['A', 'B', 'C', 'D']
        severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        locations = ['Gate A Ingress', 'Food Court A', 'Concourse Level 2', 'South Parking Lot']
        weather_conditions = ['CLEAR', 'RAINY', 'STORMY', 'OVERCAST']
        
        try:
            while self.is_simulating:
                await asyncio.sleep(random.uniform(3.5, 6.5)) # every few seconds
                
                # Pick a random event type to broadcast
                event = random.choice(event_types)
                payload: Dict[str, Any] = {}
                
                if event == 'PredictionUpdated':
                    payload = {
                        'congestion_score': round(random.uniform(40.0, 95.0), 1),
                        'risk': random.choice(['MEDIUM', 'HIGH', 'CRITICAL'])
                    }
                elif event == 'CrowdDensityUpdated':
                    payload = {
                        'zone': random.choice(gates),
                        'density': round(random.uniform(45.0, 90.0), 1)
                    }
                elif event == 'GateStatusChanged':
                    payload = {
                        'gate': random.choice(gates),
                        'status': random.choice(['OPEN', 'CLOSED', 'RESTRICTED'])
                    }
                elif event == 'EmergencyAlert':
                    payload = {
                        'location': random.choice(locations),
                        'severity': random.choice(severities)
                    }
                elif event == 'WeatherUpdated':
                    payload = {
                        'condition': random.choice(weather_conditions),
                        'temperature': round(random.uniform(15.0, 32.0), 1)
                    }
                elif event == 'NotificationCreated':
                    payload = {
                        'id': random.randint(100, 999),
                        'message': 'Ingress flow exceeds normal baseline parameters.'
                    }
                elif event == 'IncidentCreated':
                    payload = {
                        'id': random.randint(200, 999),
                        'type': 'Crowd Surge',
                        'location': 'Gate B Entry'
                    }

                await self.broadcast({
                    'type': event,
                    'data': payload,
                    'timestamp': asyncio.get_event_loop().time()
                })
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in simulation loop: {e}", exc_info=True)

# Instantiation & backward compatibility variables mapping
live_ws_manager = LiveConnectionManager()
ws_manager = live_ws_manager
