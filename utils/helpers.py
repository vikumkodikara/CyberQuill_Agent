"""
CyberQuill Helper Utilities
==============================

Purpose:
    Shared utility functions used across multiple modules.
    Keeps agent code clean by extracting common operations.

Inputs:
    Varies by function.

Outputs:
    Varies by function.

Dependencies:
    - Python standard library

Testing strategy:
    - Unit test each function with edge cases

Possible improvements:
    - Add text cleaning utilities
    - Add retry decorators for API calls
"""

import json
from datetime import datetime
from pathlib import Path


def save_json(data: list[dict] | dict, filepath: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: The data to save (list of dicts or a single dict)
        filepath: Path to the output file
    
    Why this helper?
        Multiple agents need to save JSON output. This avoids
        repeating the same file-writing boilerplate in every agent.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def load_json(filepath: str) -> list[dict] | dict:
    """
    Load data from a JSON file.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        The parsed JSON data
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file isn't valid JSON
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_timestamp() -> str:
    """
    Returns the current timestamp as a formatted string.
    
    Used for:
        - Logging when articles were collected
        - Naming PDF output files
        - Tracking pipeline execution time
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
