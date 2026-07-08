"""
Core stream processing coordinator.
Ties together: camera capture → YOLO detection → tracking → density → heatmap → publish.
Runs headless (no cv2.imshow) for server / edge deployments.
"""
import os
import cv2
import time
import logging
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any

from app.config.config import settings
from app.camera.camera_source import ThreadedCameraSource
from app.detector.person_detector import PersonDetector
from app.tracker.person_tracker import LineCrossingTracker
from app.density.density_estimator import ZoneDensityEstimator
from app.heatmap.heatmap_generator import HeatmapGenerator
from app.utils.client_integration import BackendIntegrationClient

logger = logging.getLogger("cv-edge")

# Directory to persist snapshot frames for debugging / API consumption
OUTPUT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class StreamProcessor:
    def __init__(self):
        self.camera_id = settings.CAMERA_ID
        self.zone_id = settings.ZONE_ID

        # 1. Camera
        self.camera = ThreadedCameraSource(
            source=settings.CAMERA_SOURCE,
            width=settings.RESOLUTION_WIDTH,
            height=settings.RESOLUTION_HEIGHT,
        )

        # 2. Detector
        self.detector = PersonDetector(
            model_name=settings.YOLO_MODEL,
            conf_thresh=settings.CONFIDENCE_THRESHOLD,
            iou_thresh=settings.IOU_THRESHOLD,
            force_cpu=settings.FORCE_CPU,
        )

        # 3. Tracker
        self.tracker = LineCrossingTracker(
            line_y_ratio=0.55,
            frame_height=settings.RESOLUTION_HEIGHT,
        )

        # 4. Density estimator
        self.density_estimator = ZoneDensityEstimator(
            frame_width=settings.RESOLUTION_WIDTH,
            frame_height=settings.RESOLUTION_HEIGHT,
        )

        # 5. Heatmap renderer
        self.heatmap_generator = HeatmapGenerator(
            width=settings.RESOLUTION_WIDTH,
            height=settings.RESOLUTION_HEIGHT,
        )

        # 6. Backend integration
        self.client = BackendIntegrationClient(
            api_url=settings.BACKEND_API_URL,
            ws_url=settings.BACKEND_WS_URL,
            camera_id=self.camera_id,
            zone_id=self.zone_id,
        )

        # Performance book-keeping
        self.is_running = False
        self.fps = 0.0
        self.inference_times: list[float] = []
        self.frame_count = 0
        self.skipped_frames = 0

        # Entry/exit rate tracking (per-minute)
        self._last_entry_total = 0
        self._last_exit_total = 0
        self._rate_ts = time.time()
        self.entry_rate = 0
        self.exit_rate = 0

    # ──────────────────────────────────────────────
    # Lifecycle
    # ──────────────────────────────────────────────
    def start(self):
        self.is_running = True
        self.camera.start()
        self.client.start_ws_connection()
        self._run_loop()

    def stop(self):
        self.is_running = False
        self.camera.stop()
        self.client.close()
        logger.info("Stream processor stopped.")

    # ──────────────────────────────────────────────
    # Main loop
    # ──────────────────────────────────────────────
    def _run_loop(self):
        logger.info("═══════════════════════════════════════")
        logger.info("  Edge CV processing loop STARTED")
        logger.info("═══════════════════════════════════════")

        last_publish_time = time.time()
        frame_time = time.time()
        target_frame_time = 1.0 / settings.TARGET_FPS

        while self.is_running:
            loop_start = time.time()

            ret, frame = self.camera.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            self.frame_count += 1

            # Frame skipping when overloaded
            if self.frame_count % settings.FRAME_SKIP != 0:
                self.skipped_frames += 1
                time.sleep(0.002)
                continue

            # ── 1. Detection + Tracking ──
            t0 = time.time()
            track_result = self.detector.detect_and_track(frame)
            inf_ms = (time.time() - t0) * 1000
            self.inference_times.append(inf_ms)
            if len(self.inference_times) > 120:
                self.inference_times.pop(0)

            annotated_frame = frame.copy()
            boxes = []
            if track_result is not None and track_result.boxes is not None:
                boxes = track_result.boxes
                annotated_frame = track_result.plot()

            # ── 2. Counting ──
            headcount, total_entries, total_exits = self.tracker.update(boxes)

            # ── 3. Density ──
            density = self.density_estimator.estimate_density(boxes)

            # ── 4. Heatmap overlay ──
            blended = self.heatmap_generator.generate_overlay(annotated_frame, boxes)

            # ── 5. HUD ──
            self._draw_hud(blended, headcount, density)

            # Save latest frame for debugging
            cv2.imwrite(os.path.join(OUTPUT_DIR, "latest_frame.jpg"), blended)

            # ── 6. Publish every ~1 s ──
            now = time.time()
            if now - last_publish_time >= 1.0:
                # Compute entry/exit rates (per minute extrapolation)
                dt = now - self._rate_ts
                if dt > 0:
                    self.entry_rate = int(
                        (total_entries - self._last_entry_total) / dt * 60
                    )
                    self.exit_rate = int(
                        (total_exits - self._last_exit_total) / dt * 60
                    )
                self._last_entry_total = total_entries
                self._last_exit_total = total_exits
                self._rate_ts = now

                avg_inf = (
                    sum(self.inference_times) / len(self.inference_times)
                    if self.inference_times
                    else 0
                )

                telemetry = {
                    "camera_id": self.camera_id,
                    "people_count": headcount,
                    "crowd_density": density["crowd_density"],
                    "congestion_score": density["congestion_score"],
                    "risk_level": density["risk_level"],
                    "entry_rate": self.entry_rate,
                    "exit_rate": self.exit_rate,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

                logger.info(
                    f"[TELEMETRY] count={headcount}  density={density['crowd_density']:.1f}%  "
                    f"risk={density['risk_level']}  fps={self.fps:.1f}  "
                    f"inf={avg_inf:.1f}ms  entries/min={self.entry_rate}  "
                    f"exits/min={self.exit_rate}"
                )

                # REST
                self.client.send_snapshot(headcount)

                # WebSocket broadcasts
                self.client.broadcast_event("CrowdDensityUpdated", telemetry)
                self.client.broadcast_event(
                    "PredictionUpdated",
                    {
                        "congestion_score": density["congestion_score"],
                        "risk": density["risk_level"],
                    },
                )

                if density["risk_level"] in ("HIGH", "CRITICAL"):
                    self.client.broadcast_event(
                        "EmergencyAlert",
                        {
                            "type": "CrowdCongestion",
                            "camera": self.camera_id,
                            "risk": density["risk_level"],
                            "score": density["congestion_score"],
                        },
                    )

                last_publish_time = now
                self.skipped_frames = 0

            # FPS calculation
            duration = time.time() - frame_time
            self.fps = 1.0 / duration if duration > 0 else settings.TARGET_FPS
            frame_time = time.time()

            # Rate limiter
            elapsed = time.time() - loop_start
            time.sleep(max(0.001, target_frame_time - elapsed))

    # ──────────────────────────────────────────────
    # HUD overlay
    # ──────────────────────────────────────────────
    def _draw_hud(
        self, frame: np.ndarray, count: int, density: Dict[str, Any]
    ):
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Dark panel background
        cv2.rectangle(frame, (8, 8), (230, 120), (24, 15, 37), -1)
        cv2.rectangle(frame, (8, 8), (230, 120), (74, 50, 103), 1)

        cv2.putText(
            frame, f"CAM: {self.camera_id}", (16, 28), font, 0.42,
            (255, 255, 255), 1, cv2.LINE_AA,
        )
        cv2.putText(
            frame, f"FPS: {self.fps:.1f}", (16, 46), font, 0.38,
            (198, 186, 222), 1, cv2.LINE_AA,
        )
        cv2.putText(
            frame, f"HEADCOUNT: {count}", (16, 64), font, 0.42,
            (255, 255, 255), 1, cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            f"DENSITY: {density['crowd_density']:.1f}%",
            (16, 82), font, 0.38, (247, 185, 196), 1, cv2.LINE_AA,
        )

        risk = density["risk_level"]
        risk_color = {
            "LOW": (34, 197, 94),
            "MEDIUM": (59, 180, 250),
            "HIGH": (15, 158, 245),
            "CRITICAL": (80, 80, 239),
        }.get(risk, (200, 200, 200))

        cv2.putText(
            frame, f"RISK: {risk}", (16, 100), font, 0.40,
            risk_color, 1, cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            f"SCORE: {density['congestion_score']:.0f}",
            (16, 115), font, 0.35, (198, 186, 222), 1, cv2.LINE_AA,
        )

        # Counting line
        y_line = self.tracker.counting_line_y
        cv2.line(
            frame, (0, y_line), (self.camera.width, y_line),
            (198, 186, 222), 1, cv2.LINE_AA,
        )
        cv2.putText(
            frame, "CROSSING LINE", (8, y_line - 5), font, 0.30,
            (198, 186, 222), 1, cv2.LINE_AA,
        )
