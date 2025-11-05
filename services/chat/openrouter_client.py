"""
OPENROUTER CLIENT

Wrapper for calling LLM models via OpenRouter API. Uses the OpenAI SDK.

Send prompts to AI models and get back generated answers for RAG.
"""

import logging
import httpx
from openai import OpenAI
from typing import Optional
import config

logger = logging.getLogger(__name__)


class OpenRouterClient:

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None
    ):
        # Load configuration from config.py or use provided values
        self.api_key = api_key or config.OPENROUTER_API_KEY
        self.model = model or config.OPENROUTER_MODEL
        self.temperature = temperature if temperature is not None else config.TEMPERATURE
        self.max_tokens = max_tokens or config.MAX_TOKENS

        # Validate API key exists
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable.")

        # Headers required for OpenRouter free models
        self.headers = {
            "HTTP-Referer": "https://github.com/Th30utcast/MARP-Guide-AI",
            "X-Title": "MARP Guide AI"
        }

        # Create HTTP client with headers and timeout
        http_client = httpx.Client(
            headers=self.headers,
            timeout=60.0
        )

        # Initialize OpenAI SDK pointing to OpenRouter's URL
        self.client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,  # "https://openrouter.ai/api/v1"
            api_key=self.api_key,
            http_client=http_client
        )

        logger.info(f"✅ OpenRouter client initialized | Model: {self.model}")


    def generate_answer(self, prompt: str) -> str:    
  # Send prompt to LLM and get generated answer back
       
        try:
            logger.info(f"🤖 Calling OpenRouter API | Model: {self.model}")

            # Call LLM via OpenAI SDK (routes to OpenRouter)
            response = self.client.chat.completions.create(
                model=self.model,              
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,  # Controls randomness (0.0-1.0)
                max_tokens=self.max_tokens     
            )

            # Extract answer text from response
            answer = response.choices[0].message.content.strip()
            logger.info(f"✅ Generated answer | Length: {len(answer)} chars")

            return answer

        except Exception as e:
            logger.error(f"❌ OpenRouter API call failed: {e}")
            raise Exception(f"Failed to generate answer: {str(e)}")
