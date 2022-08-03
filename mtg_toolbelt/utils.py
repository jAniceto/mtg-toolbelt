"""
General utilities
"""

import json
from pathlib import Path


def load_config():
    """Load configuration file."""
    with open('config.json', 'r') as f:
        config = json.load(f)
        return config


def setup_dir(dir_name):
    """Create directory if it doesn't exist."""
    dir_path = Path(dir_name)
    dir_path.mkdir(parents=True, exist_ok=True)
