FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/extraction/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common utilities
COPY common /app/common

# Copy service code
COPY services/extraction/extraction_service.py ./
COPY services/extraction/worker.py ./

# Create storage directory
RUN mkdir -p /app/storage/extracted

CMD ["python", "worker.py"]