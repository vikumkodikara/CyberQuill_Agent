"""
CyberQuill Duplicate Detection Agent

Purpose:
    Removes duplicate articles from the collected news feed.
    When 6 different RSS feeds report the same cybersecurity incident,
    we don't want 6 copies of the same story in our magazine.

How duplicates happen:
    - Same story, same URL: Bleeping Computer links to the same article
      that appears in both their main feed and category feed.
    - Same story, different URL: The Hacker News and SecurityWeek both
      cover the same zero-day vulnerability with different URLs.
    - Same story, different headline: "Critical Chrome Flaw Patched" vs
      "Google Fixes Zero-Day in Chrome Browser" — same story, different words.

Detection strategy (3 layers):
    Layer 1: Exact URL match
        - Cheapest check (string comparison)
        - Catches exact duplicates from the same source
    
    Layer 2: Normalized URL match
        - Strips query parameters and trailing slashes
        - Catches URLs that differ only in tracking parameters
        Example: "https://example.com/article?utm_source=rss"
             and "https://example.com/article" → same article
    
    Layer 3: Title similarity (fuzzy matching)
        - Uses SequenceMatcher to compare titles
        - Catches "same story, different headline" duplicates
        - Threshold: 0.85 (85% similar = considered duplicate)

    Why not use embeddings for similarity?
        Embeddings (sentence-transformers) would be more accurate,
        but they're expensive to compute and we already use them
        in the RAG Agent. For deduplication, SequenceMatcher is
        fast, free, and good enough.

Inputs:
    - List[Article] — articles from the Collector Agent

Outputs:
    - List[Article] — deduplicated articles

Dependencies:
    - difflib (Python standard library) — for SequenceMatcher
    - urllib.parse (Python standard library) — for URL normalization
    - models.schemas.Article — data model
    - utils.logger — logging

Agentic AI Design Pattern:
    **Orchestrator-Worker Pattern** — This agent is a "worker" that
    receives a specific task (deduplication) from the orchestrator.
    It processes data and passes it to the next agent in the pipeline.

Testing strategy:
    - Test with exact URL duplicates → should remove them
    - Test with similar URLs (different query params) → should catch them
    - Test with similar titles from different sources → should catch them
    - Test with completely different articles → should keep all
    - Test with empty list → should return empty list
    - Test preserves first occurrence → should keep the earliest article

Possible improvements:
    - Use TF-IDF vectors for more accurate title comparison
    - Add summary comparison as a 4th layer
    - Allow configurable similarity threshold
    - Track which articles were removed (for logging/debugging)
    - Add source priority (prefer The Hacker News over lesser-known sources)
"""

from difflib import SequenceMatcher
from urllib.parse import urlparse, urlunparse

from models.schemas import Article
from utils.logger import get_logger

# Create a logger named "agents.duplicate"
logger = get_logger(__name__)

# ============================================
# Configuration
# ============================================

# Title similarity threshold (0.0 to 1.0)
# Titles scoring at or above this value are considered duplicates.
#
# Why 0.75?
#   SequenceMatcher uses the Ratcliff/Obershelp algorithm which scores
#   reworded versions of the same headline around 0.75-0.85.
#   Testing with real cybersecurity headlines showed:
#     - "Critical Chrome Zero-Day Vulnerability Patched by Google" vs
#       "Google Patches Critical Chrome Zero-Day Vulnerability" → 0.77
#     - "Chrome browser update released" vs
#       "Chrome extension found stealing data" → 0.45
#   So 0.75 catches real duplicates without false positives.
TITLE_SIMILARITY_THRESHOLD = 0.75


def _normalize_url(url: str) -> str:
    """
    Normalizes a URL by removing query parameters, fragments, and trailing slashes.
    
    Why?
        RSS feeds often add tracking parameters to URLs:
        - "https://example.com/article?utm_source=rss&utm_medium=feed"
        - "https://example.com/article"
        These are the SAME article but different strings.
    
    Args:
        url: The original URL string
    
    Returns:
        Normalized URL without query params, fragments, or trailing slash
    
    Examples:
        >>> _normalize_url("https://example.com/article?utm_source=rss")
        'https://example.com/article'
        >>> _normalize_url("https://example.com/article/")
        'https://example.com/article'
    """
    if not url:
        return ""

    try:
        parsed = urlparse(url)
        # Rebuild URL with only scheme, netloc, and path
        # Drop: params, query, fragment
        normalized = urlunparse((
            parsed.scheme,    # "https"
            parsed.netloc,    # "example.com"
            parsed.path,      # "/article"
            "",               # params (dropped)
            "",               # query (dropped)
            "",               # fragment (dropped)
        ))
        # Remove trailing slash for consistency
        return normalized.rstrip("/")
    except Exception:
        return url


def _normalize_title(title: str) -> str:
    """
    Normalizes a title for comparison by lowercasing and stripping whitespace.
    
    Why normalize before comparing?
        - "Critical Chrome Flaw" and "critical chrome flaw" are the same
        - "  Chrome Flaw  " and "Chrome Flaw" are the same
        Without normalization, SequenceMatcher would see them as different.
    
    Args:
        title: The original article title
    
    Returns:
        Lowercase, stripped title
    """
    if not title:
        return ""
    return title.lower().strip()


def _calculate_title_similarity(title1: str, title2: str) -> float:
    """
    Calculates how similar two titles are, returning a score from 0.0 to 1.0.
    
    Uses a TWO-STRATEGY approach:
        1. Character-level: SequenceMatcher on the raw strings
           Good for titles with minor edits ("Chrome Flaw" vs "Chrome Flaws")
        
        2. Token-level: Sort words alphabetically, then compare
           Good for reworded titles where word ORDER changes but content is same
           "Google Patches Chrome Zero-Day" → "chrome google patches zero-day"
           "Chrome Zero-Day Patched by Google" → "by chrome google patched zero-day"
    
    Takes the MAXIMUM of both scores. This way we catch duplicates regardless
    of whether the rewording changed word order or just tweaked a few characters.
    
    Why SequenceMatcher over other options?
        - Part of Python standard library (no extra dependencies)
        - Works well for short text like headlines
        - Fast enough for hundreds of articles
        - No ML model needed (saves memory and compute)
    
    Args:
        title1: First title (already normalized to lowercase)
        title2: Second title (already normalized to lowercase)
    
    Returns:
        Similarity score between 0.0 (completely different) and 1.0 (identical)
    
    Examples:
        >>> _calculate_title_similarity(
        ...     "google patches critical chrome zero-day",
        ...     "critical chrome zero-day patched by google"
        ... )
        0.88  # High — token sorting reveals same content
    """
    if not title1 or not title2:
        return 0.0

    # Strategy 1: Character-level comparison (order-sensitive)
    char_score = SequenceMatcher(None, title1, title2).ratio()

    # Strategy 2: Token-level comparison (order-insensitive)
    # Sort words alphabetically so word order doesn't matter
    sorted1 = " ".join(sorted(title1.split()))
    sorted2 = " ".join(sorted(title2.split()))
    token_score = SequenceMatcher(None, sorted1, sorted2).ratio()

    # Return the best score from either strategy
    return max(char_score, token_score)


def _is_duplicate(
    article: Article,
    seen_urls: set[str],
    seen_titles: list[str],
) -> bool:
    """
    Checks if an article is a duplicate of any previously seen article.
    
    Applies the 3-layer detection strategy:
        1. Exact URL match (fastest, most certain)
        2. Normalized URL match (catches tracking params)
        3. Title similarity (catches "same story, different headline")
    
    Why check in this order?
        We go from cheapest to most expensive:
        - URL set lookup: O(1) — instant
        - Normalized URL set lookup: O(1) — instant  
        - Title comparison: O(n*m) — compares against all seen titles
        
        Most duplicates are caught by URL checks, so we rarely need
        the expensive title comparison.
    
    Args:
        article: The article to check
        seen_urls: Set of URLs already processed (both raw and normalized)
        seen_titles: List of normalized titles already processed
    
    Returns:
        True if the article is a duplicate, False if it's unique
    """
    # Layer 1: Exact URL match
    if article.link in seen_urls:
        logger.debug(f"Duplicate (exact URL): {article.title}")
        return True

    # Layer 2: Normalized URL match
    normalized_url = _normalize_url(article.link)
    if normalized_url in seen_urls:
        logger.debug(f"Duplicate (normalized URL): {article.title}")
        return True

    # Layer 3: Title similarity
    normalized_title = _normalize_title(article.title)
    for seen_title in seen_titles:
        similarity = _calculate_title_similarity(normalized_title, seen_title)
        if similarity >= TITLE_SIMILARITY_THRESHOLD:
            logger.debug(
                f"Duplicate (title similarity {similarity:.2f}): "
                f"'{article.title}' matches '{seen_title}'"
            )
            return True

    return False


def remove_duplicates(articles: list[Article]) -> list[Article]:
    """
    Removes duplicate articles from the list.
    
    This is the main entry point for the Duplicate Agent.
    
    How it works:
        1. Iterate through articles in order
        2. For each article, check if it's a duplicate
        3. If unique, add to results and record its URL/title
        4. If duplicate, skip it and log the removal
    
    Why keep the FIRST occurrence?
        Articles are ordered by feed (Hacker News first, then Bleeping Computer,
        etc.). The first occurrence typically has the most complete summary.
        We could add source priority later as an improvement.
    
    Args:
        articles: List of Article objects (from Collector Agent)
    
    Returns:
        List of unique Article objects (duplicates removed)
    
    Example:
        >>> from agents.duplicate import remove_duplicates
        >>> unique = remove_duplicates(articles)
        >>> print(f"Removed {len(articles) - len(unique)} duplicates")
    """
    if not articles:
        logger.info("No articles to deduplicate")
        return []

    logger.info(f"Deduplicating {len(articles)} articles...")

    unique_articles: list[Article] = []
    seen_urls: set[str] = set()       # O(1) lookup for URL checks
    seen_titles: list[str] = []       # List for title comparisons

    duplicates_removed = 0

    for article in articles:
        if _is_duplicate(article, seen_urls, seen_titles):
            duplicates_removed += 1
            continue

        # Article is unique — add it to our tracking sets
        unique_articles.append(article)
        seen_urls.add(article.link)
        seen_urls.add(_normalize_url(article.link))
        seen_titles.append(_normalize_title(article.title))

    logger.info(
        f"Deduplication complete. "
        f"Kept {len(unique_articles)} unique articles, "
        f"removed {duplicates_removed} duplicates."
    )

    return unique_articles


# ============================================
# LangGraph Node Function
# ============================================

def duplicate_node(state: dict) -> dict:
    """
    LangGraph node function for the Duplicate Agent.
    
    Reads raw_articles from state, removes duplicates,
    and writes unique_articles back to state.
    
    Args:
        state: The current pipeline state dictionary
               Expected to contain "raw_articles" key
    
    Returns:
        Dictionary with state updates:
        - "unique_articles": deduplicated article list
        - "current_stage": updated to "deduplication_complete"
    """
    logger.info("Duplicate Agent starting...")

    raw_articles = state.get("raw_articles", [])
    unique_articles = remove_duplicates(raw_articles)

    logger.info(f"Duplicate Agent finished. {len(unique_articles)} unique articles.")

    return {
        "unique_articles": unique_articles,
        "current_stage": "deduplication_complete",
    }
