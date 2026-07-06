FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY ml/ml-service/requirements.txt ./ml/ml-service/
RUN pip install --no-cache-dir -r ml/ml-service/requirements.txt

COPY ml/ml-service/ ./ml/ml-service/
COPY shared/ ./shared/

WORKDIR /workspace/ml/ml-service

EXPOSE 8081

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8081"]
