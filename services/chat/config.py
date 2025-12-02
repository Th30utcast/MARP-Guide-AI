"""
Configuration module for Chat Service
Loads environment variables and provides configuration constants
"""

import os

# Retrieval Service Configuration
RETRIEVAL_URL = os.getenv("RETRIEVAL_URL", "http://retrieval:8002")

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-3n-e2b-it:free")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

# RAG Configuration
DEFAULT_TOP_K = 5
MAX_CONTEXT_TOKENS = 2000
TEMPERATURE = 0.4 
MAX_TOKENS = 500
