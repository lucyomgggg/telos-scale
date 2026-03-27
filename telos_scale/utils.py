"""
Utility functions for Telos-Scale.
"""

import os
import json
import logging
from typing import Any, Dict


def load_json_file(path: str) -> Dict[str, Any]:
    """Load JSON file."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"Failed to load JSON {path}: {e}")
        return {}


def save_json_file(data: Dict[str, Any], path: str):
    """Save data as JSON."""
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save JSON {path}: {e}")


def get_env_var(key: str, default: str = "") -> str:
    """Get environment variable with default."""
    return os.environ.get(key, default)