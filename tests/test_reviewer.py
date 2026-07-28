"""
Tests for the Reviewer Agent
===============================

Purpose:
    Verifies that the Reviewer Agent correctly scores, reviews, and
    identifies issues in magazine articles.

Testing strategy:
    - Test rule-based review with complete articles → high score
    - Test with incomplete articles → low score, issues flagged
    - Test LLM response parsing
    - Test batch review
    - Test the reflection pattern concept
    - Edge cases

How to run:
    pytest tests/test_reviewer.py -v
"""

import pytest

from agents.reviewer import (
    APPROVAL_THRESHOLD,
    RAG_FIDELITY_THRESHOLD,
    _compute_rag_fidelity,
    _format_article_for_review,
    _parse_review_response,
    _review_by_rules,
    review_article,
    review_articles,
)
from models.schemas import MagazineArticle, ReviewResult


# ============================================
# Helper: Create test magazine articles
# ============================================

def make_complete_article() -> MagazineArticle:
    """Creates a complete, well-formed magazine article."""
    return MagazineArticle(
        title="Analysis: Critical Zero-Day Vulnerability in Chrome Browser",
        executive_summary=(
            "Google has patched a critical zero-day vulnerability in Chrome "
            "that was actively exploited in the wild. Organizations should "
            "update immediately to mitigate the risk."
        ),
        background=(
            "Zero-day vulnerabilities are security flaws unknown to the vendor. "
            "This particular vulnerability was discovered by Google's Threat "
            "Analysis Group (TAG) and affects Chrome versions prior to 120. "
            "The vulnerability has been assigned CVE-2026-1234."
        ),
        technical_analysis=(
            "The vulnerability is a use-after-free bug in Chrome's V8 "
            "JavaScript engine. Attackers can craft a malicious web page "
            "that triggers the bug, leading to arbitrary code execution. "
            "The exploit requires user interaction (visiting the page)."
        ),
        impact=(
            "All organizations using Chrome browser are potentially affected. "
            "The vulnerability could lead to remote code execution, data theft, "
            "and system compromise. Consumer users are also at risk."
        ),
        recommendations=(
            "1. Update Chrome to the latest version immediately\n"
            "2. Enable automatic updates for all browsers\n"
            "3. Implement network-level protections\n"
            "4. Monitor for indicators of compromise\n"
            "5. Review browser security policies"
        ),
        references=(
            "- Google Security Blog\n"
            "- NIST CVE Database\n"
            "- MITRE ATT&CK Framework"
        ),
        original_link="https://example.com/chrome-zeroday",
        category="Zero-Day",
    )


def make_incomplete_article() -> MagazineArticle:
    """Creates an article with missing/short sections."""
    return MagazineArticle(
        title="Short",
        executive_summary="Brief.",
        background="",  # Missing entirely
        technical_analysis="Short analysis.",  # Too short
        impact="",  # Missing
        recommendations="Update now.",  # Too short
        references="",  # Missing
        original_link="https://example.com/test",
        category="Test",
    )


# ============================================
# Tests for _review_by_rules()
# ============================================

class TestRuleBasedReview:
    """Tests for the rule-based review fallback."""

    def test_complete_article_scores_high(self):
        """Complete article should score 7+ and be approved."""
        article = make_complete_article()
        result = _review_by_rules(article)

        assert result.quality_score >= APPROVAL_THRESHOLD
        assert result.approved is True
        assert len(result.issues) == 0

    def test_incomplete_article_scores_low(self):
        """Article with missing sections should score low."""
        article = make_incomplete_article()
        result = _review_by_rules(article)

        assert result.quality_score < APPROVAL_THRESHOLD
        assert result.approved is False
        assert len(result.issues) > 0

    def test_detects_missing_sections(self):
        """Should flag each missing section as an issue."""
        article = make_incomplete_article()
        result = _review_by_rules(article)

        issue_text = " ".join(result.issues).lower()
        assert "missing" in issue_text or "short" in issue_text

    def test_detects_short_title(self):
        """Should flag titles shorter than 5 characters."""
        article = make_complete_article()
        article.title = "Hi"  # Too short
        result = _review_by_rules(article)

        assert any("title" in issue.lower() for issue in result.issues)

    def test_score_clamped_to_range(self):
        """Score should always be between 1 and 10."""
        # Article with many issues should still have score >= 1
        article = MagazineArticle(
            title="",
            executive_summary="",
            background="",
            technical_analysis="",
            impact="",
            recommendations="",
            references="",
            original_link="",
            category="",
        )
        result = _review_by_rules(article)
        assert 1 <= result.quality_score <= 10

    def test_perfect_score_possible(self):
        """A complete article should be able to score 10."""
        article = make_complete_article()
        result = _review_by_rules(article)
        assert result.quality_score == 10

    def test_returns_review_result(self):
        """Should return a ReviewResult object."""
        article = make_complete_article()
        result = _review_by_rules(article)
        assert isinstance(result, ReviewResult)

    def test_review_notes_present(self):
        """Should include review notes."""
        article = make_complete_article()
        result = _review_by_rules(article)
        assert result.review_notes != ""


# ============================================
# Tests for _format_article_for_review()
# ============================================

class TestFormatArticle:
    """Tests for article formatting."""

    def test_includes_all_sections(self):
        """Formatted text should include all section headings."""
        article = make_complete_article()
        text = _format_article_for_review(article)

        assert "Executive Summary" in text
        assert "Background" in text
        assert "Technical Analysis" in text
        assert "Impact" in text
        assert "Recommendations" in text
        assert "References" in text

    def test_includes_title(self):
        """Formatted text should include the article title."""
        article = make_complete_article()
        text = _format_article_for_review(article)
        assert article.title in text

    def test_includes_content(self):
        """Formatted text should include section content."""
        article = make_complete_article()
        text = _format_article_for_review(article)
        assert "V8 JavaScript engine" in text  # From technical analysis


# ============================================
# Tests for _parse_review_response()
# ============================================

class TestParseReviewResponse:
    """Tests for parsing LLM review responses."""

    def test_parses_high_score(self):
        """Should extract a high quality score."""
        text = """
- **Quality Score**: 9
- **Approved**: YES
- **Issues Found**: None
- **Revised Article**: No changes needed
"""
        result = _parse_review_response(text)
        assert result.quality_score == 9
        assert result.approved is True

    def test_parses_low_score(self):
        """Should extract a low quality score with issues."""
        text = """
- **Quality Score**: 4
- **Approved**: NO
- **Issues Found**:
- Missing technical depth in analysis
- Recommendations are too generic
- **Revised Article**: No changes needed
"""
        result = _parse_review_response(text)
        assert result.quality_score == 4
        assert result.approved is False
        assert len(result.issues) >= 1

    def test_clamps_invalid_score(self):
        """Should clamp scores outside 1-10 range."""
        text = "Quality Score: 15\nApproved: YES\nIssues Found: None"
        result = _parse_review_response(text)
        assert result.quality_score <= 10

    def test_parses_rag_fidelity_score(self):
        """Should extract RAG fidelity score from LLM response."""
        text = """
- **Quality Score**: 8
- **RAG Fidelity Score**: 7
- **Approved**: YES
- **Issues Found**: None
- **RAG Issues**: None
- **Revised Article**: No changes needed
"""
        result = _parse_review_response(text)
        assert result.rag_fidelity_score == 7
        assert result.approved is True

    def test_parses_rag_issues(self):
        """Should extract RAG-specific issues."""
        text = """
- **Quality Score**: 7
- **RAG Fidelity Score**: 4
- **Approved**: NO
- **Issues Found**: Grammar issues
- **RAG Issues**:
- Claim about quantum encryption not supported by context
- **Revised Article**: No changes needed
"""
        result = _parse_review_response(text)
        assert result.rag_fidelity_score == 4
        assert len(result.rag_issues) >= 1

    def test_handles_missing_fields(self):
        """Should handle response with missing fields gracefully."""
        text = "This article is good."
        result = _parse_review_response(text)
        assert isinstance(result, ReviewResult)
        assert 1 <= result.quality_score <= 10


# ============================================
# Tests for RAG Fidelity
# ============================================

class TestRagFidelity:
    """Tests for RAG-grounded verification."""

    def test_high_overlap_scores_high(self):
        """Article with overlapping keywords should score high."""
        article = make_complete_article()
        rag_context = (
            "Zero-day vulnerability use-after-free Chrome V8 JavaScript "
            "engine arbitrary code execution remote patch update browser"
        )
        score, issues = _compute_rag_fidelity(article, rag_context)
        assert score >= RAG_FIDELITY_THRESHOLD
        assert len(issues) == 0

    def test_low_overlap_scores_low(self):
        """Article with no overlap should score low."""
        article = make_complete_article()
        rag_context = (
            "xylophone zucchini quasar photon nebula heliotrope "
            "bamboozle flibbertigibbet kerfuffle"
        )
        score, issues = _compute_rag_fidelity(article, rag_context)
        assert score < RAG_FIDELITY_THRESHOLD
        assert len(issues) > 0

    def test_empty_rag_context_scores_perfect(self):
        """Empty RAG context should not penalize the article."""
        article = make_complete_article()
        score, issues = _compute_rag_fidelity(article, "")
        assert score == 10
        assert issues == []

    def test_review_with_rag_context(self):
        """review_article should return rag_fidelity_score."""
        article = make_complete_article()
        rag_context = (
            "Zero-day vulnerability Chrome browser patch update "
            "remote code execution V8 JavaScript engine"
        )
        result = review_article(article, rag_context=rag_context)
        assert hasattr(result, "rag_fidelity_score")
        assert 1 <= result.rag_fidelity_score <= 10

    def test_low_rag_fidelity_blocks_approval(self):
        """Low RAG fidelity should prevent approval even with good structure."""
        article = make_complete_article()
        rag_context = "completely unrelated kubernetes docker container topic"
        result = _review_by_rules(article, rag_context=rag_context)
        if result.rag_fidelity_score < RAG_FIDELITY_THRESHOLD:
            assert result.approved is False


# ============================================
# Tests for review_article()
# ============================================

class TestReviewArticle:
    """Tests for the main review function."""

    def test_returns_review_result(self):
        """Should return a ReviewResult."""
        article = make_complete_article()
        result = review_article(article)
        assert isinstance(result, ReviewResult)

    def test_complete_article_approved(self):
        """Complete article should be approved."""
        article = make_complete_article()
        result = review_article(article)
        assert result.approved is True

    def test_incomplete_article_not_approved(self):
        """Incomplete article should not be approved."""
        article = make_incomplete_article()
        result = review_article(article)
        assert result.approved is False


# ============================================
# Tests for review_articles() (batch)
# ============================================

class TestReviewArticles:
    """Tests for batch review."""

    def test_reviews_multiple_articles(self):
        """Should review all articles in the list."""
        articles = [
            make_complete_article(),
            make_incomplete_article(),
            make_complete_article(),
        ]
        results = review_articles(articles)

        assert len(results) == 3
        assert all(isinstance(r, ReviewResult) for r in results)

    def test_empty_list(self):
        """Should handle empty list."""
        results = review_articles([])
        assert results == []

    def test_mixed_results(self):
        """Should produce different scores for different quality articles."""
        articles = [
            make_complete_article(),    # Should pass
            make_incomplete_article(),  # Should fail
        ]
        results = review_articles(articles)

        assert results[0].quality_score > results[1].quality_score
        assert results[0].approved is True
        assert results[1].approved is False


# ============================================
# Edge Case Tests
# ============================================

class TestEdgeCases:
    """Edge case tests for the Reviewer Agent."""

    def test_all_empty_sections(self):
        """Should handle article with all empty sections."""
        article = MagazineArticle(
            title="Test Article Title Here",
            executive_summary="",
            background="",
            technical_analysis="",
            impact="",
            recommendations="",
            references="",
            original_link="",
            category="",
        )
        result = review_article(article)
        assert isinstance(result, ReviewResult)
        assert result.approved is False

    def test_article_with_only_title(self):
        """Should review articles that only have a title."""
        article = MagazineArticle(
            title="Complete Title for Testing Purposes",
            original_link="https://example.com",
            category="Test",
        )
        result = review_article(article)
        assert result.approved is False
        assert len(result.issues) > 0

    def test_review_result_serializable(self):
        """ReviewResult should be JSON-serializable."""
        article = make_complete_article()
        result = review_article(article)
        json_data = result.model_dump_json()
        assert isinstance(json_data, str)
        assert "quality_score" in json_data
