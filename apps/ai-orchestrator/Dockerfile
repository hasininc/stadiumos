FROM python:3.10-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY apps/ai-orchestrator/requirements.txt ./apps/ai-orchestrator/
RUN pip install --no-cache-dir -r apps/ai-orchestrator/requirements.txt

# Copy application files and shared modules
COPY apps/ai-orchestrator/ ./apps/ai-orchestrator/
COPY libs/ ./libs/

WORKDIR /workspace/apps/ai-orchestrator

CMD ["python", "src/main.py"]
