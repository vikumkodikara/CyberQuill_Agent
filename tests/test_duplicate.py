"""
Tests for the Duplicate Detection Agent
==========================================

Purpose:
    Verifies that the Duplicate Agent correctly identifies and removes
    duplicate articles across all three detection layers.

Testing strategy:
    1. Unit tests for helper functions (_normalize_url, _normalize_title, _calculate_title_similarity)
    2. Tests for each detection layer independently
    3. Integration test combining all layers
    4. Edge case tests (empty list, single article, all duplicates)

How to run:
    pytest tests/test_duplicate.py -v

Dependencies:
    - pytest
    - agents.duplicate (the module being tested)
    - models.schemas.Article (test data)
"""

import pytest

from agents.duplicate import (
    TITLE_SIMILARITY_THRESHOLD,
    _calculate_title_similarity,
    _normalize_title,
    _normalize_url,
    remove_duplicates,
)
from models.schemas import Article


# ============================================
# Helper: Create test articles quickly
# ============================================

def make_article(title: str, link: str, source: str = "Test Source") -> Article:
    """
    Factory function to create test articles with minimal boilerplate.
    
    Why a helper function?
        Writing Article(title=..., link=..., source=...) for every test
        is verbose. This shortcut makes tests easier to read.
    """
    return Article(title=title, link=link, source=source)


# ============================================
# Tests for _normalize_url()
# ============================================

class TestNormalizeUrl:
    """Tests for URL normalization."""

    def test_removes_query_parameters(self):
        """Should strip ?utm_source=rss and similar tracking params."""
        result = _normalize_url(
            "https://example.com/article?utm_source=rss&utm_medium=feed"
        )
        assert result == "https://example.com/article"

    def test_removes_fragment(self):
        """Should strip #section anchors."""
        result = _normalize_url("https://example.com/article#comments")
        assert result == "https://example.com/article"

    def test_removes_trailing_slash(self):
        """Should strip trailing slash for consistency."""
        result = _normalize_url("https://example.com/article/")
        assert result == "https://example.com/article"

    def test_preserves_path(self):
        """Should keep the URL path intact."""
        result = _normalize_url("https://example.com/2026/07/big-breach")
        assert result == "https://example.com/2026/07/big-breach"

    def test_empty_string(self):
        """Should handle empty string without error."""
        result = _normalize_url("")
        assert result == ""

    def test_url_without_query(self):
        """Should return the URL unchanged if no query params exist."""
        result = _normalize_url("https://example.com/article")
        assert result == "https://example.com/article"


# ============================================
# Tests for _normalize_title()
# ============================================

class TestNormalizeTitle:
    """Tests for title normalization."""

    def test_lowercases_title(self):
        """Should convert to lowercase."""
        result = _normalize_title("Critical Chrome ZERO-DAY Patched")
        assert result == "critical chrome zero-day patched"

    def test_strips_whitespace(self):
        """Should remove leading and trailing whitespace."""
        result = _normalize_title("  Chrome Flaw  ")
        assert result == "chrome flaw"

    def test_empty_string(self):
        """Should handle empty string."""
        result = _normalize_title("")
        assert result == ""


# ============================================
# Tests for _calculate_title_similarity()
# ============================================

class TestTitleSimilarity:
    """Tests for title similarity scoring."""

    def test_identical_titles(self):
        """Identical titles should score 1.0."""
        score = _calculate_title_similarity(
            "chrome zero day patched",
            "chrome zero day patched",
        )
        assert score == 1.0

    def test_completely_different_titles(self):
        """Unrelated titles should score low."""
        score = _calculate_title_similarity(
            "chrome zero day patched",
            "ransomware attack hits hospital network",
        )
        assert score < 0.5

    def test_similar_titles_above_threshold(self):
        """Same story with different wording should score above threshold."""
        score = _calculate_title_similarity(
            "critical chrome zero-day vulnerability patched by google",
            "google patches critical chrome zero-day vulnerability",
        )
        # These are the same story — should be above 0.75
        assert score >= TITLE_SIMILARITY_THRESHOLD

    def test_different_stories_below_threshold(self):
        """Different stories with some common words should score below threshold."""
        score = _calculate_title_similarity(
            "chrome browser update released with security fixes",
            "chrome extension found stealing user credentials",
        )
        # Different stories — should be below 0.85
        assert score < TITLE_SIMILARITY_THRESHOLD

    def test_empty_title(self):
        """Empty titles should score 0.0."""
        score = _calculate_title_similarity("", "some title")
        assert score == 0.0

    def test_both_empty(self):
        """Two empty titles should score 0.0."""
        score = _calculate_title_similarity("", "")
        assert score == 0.0


# ============================================
# Tests for remove_duplicates() — Layer 1: Exact URL
# ============================================

class TestExactUrlDuplicates:
    """Tests for exact URL duplicate detection."""

    def test_removes_exact_url_duplicate(self):
        """Articles with identical URLs should be deduplicated."""
        articles = [
            make_article("Article A", "https://example.com/article-1", "Source 1"),
            make_article("Article A Copy", "https://example.com/article-1", "Source 2"),
        ]
        result = remove_duplicates(articles)
        assert len(result) == 1
        assert result[0].title == "Article A"  # Keeps the first one

    def test_keeps_different_urls(self):
        """Articles with different URLs and titles should all be kept."""
        articles = [
            make_article("Ransomware Attack Hits Major Bank", "https://example.com/article-1"),
            make_article("New Phishing Kit Sold on Dark Web", "https://example.com/article-2"),
            make_article("Zero-Day Found in Popular Router Firmware", "https://example.com/article-3"),
        ]
        result = remove_duplicates(articles)
        assert len(result) == 3


# ============================================
# Tests for remove_duplicates() — Layer 2: Normalized URL
# ============================================

class TestNormalizedUrlDuplicates:
    """Tests for normalized URL duplicate detection."""

    def test_removes_url_with_tracking_params(self):
        """URLs that differ only in query params should be deduplicated."""
        articles = [
            make_article("Article A", "https://example.com/article-1"),
            make_article(
                "Article A (via feed)",
                "https://example.com/article-1?utm_source=rss",
            ),
        ]
        result = remove_duplicates(articles)
        assert len(result) == 1

    def test_removes_url_with_trailing_slash(self):
        """URLs that differ only in trailing slash should be deduplicated."""
        articles = [
            make_article("Article A", "https://example.com/article-1"),
            make_article("Article A", "https://example.com/article-1/"),
        ]
        result = remove_duplicates(articles)
        assert len(result) == 1


# ============================================
# Tests for remove_duplicates() — Layer 3: Title Similarity
# ============================================

class TestTitleSimilarityDuplicates:
    """Tests for fuzzy title duplicate detection."""

    def test_removes_similar_titles_different_sources(self):
        """Same story from different sources should be deduplicated."""
        articles = [
            make_article(
                "Critical Chrome Zero-Day Vulnerability Patched by Google",
                "https://hackernews.com/chrome-zeroday",
                "The Hacker News",
            ),
            make_article(
                "Google Patches Critical Chrome Zero-Day Vulnerability",
                "https://securityweek.com/chrome-zeroday-patch",
                "SecurityWeek",
            ),
        ]
        result = remove_duplicates(articles)
        assert len(result) == 1
        assert result[0].source == "The Hacker News"  # Keeps first

    def test_keeps_different_stories(self):
        """Clearly different stories should both be kept."""
        articles = [
            make_article(
                "Ransomware Gang Hits Major Hospital Chain",
                "https://source1.com/ransomware",
            ),
            make_article(
                "New AI Tool Detects Phishing Emails",
                "https://source2.com/ai-phishing",
            ),
        ]
        result = remove_duplicates(articles)
        assert len(result) == 2


# ============================================
# Edge Case Tests
# ============================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_list(self):
        """Should return empty list without error."""
        result = remove_duplicates([])
        assert result == []

    def test_single_article(self):
        """Single article should always be kept."""
        articles = [make_article("Only Article", "https://example.com/only")]
        result = remove_duplicates(articles)
        assert len(result) == 1

    def test_all_duplicates(self):
        """When all articles are duplicates, keep only the first."""
        articles = [
            make_article("Same Article", "https://example.com/same"),
            make_article("Same Article", "https://example.com/same"),
            make_article("Same Article", "https://example.com/same"),
        ]
        result = remove_duplicates(articles)
        assert len(result) == 1

    def test_preserves_article_order(self):
        """Unique articles should maintain their original order."""
        articles = [
            make_article("Ransomware Hits Hospital Network", "https://example.com/1"),
            make_article("New Phishing Campaign Targets Banks", "https://example.com/2"),
            make_article("Zero-Day Found in Enterprise Software", "https://example.com/3"),
        ]
        result = remove_duplicates(articles)
        assert result[0].title == "Ransomware Hits Hospital Network"
        assert result[1].title == "New Phishing Campaign Targets Banks"
        assert result[2].title == "Zero-Day Found in Enterprise Software"

    def test_preserves_all_article_fields(self):
        """Deduplication should not modify any article fields."""
        original = Article(
            title="Test Article",
            link="https://example.com/test",
            source="Test Source",
            published="2026-07-21",
            summary="This is a test summary",
        )
        result = remove_duplicates([original])
        assert result[0].title == original.title
        assert result[0].link == original.link
        assert result[0].source == original.source
        assert result[0].published == original.published
        assert result[0].summary == original.summary


# ============================================
# Integration Test: Full Pipeline
# ============================================

class TestIntegration:
    """Integration test simulating a real collection scenario."""

    def test_mixed_duplicates_across_sources(self):
        """
        Simulates articles from multiple sources with various
        types of duplicates mixed in.
        """
        articles = [
            # Unique article 1
            make_article(
                "New Ransomware Variant Targets Healthcare",
                "https://hackernews.com/ransomware-healthcare",
                "The Hacker News",
            ),
            # Unique article 2
            make_article(
                "CISA Releases Advisory on Critical Infrastructure",
                "https://cisa.gov/advisory-2026-07",
                "CISA",
            ),
            # Duplicate of article 1 (similar title, different URL)
            make_article(
                "Ransomware Variant Targets Healthcare Organizations",
                "https://bleeping.com/ransomware-healthcare-orgs",
                "Bleeping Computer",
            ),
            # Duplicate of article 1 (exact URL)
            make_article(
                "Ransomware in Healthcare",
                "https://hackernews.com/ransomware-healthcare",
                "The Hacker News",
            ),
            # Unique article 3
            make_article(
                "Zero-Day in Popular VPN Software Exploited",
                "https://darkreading.com/vpn-zeroday",
                "Dark Reading",
            ),
            # Duplicate of article 2 (URL with tracking params)
            make_article(
                "CISA Advisory on Critical Infrastructure",
                "https://cisa.gov/advisory-2026-07?ref=rss",
                "CISA",
            ),
        ]

        result = remove_duplicates(articles)

        # Should keep exactly 3 unique articles
        assert len(result) == 3

        # Verify the correct articles were kept (first occurrences)
        titles = [a.title for a in result]
        assert "New Ransomware Variant Targets Healthcare" in titles
        assert "CISA Releases Advisory on Critical Infrastructure" in titles
        assert "Zero-Day in Popular VPN Software Exploited" in titles
