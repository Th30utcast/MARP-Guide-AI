"""
OpenRouter Client Module
Handles LLM API calls for answer generation 
"""
import logging
from openai import OpenAI
from typing import Optional
import config

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """
    Client for OpenRouter API using OpenAI SDK
    Handles LLM calls for answer generation
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None
    ):
        """
        Initialize OpenRouter client

        Args:
            api_key: OpenRouter API key (defaults to config)
            model: Model to use (defaults to config)
            temperature: Sampling temperature (defaults to config)
            max_tokens: Maximum tokens in response (defaults to config)
        """
        self.api_key = api_key or config.OPENROUTER_API_KEY
        self.model = model or config.OPENROUTER_MODEL
        self.temperature = temperature if temperature is not None else config.TEMPERATURE
        self.max_tokens = max_tokens or config.MAX_TOKENS

        if not self.api_key:
            raise ValueError("OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable.")

        # Initialize OpenAI client with OpenRouter base URL
        self.client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=self.api_key
        )

        logger.info(f"✅ OpenRouter client initialized | Model: {self.model}")

    def generate_answer(self, prompt: str) -> str:
        """
        Generate answer using OpenRouter API

        Args:
            prompt: The complete RAG prompt (system + context + query)

        Returns:
            Generated answer as string

        Raises:
            Exception: If API call fails
        """
        try:
            logger.info(f"🤖 Calling OpenRouter API | Model: {self.model}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            answer = response.choices[0].message.content.strip()
            logger.info(f"✅ Generated answer | Length: {len(answer)} chars")

            return answer

        except Exception as e:
            logger.error(f"❌ OpenRouter API call failed: {e}")
            raise Exception(f"Failed to generate answer: {str(e)}")
