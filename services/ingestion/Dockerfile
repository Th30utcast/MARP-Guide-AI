FROM python:3.11-slim

WORKDIR /app

#! Install the dependencies needed for the Ingestion Service to run.
COPY services/ingestion/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common utilities (shared RabbitMQ broker)
COPY common /app/common

# Copy application code
COPY services/ingestion/main.py .
COPY services/ingestion/scraper.py .
COPY services/ingestion/fetcher.py .

#! Create a directory for the PDFs to be downloaded and stored (not needed for full aplplication)
RUN mkdir -p /app/pdfs

# Expose port
EXPOSE 8000

#!Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
