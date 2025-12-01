# services/chat/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY services/chat/requirements.txt .
# Use BuildKit cache mount for pip - speeds up rebuilds significantly
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy common utilities
COPY common /app/common

# Copy service code
COPY services/chat/chat_service.py ./
COPY services/chat/openrouter_client.py ./
COPY services/chat/retrieval_client.py ./
COPY services/chat/prompt_templates.py ./
COPY services/chat/config.py ./

EXPOSE 8003
CMD ["uvicorn", "chat_service:app", "--host", "0.0.0.0", "--port", "8003"]
