"""
Shared client for uploading and searching trials (optional).
"""

import requests
import json
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class SharedClient:
    """Client for the shared server (optional)."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def upload(self, goal: str, result: str, metadata: Optional[Dict] = None):
        """Upload a trial to the shared server."""
        payload = {
            "goal": goal,
            "result": result,
            "metadata": metadata or {},
        }
        try:
            response = self.session.post(
                f"{self.base_url}/api/upload",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            logger.info(f"Upload successful: {response.json().get('id')}")
        except Exception as e:
            logger.warning(f"Upload failed: {e}")

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar trials."""
        params = {"q": query, "limit": limit}
        try:
            response = self.session.get(
                f"{self.base_url}/api/search",
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            return []

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (placeholder)."""
        # For v0.1, return dummy embedding
        return [0.0] * 384


if __name__ == "__main__":
    # Test with a mock server (not run)
    pass