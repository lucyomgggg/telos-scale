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
        
        # Determine necessary environment variable based on model provider
        provider = model.split("/")[0].lower() if "/" in model else "openai"
        key_var = f"{provider.upper()}_API_KEY"
        
        # If specific provider key is missing, check for OPENROUTER_API_KEY as a generic proxy
        if api_key:
            os.environ[key_var] = api_key
        elif key_var not in os.environ:
            if "OPENROUTER_API_KEY" in os.environ:
                logger.info(f"Using OPENROUTER_API_KEY as fallback for provider '{provider}'")
            else:
                logger.warning(f"Required API key '{key_var}' not found in environment.")

        # Optional base URL for custom endpoints
        if base_url:
            base_var = f"{model.upper().replace('/', '_')}_API_BASE"
            os.environ[base_var] = base_url

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
            logger.error(f"LLM completion failed for model {self.model}: {e}")
            # Do NOT fallback to dummy strings. Let the caller handle the error.
            raise

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost in USD based on model pricing."""
        # Pricing per 1M tokens as of late 2024 / early 2025
        pricing_data = {
            "gemini/gemini-flash-latest": {"prompt": 0.075, "completion": 0.30},
            "deepseek/deepseek-chat": {"prompt": 0.14, "completion": 0.28},
            "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
        }
        
        # Use simple pricing if specific data isn't available
        model_pricing = pricing_data.get(self.model, {"prompt": 0.1, "completion": 0.2})
        cost = (prompt_tokens / 1_000_000 * model_pricing["prompt"]) + \
               (completion_tokens / 1_000_000 * model_pricing["completion"])
        return cost

    def count_tokens(self, text: str) -> int:
        """Approximate token count."""
        try:
            return litellm.token_counter(model=self.model, text=text)
        except:
            # Fallback if litellm counter fails
            return len(text) // 4


if __name__ == "__main__":
    # Quick test
    client = LLMClient()
    print("Model:", client.model)
    test_prompt = "Say hello in one word."
    try:
        result = client.complete(test_prompt, max_tokens=10)
        print("Completion:", result)
    except Exception as e:
        print(f"Connection test failed (this is expected if no API key is set): {e}")