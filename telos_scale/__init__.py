"""
Telos-Scale: Autonomous AI agent platform for massive parallel experimentation.
"""

from .core import TelosScale
from .sandbox import DockerSandbox
from .memory import LocalMemory
from .llm import LLMClient
from .shared import SharedClient

__version__ = "0.1.0"
__all__ = ["TelosScale", "DockerSandbox", "LocalMemory", "LLMClient", "SharedClient"]