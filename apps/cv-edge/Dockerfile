FROM python:3.10-slim

WORKDIR /workspace

# Install system dependencies needed for compiling image libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY apps/cv-edge/requirements.txt ./apps/cv-edge/
RUN pip install --no-cache-dir -r apps/cv-edge/requirements.txt

# Copy application files and shared packages
COPY apps/cv-edge/ ./apps/cv-edge/
COPY libs/ ./libs/

WORKDIR /workspace/apps/cv-edge

CMD ["python", "app/main_edge.py"]
