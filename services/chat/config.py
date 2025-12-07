"""
Configuration module for Chat Service
Loads environment variables and provides configuration constants
"""

import os

# Retrieval Service Configuration
RETRIEVAL_URL = os.getenv("RETRIEVAL_URL", "http://retrieval:8002")

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

# RAG Configuration
DEFAULT_TOP_K = 10
MAX_CONTEXT_TOKENS = 3500  # More context for comprehensive answers
TEMPERATURE = 0.4  # Balanced for focused answers
MAX_TOKENS = 1200  # Increased to prevent cutoff and repetition

# Query Reformulation Configuration
ENABLE_QUERY_REFORMULATION = os.getenv("ENABLE_QUERY_REFORMULATION", "true").lower() == "true"
# Set to False to disable query reformulation (e.g., for testing or debugging)

# Multi-Model Comparison Configuration (Tier 2-D)
ENABLE_MULTI_MODEL_COMPARISON = os.getenv("ENABLE_MULTI_MODEL_COMPARISON", "false").lower() == "true"

COMPARISON_MODELS = [
    {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini",
        "description": "Fast and efficient for general questions",
    },
    {
        "id": "google/gemma-3n-e2b-it:free",
        "name": "Google Gemma 3n 2B",
        "description": "Lightweight and fast Google model",
    },
    {
        "id": "deepseek/deepseek-chat",
        "name": "DeepSeek Chat",
        "description": "Dialogue-optimized for conversational QA",
    },
]
