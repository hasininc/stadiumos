FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ai/ai-orchestrator/requirements.txt ./ai/ai-orchestrator/
RUN pip install --no-cache-dir -r ai/ai-orchestrator/requirements.txt

COPY ai/ai-orchestrator/ ./ai/ai-orchestrator/
COPY shared/ ./shared/

WORKDIR /workspace/ai/ai-orchestrator

CMD ["python", "src/main.py"]
