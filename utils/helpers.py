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
from typing import Optional

import streamlit as st


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


# ============================================
# Presentation-Layer Helpers
# ============================================

def estimate_reading_time(text: str) -> int:
    """
    Returns estimated reading time in minutes.
    Uses average reading speed of 200 words per minute.
    """
    if not text:
        return 1
    word_count = len(text.split())
    return max(1, round(word_count / 200))


def format_date_magazine(date_str: str) -> str:
    """
    Formats a date string into magazine style: 'July 24, 2026'.
    Falls back to the original string if parsing fails.
    """
    if not date_str:
        return datetime.now().strftime("%B %d, %Y")
    try:
        from dateutil import parser as dateutil_parser
        dt = dateutil_parser.parse(date_str)
        return dt.strftime("%B %d, %Y")
    except Exception:
        return date_str[:20] if len(date_str) > 20 else date_str


def get_ui_mode() -> str:
    """
    Returns the current UI mode: 'magazine' or 'debug'.
    Default is 'magazine' for reader-friendly display.
    """
    return st.session_state.get("ui_mode", "magazine")


def is_magazine_mode() -> bool:
    """Shorthand check for magazine mode."""
    return get_ui_mode() == "magazine"


def is_debug_mode() -> bool:
    """Shorthand check for debug mode."""
    return get_ui_mode() == "debug"


def estimate_article_reading_time(article) -> int:
    """
    Estimates total reading time for a MagazineArticle object.
    Sums all content sections.
    """
    total = ""
    for field in [
        "executive_summary", "background", "technical_analysis",
        "impact", "recommendations", "references",
    ]:
        val = getattr(article, field, "") or ""
        total += val + " "
    return estimate_reading_time(total)

