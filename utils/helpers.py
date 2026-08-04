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

from datetime import datetime


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
