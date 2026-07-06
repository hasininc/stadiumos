FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY cv/cv-service/requirements.txt ./cv/cv-service/
RUN pip install --no-cache-dir -r cv/cv-service/requirements.txt

COPY cv/cv-service/ ./cv/cv-service/
COPY shared/ ./shared/

WORKDIR /workspace/cv/cv-service

CMD ["python", "src/main.py"]
