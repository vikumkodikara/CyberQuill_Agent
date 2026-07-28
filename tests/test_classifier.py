"""
Tests for the Classification Agent
=====================================

Purpose:
    Verifies that the Classification Agent correctly categorizes
    cybersecurity articles using keyword-based and multi-pass methods.
"""

import pytest

from config.settings import settings
from agents.classifier import (
    UNCATEGORIZED,
    _best_guess_category,
    _classify_by_keywords,
    _is_security_article,
    _normalize_category,
    classify_article,
    classify_articles,
)
from models.schemas import Article, ClassifiedArticle


def make_article(title: str, summary: str = "") -> Article:
    """Creates a test article with minimal fields."""
    return Article(
        title=title,
        link=f"https://example.com/{title[:20].lower().replace(' ', '-')}",
        source="Test Source",
        summary=summary,
    )


SAMPLE_SECURITY_HEADLINES = [
    ("LockBit ransomware encrypts hospital systems", "Malware attack disrupts operations."),
    ("10 million customer records leaked online", "Database exposure affects millions."),
    ("ChatGPT prompt injection bypasses safety filters", "LLM vulnerability discovered."),
    ("AWS S3 bucket misconfiguration exposes data", "Cloud storage left public."),
    ("Chrome zero-day exploited in the wild", "Emergency patch released for CVE."),
    ("APT29 linked to new espionage campaign", "Nation-state threat actor attributed."),
    ("Microsoft Patch Tuesday fixes 80 flaws", "Security advisory lists CVE patches."),
    ("Phishing campaign delivers banking trojan", "Emails target financial sector."),
    ("Hackers steal credentials from retailer", "Customer accounts compromised."),
    ("Kubernetes cluster hit by cryptominer", "Container workload compromised."),
    ("Deepfake scam targets CEO wire transfers", "AI-generated voice used in fraud."),
    ("Emergency patch for actively exploited flaw", "Vendor urges immediate update."),
    ("Cybercrime gang indicted for ransomware", "Law enforcement takes down group."),
    ("Firmware update fixes critical security bug", "Advisory recommends patching."),
    ("Scam emails impersonate tax authority", "Social engineering campaign spreads."),
    ("OpenAI model vulnerable to jailbreak", "AI safety bypass demonstrated."),
    ("Azure misconfiguration leaks API keys", "Cloud tenant data exposed."),
    ("Threat actors use supply chain attack", "Software update channel compromised."),
    ("Bug bounty hunter finds RCE flaw", "Responsible disclosure leads to patch."),
    ("New banking malware spreads via SMS", "Mobile trojan targets users."),
]


class TestNormalizeCategory:
    """Tests for category response normalization."""

    def test_exact_match(self):
        assert _normalize_category("Malware") == "Malware"

    def test_with_punctuation(self):
        assert _normalize_category("Category: Zero-Day.") == "Zero-Day"

    def test_alias_ransomware(self):
        assert _normalize_category("This is about ransomware") == "Malware"

    def test_uncategorized_returns_none(self):
        assert _normalize_category("Uncategorized") is None

    def test_empty_returns_none(self):
        assert _normalize_category("") is None


class TestKeywordClassification:
    """Tests for the keyword-based fallback classifier."""

    def test_malware_by_title(self):
        category, confidence = _classify_by_keywords(
            "New Ransomware Strain Targets Healthcare",
            "A sophisticated ransomware attack has been discovered.",
        )
        assert category == "Malware"
        assert confidence > 0.0

    def test_phishing_classified_as_malware(self):
        category, _ = _classify_by_keywords(
            "Massive Phishing Campaign Targets Banks",
            "Scam emails deliver malicious payload.",
        )
        assert category == "Malware"

    def test_hack_classified_as_data_breach(self):
        category, _ = _classify_by_keywords(
            "Retail Giant Hacked — Customer Data Stolen",
            "Hackers exfiltrated millions of records.",
        )
        assert category == "Data Breach"

    def test_supply_chain_as_threat_intel(self):
        category, _ = _classify_by_keywords(
            "Supply Chain Attack Hits Software Vendor",
            "Threat actors compromised update channel.",
        )
        assert category == "Threat Intelligence"

    def test_data_breach_by_title(self):
        category, confidence = _classify_by_keywords(
            "Major Data Breach Exposes 10 Million Records",
            "Personal data was leaked from a healthcare database.",
        )
        assert category == "Data Breach"
        assert confidence > 0.0

    def test_ai_security(self):
        category, confidence = _classify_by_keywords(
            "ChatGPT Vulnerability Allows Prompt Injection Attacks",
            "Researchers discover prompt injection vulnerability in LLM systems.",
        )
        assert category == "AI Security"
        assert confidence > 0.0

    def test_cloud_security(self):
        category, confidence = _classify_by_keywords(
            "AWS S3 Bucket Misconfiguration Exposes Sensitive Data",
            "Cloud misconfiguration in kubernetes cluster leads to breach.",
        )
        assert category == "Cloud Security"
        assert confidence > 0.0

    def test_zero_day(self):
        category, confidence = _classify_by_keywords(
            "Critical Zero-Day in Chrome Actively Exploited",
            "Google patches a critical zero-day vulnerability CVE-2026-1234.",
        )
        assert category == "Zero-Day"
        assert confidence > 0.0

    def test_threat_intelligence(self):
        category, confidence = _classify_by_keywords(
            "APT Group Linked to Nation-State Cyber Espionage Campaign",
            "New threat actor group attributed to state-sponsored campaign.",
        )
        assert category == "Threat Intelligence"
        assert confidence > 0.0

    def test_vulnerability_management(self):
        category, confidence = _classify_by_keywords(
            "Microsoft Releases Critical Security Update for Windows",
            "Security advisory covers multiple CVE patches and firmware updates.",
        )
        assert category == "Vulnerability Management"
        assert confidence > 0.0

    def test_uncategorized_when_no_match(self):
        category, confidence = _classify_by_keywords(
            "Company Announces New Office Location",
            "The tech firm will open a new office in downtown.",
        )
        assert category == UNCATEGORIZED
        assert confidence == 0.0

    def test_empty_title_and_summary(self):
        category, confidence = _classify_by_keywords("", "")
        assert category == UNCATEGORIZED
        assert confidence == 0.0

    def test_confidence_is_bounded(self):
        category, confidence = _classify_by_keywords(
            "Ransomware malware trojan botnet virus payload",
            "Backdoor rootkit spyware keylogger infostealer worm",
        )
        assert confidence <= 0.9

    def test_picks_strongest_category(self):
        category, confidence = _classify_by_keywords(
            "New Ransomware Trojan Malware Uses Backdoor",
            "The botnet delivers spyware payload via rootkit.",
        )
        assert category == "Malware"


class TestBestGuess:
    """Tests for best-guess fallback."""

    def test_security_article_gets_category(self):
        category, confidence = _best_guess_category(
            "Cyber attack disrupts power grid",
            "Security incident under investigation.",
        )
        assert category != UNCATEGORIZED
        assert confidence > 0.0

    def test_non_security_stays_uncategorized(self):
        category, confidence = _best_guess_category(
            "Company opens new downtown office",
            "Expansion into retail market announced.",
        )
        assert category == UNCATEGORIZED
        assert confidence == 0.0


class TestIsSecurityArticle:
    """Tests for security signal detection."""

    def test_detects_security_content(self):
        assert _is_security_article("New ransomware attack", "Malware encrypts files.")

    def test_rejects_non_security(self):
        assert not _is_security_article("New office opening", "Retail expansion.")


class TestUncategorizedRate:
    """Regression test for uncategorized rate on sample headlines."""

    def test_uncategorized_rate_on_sample_headlines(self):
        articles = [make_article(title, summary) for title, summary in SAMPLE_SECURITY_HEADLINES]
        results = classify_articles(articles)

        uncategorized = sum(1 for r in results if r.category == UNCATEGORIZED)
        rate = uncategorized / len(results)

        assert rate <= 0.05, (
            f"Uncategorized rate {rate:.1%} exceeds 5% target "
            f"({uncategorized}/{len(results)} articles)"
        )


class TestClassifyArticle:
    """Tests for the single-article classification function."""

    def test_returns_classified_article(self):
        article = make_article(
            "Ransomware Attack on Hospital",
            "Malware encrypts patient records.",
        )
        result = classify_article(article)
        assert isinstance(result, ClassifiedArticle)

    def test_preserves_original_fields(self):
        article = Article(
            title="Test Ransomware Article",
            link="https://example.com/test",
            source="Test Source",
            published="2026-07-21",
            summary="A ransomware attack was discovered.",
        )
        result = classify_article(article)

        assert result.title == article.title
        assert result.link == article.link
        assert result.source == article.source
        assert result.published == article.published
        assert result.summary == article.summary
        assert result.category != ""
        assert result.confidence >= 0.0
        assert result.classification_method != ""

    def test_assigns_category(self):
        article = make_article(
            "Zero-Day Exploit Found in Chrome",
            "Actively exploited vulnerability discovered.",
        )
        result = classify_article(article)
        assert result.category in settings.CATEGORIES + [UNCATEGORIZED]

    def test_non_security_can_remain_uncategorized(self):
        article = make_article(
            "Company Announces New Office Location",
            "The firm expands into a new downtown building.",
        )
        result = classify_article(article)
        assert result.category == UNCATEGORIZED


class TestClassifyArticles:
    """Tests for the batch classification function."""

    def test_classifies_multiple_articles(self):
        articles = [
            make_article("Ransomware Hits Bank", "Malware attack on banking systems."),
            make_article("AWS Breach Exposes Data", "S3 bucket misconfiguration found."),
            make_article("Zero-Day in Windows", "Critical exploit actively used."),
        ]
        result = classify_articles(articles)

        assert len(result) == 3
        assert all(isinstance(a, ClassifiedArticle) for a in result)

    def test_empty_list(self):
        result = classify_articles([])
        assert result == []

    def test_each_article_has_category(self):
        articles = [
            make_article("Critical Malware Found", "Trojan distributed via email."),
        ]
        result = classify_articles(articles)
        assert result[0].category != ""

    def test_classification_distribution(self):
        articles = [
            make_article("Ransomware Trojan Malware Attack", "Botnet delivers payload."),
            make_article("Major Data Breach at Hospital", "10M records leaked from database."),
            make_article("Zero-Day Exploit in Chrome", "CVE-2026-1234 actively exploited."),
        ]
        result = classify_articles(articles)

        categories = {a.category for a in result}
        assert len(categories) >= 2


class TestForcedChoiceFallback:
    """Tests for forced-choice LLM fallback."""

    def test_forced_choice_used_when_primary_fails(self, monkeypatch):
        from agents import classifier as clf

        call_count = {"n": 0}

        def mock_invoke(prompt):
            call_count["n"] += 1
            if "MUST pick the BEST" in prompt:
                return "Malware"
            return "invalid response"

        monkeypatch.setattr(clf, "_invoke_llm", mock_invoke)
        monkeypatch.setattr(clf, "_llm_available", lambda: True)

        article = make_article(
            "Obscure security incident reported",
            "Cyber attack affects regional systems.",
        )
        result = clf.classify_article(article)

        assert result.category == "Malware"
        assert result.classification_method == "forced_llm"
        assert call_count["n"] >= 2
