import os
import cv2
import time
import threading
import logging
from typing import Union, Optional

from app.camera.synthetic_feed import SyntheticCrowdGenerator

logger = logging.getLogger("cv-edge")

# Suppress macOS camera authorization popup in background threads
os.environ["OPENCV_AVFOUNDATION_SKIP_AUTH"] = "1"


class ThreadedCameraSource:
    """
    Threaded video capture with automatic fallback to synthetic feed.
    Supports: USB webcam (int), RTSP stream (str), local MP4 (str), synthetic demo.
    """

    def __init__(self, source: str, width: int = 640, height: int = 480):
        if source.isdigit():
            self.source: Union[int, str] = int(source)
        else:
            self.source = source

        self.width = width
        self.height = height

        self.cap = None
        self.ret = False
        self.frame = None
        self.is_running = False
        self.lock = threading.Lock()
        self.thread = None
        self.using_synthetic = False

        # Metrics
        self.dropped_frames = 0
        self.total_frames = 0

    def start(self):
        if self.is_running:
            return self

        logger.info(f"Opening video feed from source: {self.source} ...")
        self.cap = cv2.VideoCapture(self.source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        self.ret, self.frame = self.cap.read()
        if not self.ret:
            logger.warning(
                "Physical camera unavailable — switching to SYNTHETIC demo feed."
            )
            self.cap.release()
            self.cap = SyntheticCrowdGenerator(self.width, self.height, num_people=25)
            self.using_synthetic = True
            self.ret, self.frame = self.cap.read()

        mode = "SYNTHETIC" if self.using_synthetic else "LIVE"
        logger.info(f"Camera source initialised in {mode} mode.")

        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        return self

    def _capture_loop(self):
        while self.is_running:
            if self.cap is None or (
                not self.using_synthetic and not self.cap.isOpened()
            ):
                logger.warning("Camera source disconnected. Attempting recovery…")
                time.sleep(2.0)
                self.cap = cv2.VideoCapture(self.source)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                if not self.cap.isOpened():
                    logger.warning("Recovery failed — falling back to synthetic feed.")
                    self.cap = SyntheticCrowdGenerator(
                        self.width, self.height, num_people=25
                    )
                    self.using_synthetic = True
                continue

            ret, frame = self.cap.read()
            if not ret:
                self.dropped_frames += 1
                time.sleep(0.01)
                continue

            with self.lock:
                self.ret = ret
                self.frame = frame
                self.total_frames += 1

            time.sleep(0.005)

    def read(self) -> tuple[bool, Optional[cv2.typing.MatLike]]:
        with self.lock:
            if self.frame is None:
                return False, None
            return self.ret, self.frame.copy()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cap:
            if hasattr(self.cap, "release"):
                self.cap.release()
            self.cap = None
        logger.info("Threaded camera capture stopped.")
