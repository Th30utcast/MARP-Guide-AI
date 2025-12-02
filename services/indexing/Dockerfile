FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/indexing/requirements.txt .
# Use BuildKit cache mount for pip - speeds up rebuilds significantly
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy common utilities
COPY common /app/common

# Copy service code
COPY services/indexing/indexing_service.py ./
COPY services/indexing/worker.py ./

# Create storage directory
RUN mkdir -p /app/storage/extracted

CMD ["python", "worker.py"]
