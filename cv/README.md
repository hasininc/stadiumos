# Computer Vision (CV) Processing Core

This directory contains the edge-based video analytics code for StadiumOS:

## Directory Index
- `cv-service/`: A Python-based video analytics service running YOLOv11 and OpenCV keypoint estimators.

## Core Guidelines
- Blur faces and license plates at the edge before uploading metadata to GCS.
- Process video streams locally to minimize network bandwidth usage.
- Optimize pipelines to achieve less than 100ms latency for detection events.
