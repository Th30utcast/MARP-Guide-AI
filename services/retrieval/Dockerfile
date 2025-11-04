# services/retrieval/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for sentence-transformers (small footprint)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/retrieval/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common utilities
COPY common /app/common

# Copy service code
COPY services/retrieval/retrieval_service.py ./
COPY services/retrieval/retrieval_utils.py ./

EXPOSE 8002
CMD ["uvicorn", "retrieval_service:app", "--host", "0.0.0.0", "--port", "8002"]
