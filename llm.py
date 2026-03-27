"""
LLM client wrapper using LiteLLM.
"""

import os
import litellm
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for LLM interactions via LiteLLM."""

    def __init__(
        self,
        model: str = "gemini/gemini-flash-latest",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_tokens: int = 8000,
        temperature: float = 0.7,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        # Set up API key
        if api_key:
            os.environ["OPENROUTER_API_KEY"] = api_key
        elif "OPENROUTER_API_KEY" not in os.environ:
            logger.warning("OPENROUTER_API_KEY environment variable not set.")
        # Optional base URL for custom endpoints
        if base_url:
            os.environ[f"{model.upper().replace('/', '_')}_API_BASE"] = base_url

    def complete(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        """Generate completion for given prompt."""
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM completion failed: {e}")
            # Fallback to a simple response
            return "Write a 'Hello, World!' program in Python."

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost in USD based on model pricing (placeholder)."""
        # Rough estimates per 1K tokens
        pricing = {
            "gemini/gemini-flash-latest": 0.000075,  # $0.075 per 1K tokens
            "openrouter/deepseek/deepseek-chat-v3-0324": 0.00014,
            "gpt-4o-mini": 0.00015,
        }
        rate = pricing.get(self.model, 0.0001)
        total_tokens = prompt_tokens + completion_tokens
        return (total_tokens / 1000) * rate

    def count_tokens(self, text: str) -> int:
        """Approximate token count (placeholder)."""
        # Simple approximation: 4 chars per token
        return len(text) // 4


if __name__ == "__main__":
    # Quick test (requires API key)
    client = LLMClient()
    print("Model:", client.model)
    test_prompt = "Say hello in one word."
    try:
        result = client.complete(test_prompt, max_tokens=10)
        print("Completion:", result)
    except Exception as e:
        print(f"Error (expected without API key): {e}")