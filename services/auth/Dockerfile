FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY services/auth/requirements.txt .
# Use BuildKit cache mount for pip - speeds up rebuilds significantly
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy service code
COPY services/auth/auth_service.py ./

EXPOSE 8004
CMD ["uvicorn", "auth_service:app", "--host", "0.0.0.0", "--port", "8004"]
