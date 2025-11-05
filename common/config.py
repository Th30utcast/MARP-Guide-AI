import os
from pathlib import Path
from typing import Optional

from .mq import RabbitMQEventBroker


# ============================================================================
# RabbitMQ Configuration
# ============================================================================

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")


def get_rabbitmq_broker() -> RabbitMQEventBroker:
    # Create and return a configured RabbitMQ event broker instance.
    return RabbitMQEventBroker(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        username=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD
    )


# ============================================================================
# Storage Configuration
# ============================================================================

STORAGE_PATH = os.getenv("STORAGE_PATH", "/app/storage/extracted")
PDF_OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", "/app/pdfs")


def get_storage_path(create: bool = True) -> Path:
    path = Path(STORAGE_PATH)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def get_pdf_output_dir(create: bool = True) -> Path:
    path = Path(PDF_OUTPUT_DIR)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


# ============================================================================
# Qdrant Configuration
# ============================================================================

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_URL = os.getenv("QDRANT_URL", f"http://{QDRANT_HOST}:{QDRANT_PORT}")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "marp-documents")


# ============================================================================
# Model Configuration
# ============================================================================

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


# ============================================================================
# Ingestion Configuration
# ============================================================================

MARP_URL = os.getenv("MARP_URL", "https://www.gov.uk/government/collections/medicines-and-healthcare-products-regulatory-agency-risk-assessments")
