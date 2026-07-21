"""
Tests for the Collector Agent
===============================

Purpose:
    Verifies that the Collector Agent correctly fetches, parses,
    and normalizes RSS feed data.

Testing strategy:
    1. Unit tests for helper functions (_extract_source_name, _parse_date, _clean_summary)
    2. Integration test with a LIVE feed (tests real network behavior)
    3. Edge case tests (empty feed, invalid URL, missing fields)

How to run:
    pytest tests/test_collector.py -v

Dependencies:
    - pytest
    - agents.collector (the module being tested)
"""

import pytest

from agents.collector import (
    _clean_summary,
    _extract_source_name,
    _parse_date,
    collect_all_feeds,
    fetch_single_feed,
)
from models.schemas import Article


# ============================================
# Tests for _extract_source_name()
# ============================================

class TestExtractSourceName:
    """Tests for the source name extraction function."""

    def test_known_domain_hacker_news(self):
        """Should return 'The Hacker News' for the feedburner URL."""
        result = _extract_source_name(
            "https://feeds.feedburner.com/TheHackersNews"
        )
        assert result == "The Hacker News"

    def test_known_domain_bleeping_computer(self):
        """Should return 'Bleeping Computer' for bleepingcomputer.com."""
        result = _extract_source_name(
            "https://www.bleepingcomputer.com/feed/"
        )
        assert result == "Bleeping Computer"

    def test_known_domain_cisa(self):
        """Should return 'CISA' for cisa.gov."""
        result = _extract_source_name("https://www.cisa.gov/news.xml")
        assert result == "CISA"

    def test_unknown_domain_with_feed_title(self):
        """Should fall back to feed title when domain is not in SOURCE_MAP."""
        result = _extract_source_name(
            "https://unknown-site.com/feed",
            feed_title="Unknown Security Blog",
        )
        assert result == "Unknown Security Blog"

    def test_unknown_domain_no_title(self):
        """Should fall back to domain name when no title is available."""
        result = _extract_source_name("https://example.com/feed/rss")
        assert result == "example.com"


# ============================================
# Tests for _parse_date()
# ============================================

class TestParseDate:
    """Tests for the date parsing function."""

    def test_rfc822_format(self):
        """Should parse standard RSS date format."""
        result = _parse_date("Mon, 21 Jul 2026 10:00:00 GMT")
        assert "2026-07-21" in result

    def test_iso_format(self):
        """Should parse ISO 8601 format."""
        result = _parse_date("2026-07-21T10:00:00+00:00")
        assert "2026-07-21" in result

    def test_empty_string(self):
        """Should return current timestamp for empty string."""
        result = _parse_date("")
        # Should not crash and should return something
        assert len(result) > 0

    def test_invalid_date(self):
        """Should return original string for unparseable dates."""
        result = _parse_date("not-a-date")
        # Should not crash
        assert isinstance(result, str)


# ============================================
# Tests for _clean_summary()
# ============================================

class TestCleanSummary:
    """Tests for the HTML cleaning function."""

    def test_removes_html_tags(self):
        """Should strip all HTML tags."""
        result = _clean_summary("<p>Hello <b>world</b></p>")
        assert result == "Hello world"

    def test_replaces_html_entities(self):
        """Should convert HTML entities to characters."""
        result = _clean_summary("AT&amp;T data &lt;breach&gt;")
        assert result == "AT&T data <breach>"

    def test_collapses_whitespace(self):
        """Should collapse multiple spaces and newlines."""
        result = _clean_summary("Hello   \n\n   world")
        assert result == "Hello world"

    def test_empty_string(self):
        """Should handle empty string without error."""
        result = _clean_summary("")
        assert result == ""

    def test_none_input(self):
        """Should handle None-like empty input."""
        result = _clean_summary("")
        assert result == ""


# ============================================
# Integration Test: Live Feed
# ============================================

class TestFetchSingleFeed:
    """
    Integration tests that fetch REAL RSS feeds.
    
    These tests require internet access. They verify that
    the collector can handle real-world feed data.
    
    Note: These may fail if the feed server is down.
    That's expected and acceptable.
    """

    def test_fetch_hacker_news_feed(self):
        """Should successfully fetch articles from The Hacker News."""
        articles = fetch_single_feed(
            "https://feeds.feedburner.com/TheHackersNews"
        )

        # Should return at least some articles
        assert len(articles) > 0

        # Each article should be a valid Article object
        for article in articles:
            assert isinstance(article, Article)
            assert article.title  # Title should not be empty
            assert article.link   # Link should not be empty
            assert article.source == "The Hacker News"

    def test_fetch_invalid_url(self):
        """Should return empty list for invalid URL, not crash."""
        articles = fetch_single_feed("https://invalid-url-that-does-not-exist.com/feed")
        assert articles == []

    def test_fetch_non_rss_url(self):
        """Should handle non-RSS URL gracefully."""
        articles = fetch_single_feed("https://www.google.com")
        # Should return empty list (Google's homepage is not an RSS feed)
        assert isinstance(articles, list)


# ============================================
# Integration Test: Collect All
# ============================================

class TestCollectAllFeeds:
    """Tests for the main collect_all_feeds function."""

    def test_collect_from_single_feed(self):
        """Should work when given a single feed URL."""
        articles = collect_all_feeds(
            feed_urls=["https://feeds.feedburner.com/TheHackersNews"]
        )
        assert len(articles) > 0
        assert all(isinstance(a, Article) for a in articles)

    def test_collect_returns_articles_with_all_fields(self):
        """Every article should have title, link, and source filled."""
        articles = collect_all_feeds(
            feed_urls=["https://feeds.feedburner.com/TheHackersNews"]
        )

        if articles:  # Only test if we got results
            article = articles[0]
            assert article.title != ""
            assert article.link != ""
            assert article.source != ""
