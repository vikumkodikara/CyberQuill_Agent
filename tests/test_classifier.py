"""
Tests for the Classification Agent
=====================================

Purpose:
    Verifies that the Classification Agent correctly categorizes
    cybersecurity articles using both keyword-based and LLM-based methods.

Testing strategy:
    - Unit tests for keyword classification (no API needed, always runnable)
    - Tests for edge cases (empty text, no matching keywords)
    - Tests for the classify_articles pipeline function
    - LLM integration tests are skipped if GROQ_API_KEY is not set

How to run:
    pytest tests/test_classifier.py -v

Dependencies:
    - pytest
    - agents.classifier
    - models.schemas
"""

import pytest

from agents.classifier import (
    _classify_by_keywords,
    classify_article,
    classify_articles,
)
from models.schemas import Article, ClassifiedArticle


# ============================================
# Helper: Create test articles
# ============================================

def make_article(title: str, summary: str = "") -> Article:
    """Creates a test article with minimal fields."""
    return Article(
        title=title,
        link=f"https://example.com/{title[:20].lower().replace(' ', '-')}",
        source="Test Source",
        summary=summary,
    )


# ============================================
# Tests for _classify_by_keywords()
# ============================================

class TestKeywordClassification:
    """Tests for the keyword-based fallback classifier."""

    def test_malware_by_title(self):
        """Should classify articles mentioning 'ransomware' as Malware."""
        category, confidence = _classify_by_keywords(
            "New Ransomware Strain Targets Healthcare",
            "A sophisticated ransomware attack has been discovered.",
        )
        assert category == "Malware"
        assert confidence > 0.0

    def test_data_breach_by_title(self):
        """Should classify articles about breaches as Data Breach."""
        category, confidence = _classify_by_keywords(
            "Major Data Breach Exposes 10 Million Records",
            "Personal data was leaked from a healthcare database.",
        )
        assert category == "Data Breach"
        assert confidence > 0.0

    def test_ai_security(self):
        """Should classify AI-related security articles."""
        category, confidence = _classify_by_keywords(
            "ChatGPT Vulnerability Allows Prompt Injection Attacks",
            "Researchers discover prompt injection vulnerability in LLM systems.",
        )
        assert category == "AI Security"
        assert confidence > 0.0

    def test_cloud_security(self):
        """Should classify cloud-related articles."""
        category, confidence = _classify_by_keywords(
            "AWS S3 Bucket Misconfiguration Exposes Sensitive Data",
            "Cloud misconfiguration in kubernetes cluster leads to breach.",
        )
        assert category == "Cloud Security"
        assert confidence > 0.0

    def test_zero_day(self):
        """Should classify zero-day vulnerability articles."""
        category, confidence = _classify_by_keywords(
            "Critical Zero-Day in Chrome Actively Exploited",
            "Google patches a critical zero-day vulnerability CVE-2026-1234.",
        )
        assert category == "Zero-Day"
        assert confidence > 0.0

    def test_threat_intelligence(self):
        """Should classify threat intelligence articles."""
        category, confidence = _classify_by_keywords(
            "APT Group Linked to Nation-State Cyber Espionage Campaign",
            "New threat actor group attributed to state-sponsored campaign.",
        )
        assert category == "Threat Intelligence"
        assert confidence > 0.0

    def test_vulnerability_management(self):
        """Should classify vulnerability/patch articles."""
        category, confidence = _classify_by_keywords(
            "Microsoft Releases Critical Security Update for Windows",
            "Security advisory covers multiple CVE patches and firmware updates.",
        )
        assert category == "Vulnerability Management"
        assert confidence > 0.0

    def test_uncategorized_when_no_match(self):
        """Should return Uncategorized when no keywords match."""
        category, confidence = _classify_by_keywords(
            "Company Announces New Office Location",
            "The tech firm will open a new office in downtown.",
        )
        assert category == "Uncategorized"
        assert confidence == 0.0

    def test_empty_title_and_summary(self):
        """Should handle empty inputs without crashing."""
        category, confidence = _classify_by_keywords("", "")
        assert category == "Uncategorized"
        assert confidence == 0.0

    def test_confidence_is_bounded(self):
        """Confidence should never exceed 0.9 for keyword matching."""
        # Article with many malware keywords → high match count
        category, confidence = _classify_by_keywords(
            "Ransomware malware trojan botnet virus payload",
            "Backdoor rootkit spyware keylogger infostealer worm",
        )
        assert confidence <= 0.9

    def test_picks_strongest_category(self):
        """When multiple categories match, should pick the one with most matches."""
        # This title has more Malware keywords than Zero-Day keywords
        category, confidence = _classify_by_keywords(
            "New Ransomware Trojan Malware Uses Backdoor",
            "The botnet delivers spyware payload via rootkit.",
        )
        assert category == "Malware"


# ============================================
# Tests for classify_article()
# ============================================

class TestClassifyArticle:
    """Tests for the single-article classification function."""

    def test_returns_classified_article(self):
        """Should return a ClassifiedArticle object."""
        article = make_article(
            "Ransomware Attack on Hospital",
            "Malware encrypts patient records.",
        )
        result = classify_article(article)
        assert isinstance(result, ClassifiedArticle)

    def test_preserves_original_fields(self):
        """Classification should not lose any original article data."""
        article = Article(
            title="Test Ransomware Article",
            link="https://example.com/test",
            source="Test Source",
            published="2026-07-21",
            summary="A ransomware attack was discovered.",
        )
        result = classify_article(article)

        # All original fields should be preserved
        assert result.title == article.title
        assert result.link == article.link
        assert result.source == article.source
        assert result.published == article.published
        assert result.summary == article.summary

        # New fields should be populated
        assert result.category != ""
        assert result.confidence >= 0.0

    def test_assigns_category(self):
        """Should assign a meaningful category."""
        article = make_article(
            "Zero-Day Exploit Found in Chrome",
            "Actively exploited vulnerability discovered.",
        )
        result = classify_article(article)
        # Without API key, uses keyword fallback
        assert result.category in [
            "Malware", "Data Breach", "AI Security", "Cloud Security",
            "Zero-Day", "Threat Intelligence", "Vulnerability Management",
            "Uncategorized",
        ]


# ============================================
# Tests for classify_articles() (batch)
# ============================================

class TestClassifyArticles:
    """Tests for the batch classification function."""

    def test_classifies_multiple_articles(self):
        """Should classify all articles in the list."""
        articles = [
            make_article("Ransomware Hits Bank", "Malware attack on banking systems."),
            make_article("AWS Breach Exposes Data", "S3 bucket misconfiguration found."),
            make_article("Zero-Day in Windows", "Critical exploit actively used."),
        ]
        result = classify_articles(articles)

        assert len(result) == 3
        assert all(isinstance(a, ClassifiedArticle) for a in result)

    def test_empty_list(self):
        """Should handle empty list without error."""
        result = classify_articles([])
        assert result == []

    def test_each_article_has_category(self):
        """Every classified article should have a category field."""
        articles = [
            make_article("Critical Malware Found", "Trojan distributed via email."),
        ]
        result = classify_articles(articles)
        assert result[0].category != ""

    def test_classification_distribution(self):
        """Articles with different topics should get different categories."""
        articles = [
            make_article("Ransomware Trojan Malware Attack", "Botnet delivers payload."),
            make_article("Major Data Breach at Hospital", "10M records leaked from database."),
            make_article("Zero-Day Exploit in Chrome", "CVE-2026-1234 actively exploited."),
        ]
        result = classify_articles(articles)

        categories = {a.category for a in result}
        # Should have at least 2 different categories
        assert len(categories) >= 2


# ============================================
# Integration Test: Full Collector → Duplicate → Classifier Pipeline
# ============================================

class TestPipelineIntegration:
    """Tests the first 3 agents working together."""

    def test_collector_to_classifier_pipeline(self):
        """
        End-to-end test: Collect → Deduplicate → Classify.
        Uses a single feed to keep the test fast.
        """
        from agents.collector import collect_all_feeds
        from agents.duplicate import remove_duplicates

        # Step 1: Collect
        articles = collect_all_feeds(
            feed_urls=["https://feeds.feedburner.com/TheHackersNews"]
        )
        assert len(articles) > 0

        # Step 2: Deduplicate
        unique = remove_duplicates(articles)
        assert len(unique) > 0

        # Step 3: Classify (keyword mode — no API key needed)
        classified = classify_articles(unique[:5])  # Classify first 5 only
        assert len(classified) == 5

        # Verify output
        for article in classified:
            assert isinstance(article, ClassifiedArticle)
            assert article.title != ""
            assert article.category != ""

            # Print for visual inspection during test run
            print(f"  [{article.category}] {article.title[:60]}...")
