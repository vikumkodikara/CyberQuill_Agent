"""
CyberQuill Collector Agent

Purpose:
    Fetches cybersecurity news articles from multiple RSS feeds and
    returns them as a list of standardized Article objects.

    This is the FIRST agent in the pipeline. Everything downstream
    depends on the data this agent produces.

How it works (step by step):
    1. Reads the list of RSS feed URLs from config/settings.py
    2. For each URL, uses `feedparser` to download and parse the feed
    3. Extracts title, link, source name, published date, and summary
    4. Normalizes the data into our Article schema (models/schemas.py)
    5. Returns all articles as a list

Inputs:
    - List of RSS feed URLs (from settings.RSS_FEEDS)

Outputs:
    - List[Article] — standardized article objects

Dependencies:
    - feedparser: Parses RSS/Atom feeds
    - python-dateutil: Parses inconsistent date formats
    - models.schemas.Article: The data model for articles
    - config.settings: RSS feed URLs
    - utils.logger: Logging

Agentic AI Design Pattern:
    **Tool Use Pattern** — This agent uses feedparser as an external
    tool to fetch and parse RSS data. The agent doesn't contain the
    parsing logic itself; it delegates to a specialized tool.

Testing strategy:
    - Test with a live feed → should return articles
    - Test with an invalid URL → should handle error gracefully
    - Test data normalization → all fields should be populated
    - Test empty feed → should return empty list without crashing

Possible improvements:
    - Add caching to avoid re-fetching unchanged feeds
    - Add rate limiting to be polite to feed servers
    - Add parallel fetching with asyncio for speed
    - Add content extraction (fetch full article text from URL)
    - Add feed health monitoring (track which feeds are up/down)
"""

from datetime import datetime
from typing import Optional

import feedparser
from dateutil import parser as date_parser

from config.settings import settings
from models.schemas import Article
from utils.logger import get_logger

# Create a logger named "agents.collector"
# This name appears in log messages so we know which agent produced them
logger = get_logger(__name__)


# ============================================
# Source Name Mapping
# ============================================
# RSS feeds don't always include a clean source name.
# This dictionary maps feed URLs to human-readable names.
# Why? Because "https://feeds.feedburner.com/TheHackersNews"
# is not a useful source name in a magazine article.

SOURCE_MAP: dict[str, str] = {
    "feeds.feedburner.com": "The Hacker News",
    "bleepingcomputer.com": "Bleeping Computer",
    "krebsonsecurity.com": "Krebs on Security",
    "securityweek.com": "SecurityWeek",
    "darkreading.com": "Dark Reading",
    "cisa.gov": "CISA",
}


def _extract_source_name(feed_url: str, feed_title: Optional[str] = None) -> str:
    """
    Determines a clean, human-readable source name from the feed URL.

    Strategy:
        1. Check our SOURCE_MAP for a known domain → use the mapped name
        2. If not in the map, use the feed's own title (from RSS metadata)
        3. If no title either, use the domain name as a fallback

    Args:
        feed_url: The URL of the RSS feed
        feed_title: The title from the feed's metadata (if available)

    Returns:
        A human-readable source name (e.g., "The Hacker News")

    Why a separate function?
        - Keeps the main collection logic clean
        - Easy to test independently
        - Easy to add new sources
    """
    # Check each known domain against the feed URL
    for domain, name in SOURCE_MAP.items():
        if domain in feed_url:
            return name

    # Fallback to the feed's own title
    if feed_title:
        return feed_title

    # Last resort: extract domain from URL
    # "https://example.com/feed/" → "example.com"
    try:
        from urllib.parse import urlparse
        return urlparse(feed_url).netloc
    except Exception:
        return "Unknown Source"


def _parse_date(date_string: str) -> str:
    """
    Parses various date formats into a consistent ISO format string.

    Why is this needed?
        RSS feeds use many different date formats:
        - "Mon, 21 Jul 2026 10:00:00 GMT"
        - "2026-07-21T10:00:00+00:00"
        - "July 21, 2026"
        python-dateutil handles all of these automatically.

    Args:
        date_string: The raw date string from the RSS feed

    Returns:
        ISO format string (e.g., "2026-07-21T10:00:00")
        or the original string if parsing fails

    Why not raise an error on failure?
        A bad date shouldn't prevent us from collecting the article.
        The article content is more important than a perfect date.
    """
    if not date_string:
        return datetime.now().isoformat()

    try:
        parsed = date_parser.parse(date_string)
        return parsed.isoformat()
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not parse date '{date_string}': {e}")
        return date_string


def _clean_summary(summary: str) -> str:
    """
    Cleans HTML tags and extra whitespace from article summaries.

    Why?
        RSS feed summaries often contain HTML tags like <p>, <a>, <img>.
        We want plain text for our pipeline because:
        - The LLM classifier works better with clean text
        - The magazine writer doesn't need source HTML
        - It reduces token count (saves money on API calls)

    Args:
        summary: Raw summary text (may contain HTML)

    Returns:
        Cleaned plain text summary
    """
    if not summary:
        return ""

    import re

    # Remove HTML tags: <anything> → empty string
    clean = re.sub(r"<[^>]+>", "", summary)

    # Replace HTML entities
    clean = clean.replace("&amp;", "&")
    clean = clean.replace("&lt;", "<")
    clean = clean.replace("&gt;", ">")
    clean = clean.replace("&quot;", '"')
    clean = clean.replace("&#39;", "'")
    clean = clean.replace("&nbsp;", " ")

    # Collapse multiple whitespace/newlines into single spaces
    clean = re.sub(r"\s+", " ", clean).strip()

    return clean


def fetch_single_feed(feed_url: str) -> list[Article]:
    """
    Fetches and parses a single RSS feed, returning a list of Article objects.

    This is the core function. It:
        1. Downloads the RSS feed using feedparser
        2. Extracts the source name
        3. Loops through each entry (article) in the feed
        4. Normalizes each entry into an Article object
        5. Handles errors gracefully (logs them, doesn't crash)

    Args:
        feed_url: URL of the RSS feed to fetch

    Returns:
        List of Article objects from this feed.
        Returns an empty list if the feed fails to load.

    Why return empty list on error (not raise)?
        If one feed is down, we still want articles from the other 5 feeds.
        Crashing the entire pipeline because CISA's feed is slow would
        mean we get ZERO articles instead of articles from 5 sources.
    """
    logger.info(f"Fetching feed: {feed_url}")
    articles: list[Article] = []

    try:
        # feedparser.parse() downloads and parses the RSS/Atom feed
        # It handles HTTP requests, XML parsing, and encoding issues
        feed = feedparser.parse(feed_url)

        # Check if the feed loaded successfully
        # feed.bozo is True if feedparser encountered any issues
        if feed.bozo and not feed.entries:
            logger.warning(
                f"Feed error for {feed_url}: {feed.get('bozo_exception', 'Unknown error')}"
            )
            return []

        # Get the source name for all articles in this feed
        feed_title = feed.feed.get("title", None)
        source_name = _extract_source_name(feed_url, feed_title)

        logger.info(f"Found {len(feed.entries)} entries from {source_name}")

        # Process each article in the feed
        for entry in feed.entries:
            try:
                article = Article(
                    title=entry.get("title", "Untitled"),
                    link=entry.get("link", ""),
                    source=source_name,
                    published=_parse_date(
                        entry.get("published", entry.get("updated", ""))
                    ),
                    summary=_clean_summary(
                        entry.get("summary", entry.get("description", ""))
                    ),
                )
                articles.append(article)

            except Exception as e:
                # If ONE article fails to parse, skip it and continue
                # Don't let one bad entry ruin the entire feed
                logger.warning(
                    f"Skipping entry from {source_name}: {e}"
                )
                continue

    except Exception as e:
        # Catch network errors, timeouts, etc.
        logger.error(f"Failed to fetch feed {feed_url}: {e}")
        return []

    return articles


def collect_all_feeds(feed_urls: Optional[list[str]] = None) -> list[Article]:
    """
    Fetches articles from ALL configured RSS feeds.

    This is the main entry point for the Collector Agent.
    The orchestrator (LangGraph pipeline) will call this function.

    Args:
        feed_urls: Optional list of feed URLs. If not provided,
                   uses the URLs from settings.RSS_FEEDS.
                   This parameter exists for testing — you can
                   pass a single URL to test one feed at a time.

    Returns:
        List of all Article objects collected from all feeds.

    Example:
        >>> from agents.collector import collect_all_feeds
        >>> articles = collect_all_feeds()
        >>> print(f"Collected {len(articles)} articles")
    """
    urls = feed_urls or settings.RSS_FEEDS

    logger.info(f"Starting collection from {len(urls)} feeds")

    all_articles: list[Article] = []

    for url in urls:
        feed_articles = fetch_single_feed(url)
        all_articles.extend(feed_articles)

    logger.info(f"Collection complete. Total articles: {len(all_articles)}")

    return all_articles


# ============================================
# LangGraph Node Function
# ============================================
# LangGraph agents are functions that take state and return state updates.
# This function wraps collect_all_feeds() to work as a LangGraph node.

def collector_node(state: dict) -> dict:
    """
    LangGraph node function for the Collector Agent.

    How LangGraph works:
        - Each agent is a "node" in a graph
        - Nodes receive the current pipeline state (a dictionary)
        - Nodes return updates to the state
        - LangGraph merges the updates into the state

    Args:
        state: The current pipeline state dictionary

    Returns:
        Dictionary with state updates:
        - "raw_articles": the collected articles
        - "current_stage": updated to "collection_complete"
    """
    logger.info("Collector Agent starting...")

    articles = collect_all_feeds()

    logger.info(f"Collector Agent finished. Collected {len(articles)} articles.")

    return {
        "raw_articles": articles,
        "current_stage": "collection_complete",
    }
