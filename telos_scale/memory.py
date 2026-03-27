"""
Local memory for storing past trials.
"""

import time
from typing import List, Dict, Optional


class LocalMemory:
    """Simple local memory storing recent trials."""

    def __init__(self, max_size: int = 1000):
        self.memory: List[Dict] = []  # each dict contains goal, result, timestamp
        self.max_size = max_size

    def add(self, goal: str, result: str, metadata: Optional[Dict] = None):
        """Add a trial to memory."""
        entry = {
            "goal": goal,
            "result": result,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }
        self.memory.append(entry)
        if len(self.memory) > self.max_size:
            self.memory.pop(0)  # FIFO removal

    def get_recent(self, n: int) -> List[Dict]:
        """Get the n most recent trials."""
        if n <= 0:
            return []
        return self.memory[-n:] if self.memory else []

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Simple keyword search over goals and results (placeholder)."""
        # For v0.1, just return recent entries.
        # In future, implement embedding-based search.
        return self.get_recent(limit)

    def clear(self):
        """Clear all memory."""
        self.memory.clear()

    def size(self) -> int:
        return len(self.memory)


if __name__ == "__main__":
    # Quick test
    mem = LocalMemory(max_size=3)
    mem.add("Write hello world", "Success", {"model": "test"})
    mem.add("Write factorial", "Success", {})
    mem.add("Write web scraper", "Failure", {})
    print("Recent 2:", mem.get_recent(2))
    mem.add("Another", "Success", {})
    print("After overflow:", mem.size())
    print("Recent 5:", mem.get_recent(5))