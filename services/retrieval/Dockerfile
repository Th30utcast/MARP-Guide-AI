#This Dockerfile builds a container image for the Retrieval Service, a microservice in the MARP Guide AI system.
#This Dockerfile transforms the Retrieval Service into a portable, containerized service that integrates with the rest of the microservices architecture.

# File Path: services/retrieval/Dockerfile

# Base image: official Python 3.11 slim variant (smaller, minimal dependencies)
FROM python:3.11-slim

# Sets environment variables 
# prevents Python from writing bytecode and buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Sets the working directory for the container to /app
WORKDIR /app

# System deps for sentence-transformers (small footprint)
# installs git for cloning the sentence-transformers repository
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# copies the requirements.txt file from the services/retrieval directory into the container at /app
COPY services/retrieval/requirements.txt .
# Use BuildKit cache mount for pip - speeds up rebuilds significantly
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy common utilities
# copies the common directory from the root of the project into the container at /app/common
COPY common /app/common

# Copy service code
# copies the retrieval_service.py and retrieval_utils.py files from the services/retrieval directory into the container at /app
COPY services/retrieval/retrieval_service.py ./
COPY services/retrieval/retrieval_utils.py ./

# Exposes port 8002 for the retrieval service
EXPOSE 8002

# Starts the retrieval service using uvicorn
# uvicorn is a lightning-fast ASGI server for Python
# --host 0.0.0.0 makes the server accessible from all network interfaces
# --port 8002 specifies the port to listen on
# retrieval_service:app is the module and app name to run
# the retrieval service will run on port 8002
CMD ["uvicorn", "retrieval_service:app", "--host", "0.0.0.0", "--port", "8002"]
