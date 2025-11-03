FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/ingestion/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common utilities (shared RabbitMQ broker and events)
COPY common /app/common

# Copy application code (only service and worker)
COPY services/ingestion/ingestion_service.py .
COPY services/ingestion/worker.py .

# Create directories for PDFs and storage
RUN mkdir -p /app/pdfs /app/storage/extracted

# Expose port for health checks
EXPOSE 8000

# Run the worker
CMD ["python", "worker.py"]
