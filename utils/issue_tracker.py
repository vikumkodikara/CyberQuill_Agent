"""
CyberQuill Issue Tracker
==========================

Purpose:
    Maintains a simple JSON-based counter for magazine issue numbers
    and keeps a history of all generated issues.

Storage:
    data/issue_history.json
"""

import json
from datetime import datetime
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)

_HISTORY_FILE = Path("data/issue_history.json")


def _load_history() -> dict:
    """Loads issue history from disk or returns a fresh structure."""
    if _HISTORY_FILE.exists():
        try:
            return json.loads(_HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Failed to load issue history: {e}")
    return {"next_issue": 1, "issues": []}


def _save_history(data: dict) -> None:
    """Persists issue history to disk."""
    _HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _HISTORY_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_current_issue_number() -> int:
    """Returns the next issue number without incrementing."""
    return _load_history()["next_issue"]


def get_next_issue_number() -> int:
    """Returns the next issue number and increments the counter."""
    data = _load_history()
    issue_num = data["next_issue"]
    data["next_issue"] = issue_num + 1
    _save_history(data)
    return issue_num


def record_issue(
    issue_number: int,
    article_count: int,
    pdf_path: str = "",
    categories: dict[str, int] | None = None,
) -> None:
    """Records a generated issue in the history."""
    data = _load_history()
    data["issues"].append({
        "issue_number": issue_number,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date_display": datetime.now().strftime("%B %Y"),
        "article_count": article_count,
        "pdf_path": pdf_path,
        "categories": categories or {},
    })
    _save_history(data)
    logger.info(f"Recorded issue #{issue_number} with {article_count} articles")


def get_issue_history() -> list[dict]:
    """Returns all past issues, newest first."""
    data = _load_history()
    return list(reversed(data.get("issues", [])))
