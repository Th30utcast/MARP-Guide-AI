FROM python:3.11-slim

WORKDIR /app

#! Install the dependencies needed for the Ingestion Service to run.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY scraper.py .
COPY fetcher.py .
COPY event_broker.py .

#! Create a directory for the PDFs to be downloaded and stored (not needed for full aplplication)
RUN mkdir -p /app/pdfs

# Expose port
EXPOSE 8000

#!Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
