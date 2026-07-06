FROM python:3.10-slim

WORKDIR /workspace

# Install system dependencies needed for compiling postgres modules
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY apps/backend-fastapi/requirements.txt ./apps/backend-fastapi/
RUN pip install --no-cache-dir -r apps/backend-fastapi/requirements.txt

# Copy application files and shared packages
COPY apps/backend-fastapi/ ./apps/backend-fastapi/
COPY libs/ ./libs/

WORKDIR /workspace/apps/backend-fastapi

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
