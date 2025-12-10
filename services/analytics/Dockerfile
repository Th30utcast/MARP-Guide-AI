FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY services/analytics/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common module
COPY common /app/common

# Copy analytics service
COPY services/analytics/analytics_service.py .

# Run the service
CMD ["uvicorn", "analytics_service:app", "--host", "0.0.0.0", "--port", "8005"]
