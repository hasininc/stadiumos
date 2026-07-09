"""
Backend integration client for the Edge CV service.
Handles:
  - OAuth2 form-login to obtain JWT bearer tokens
  - REST POST of crowd snapshots
  - WebSocket connection for real-time event broadcast (resilient reconnect)
"""
import os
import time
import logging
import requests
import json
import threading
from typing import Dict, Any, Optional

# pyrefly: ignore [missing-import]
import websocket

logger = logging.getLogger("cv-edge")


class BackendIntegrationClient:
    def __init__(
        self,
        api_url: str,
        ws_url: str,
        camera_id: str,
        zone_id: str,
    ):
        self.api_url = api_url.rstrip("/")
        self.ws_url = ws_url
        self.camera_id = camera_id
        self.zone_id = zone_id

        self.access_token: Optional[str] = None
        self.headers: Dict[str, str] = {}

        # WebSocket state
        self.ws: Optional[websocket.WebSocketApp] = None
        self.ws_thread: Optional[threading.Thread] = None
        self.ws_connected = False
        self._ws_stop = False
        self._reconnect_delay = 3.0

        # REST failure counter (avoid log spam)
        self._rest_fail_count = 0

    # ──────────────────────────────────────────────
    # Authentication
    # ──────────────────────────────────────────────
    def authenticate(self) -> bool:
        login_url = f"{self.api_url}/api/v1/auth/login"
        payload = {
            "email": os.getenv("CV_EDGE_OPERATOR_EMAIL", "operator@stadiumos.dev"),
            "password": os.getenv("CV_EDGE_OPERATOR_PASSWORD", "operator123"),
}
        try:
            res = requests.post(login_url, json=payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                self.access_token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.access_token}"}
                logger.info("Backend authentication successful.")
                self._discover_zone_id()
                return True
            logger.warning(f"Auth failed ({res.status_code}): {res.text[:200]}")
        except requests.ConnectionError:
            logger.warning("Backend unreachable for authentication — will retry later.")
        except Exception as e:
            logger.error(f"Auth error: {e}")
        return False

    def _discover_zone_id(self):
        """Auto-discover real zone UUID from backend to match config zone name."""
        try:
            res = requests.get(
                f"{self.api_url}/api/v1/crowd/zones",
                headers=self.headers, timeout=5,
            )
            if res.status_code == 200:
                zones = res.json()
                if zones:
                    # Use the first zone as default; can be mapped by name later
                    self.zone_id = zones[0]["id"]
                    logger.info(
                        f"Auto-discovered zone: {zones[0]['name']} ({self.zone_id})"
                    )
        except Exception as e:
            logger.warning(f"Zone discovery failed: {e}")

    # ──────────────────────────────────────────────
    # REST Snapshot
    # ──────────────────────────────────────────────
    def send_snapshot(self, people_count: int) -> bool:
        snapshot_url = f"{self.api_url}/api/v1/crowd/snapshot"
        payload = {"zone_id": self.zone_id, "headcount": people_count}

        if not self.access_token:
            if not self.authenticate():
                return False

        try:
            res = requests.post(
                snapshot_url, json=payload, headers=self.headers, timeout=3
            )
            if res.status_code in (200, 201):
                self._rest_fail_count = 0
                return True
            if res.status_code == 401:
                self.access_token = None
                if self.authenticate():
                    return self.send_snapshot(people_count)
            # Log sparingly
            self._rest_fail_count += 1
            if self._rest_fail_count <= 3 or self._rest_fail_count % 20 == 0:
                logger.warning(
                    f"Snapshot POST failed ({res.status_code}): {res.text[:120]}"
                )
        except requests.ConnectionError:
            self._rest_fail_count += 1
            if self._rest_fail_count <= 2:
                logger.warning("Backend unreachable for snapshot POST.")
        except Exception as e:
            logger.error(f"Snapshot error: {e}")
        return False

    # ──────────────────────────────────────────────
    # WebSocket Broadcast
    # ──────────────────────────────────────────────
    def start_ws_connection(self):
        if self.ws_connected or self._ws_stop:
            return
        self._ws_stop = False

        websocket.enableTrace(False)

        self.ws_thread = threading.Thread(
            target=self._ws_run_loop, daemon=True
        )
        self.ws_thread.start()

    def _ws_run_loop(self):
        """Run the WS with built-in reconnect."""
        while not self._ws_stop:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_ws_open,
                on_message=self._on_ws_message,
                on_error=self._on_ws_error,
                on_close=self._on_ws_close,
            )
            try:
                logger.info(f"Connecting to WebSocket at {self.ws_url} …")
                self.ws.run_forever(ping_interval=10, ping_timeout=5)
            except Exception as e:
                logger.warning(f"WS run_forever exception: {e}")
            if self._ws_stop:
                break
            logger.info(
                f"WebSocket disconnected — reconnecting in {self._reconnect_delay}s …"
            )
            time.sleep(self._reconnect_delay)

    def _on_ws_open(self, ws):
        logger.info("WebSocket connection established.")
        self.ws_connected = True

    def _on_ws_message(self, ws, message):
        pass  # Edge service is a publisher, not a subscriber

    def _on_ws_error(self, ws, error):
        # Only log novel errors, not repeated 404s
        err_str = str(error)
        if "404" in err_str:
            logger.debug("WS endpoint not found (404) — backend may need restart.")
        else:
            logger.warning(f"WS error: {err_str[:200]}")

    def _on_ws_close(self, ws, close_status_code, close_msg):
        self.ws_connected = False

    def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        if not self.ws_connected or self.ws is None:
            return  # Silently skip if WS is down; it will reconnect

        payload = json.dumps(
            {"type": event_type, "data": data, "timestamp": time.time()}
        )
        try:
            self.ws.send(payload)
        except Exception:
            self.ws_connected = False

    def close(self):
        self._ws_stop = True
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None
        self.ws_connected = False
