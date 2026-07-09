"""
Synthetic crowd video generator for development and demo environments.
Generates realistic moving-person rectangles on a stadium-themed background
so the YOLO detector has actual frames to process when no physical camera is available.
"""
import cv2
import numpy as np
import random

from typing import List, Tuple


class SyntheticPerson:
    def __init__(self, frame_w: int, frame_h: int):
        self.x = random.randint(40, frame_w - 40)
        self.y = random.randint(40, frame_h - 40)
        self.w = random.randint(20, 35)
        self.h = random.randint(50, 80)
        self.vx = random.uniform(-2.0, 2.0)
        self.vy = random.uniform(-1.5, 1.5)
        self.frame_w = frame_w
        self.frame_h = frame_h
        # Skin/clothing color variation
        self.color = (
            random.randint(100, 230),
            random.randint(80, 200),
            random.randint(60, 180),
        )
        self.head_color = (
            random.randint(160, 240),
            random.randint(140, 220),
            random.randint(120, 200),
        )

    def step(self):
        self.x += self.vx
        self.y += self.vy
        # Bounce off edges
        if self.x < 10 or self.x > self.frame_w - 40:
            self.vx *= -1
        if self.y < 10 or self.y > self.frame_h - 40:
            self.vy *= -1
        # Add slight random drift
        self.vx += random.uniform(-0.3, 0.3)
        self.vy += random.uniform(-0.2, 0.2)
        self.vx = max(-3.0, min(3.0, self.vx))
        self.vy = max(-2.5, min(2.5, self.vy))

    def draw(self, frame: np.ndarray):
        x, y, w, h = int(self.x), int(self.y), self.w, self.h
        # Body rectangle
        cv2.rectangle(frame, (x, y + h // 5), (x + w, y + h), self.color, -1)
        # Head circle
        head_r = w // 3
        cv2.circle(frame, (x + w // 2, y + head_r), head_r, self.head_color, -1)


class SyntheticCrowdGenerator:
    """
    Generates synthetic video frames with moving person-like shapes.
    Acts as a drop-in cv2.VideoCapture replacement for demo mode.
    """

    def __init__(self, width: int = 640, height: int = 480, num_people: int = 25):
        self.width = width
        self.height = height
        self.people: List[SyntheticPerson] = [
            SyntheticPerson(width, height) for _ in range(num_people)
        ]
        self.frame_count = 0
        self.is_opened = True

    def isOpened(self) -> bool:
        return self.is_opened

    def read(self) -> Tuple[bool, np.ndarray]:
        if not self.is_opened:
            return False, None

        # Create stadium-green background
        frame = np.full((self.height, self.width, 3), (42, 52, 38), dtype=np.uint8)

        # Draw subtle ground lines
        for i in range(0, self.width, 80):
            cv2.line(frame, (i, 0), (i, self.height), (48, 58, 44), 1)
        for j in range(0, self.height, 60):
            cv2.line(frame, (0, j), (self.width, j), (48, 58, 44), 1)

        # Step and draw all persons
        for person in self.people:
            person.step()
            person.draw(frame)

        # Occasionally add / remove people to simulate flow
        self.frame_count += 1
        if self.frame_count % 90 == 0 and len(self.people) < 40:
            self.people.append(SyntheticPerson(self.width, self.height))
        if self.frame_count % 120 == 0 and len(self.people) > 10:
            self.people.pop(random.randint(0, len(self.people) - 1))

        # Add slight Gaussian noise for realism
        noise = np.random.normal(0, 3, frame.shape).astype(np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        return True, frame

    def set(self, prop_id: int, value: float):
        pass  # No-op for compatibility

    def release(self):
        self.is_opened = False
