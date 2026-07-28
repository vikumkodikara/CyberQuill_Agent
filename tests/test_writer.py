"""
Tests for the Writer Agent
============================

Purpose:
    Verifies that the Writer Agent correctly transforms enriched articles
    into magazine-style articles using both template and LLM methods.

Testing strategy:
    - Unit tests for template-based writing (no API needed)
    - Tests for LLM response parsing
    - Tests for section extraction
    - Batch writing tests
    - Edge case tests
    - Pipeline integration test (Collect → Dedup → Classify → RAG → Write)

How to run:
    pytest tests/test_writer.py -v

Dependencies:
    - pytest
    - agents.writer
    - models.schemas
"""

import pytest

from agents.writer import (
    RAG_CONTEXT_MAX_CHARS,
    _extract_section,
    _parse_llm_sections,
    _write_by_template,
    write_article,
    write_articles,
)
from models.schemas import EnrichedArticle, MagazineArticle, ReviewResult


# ============================================
# Helper: Create test enriched articles
# ============================================

def make_enriched(
    title: str = "Critical Zero-Day in Chrome",
    summary: str = "Google patches a zero-day vulnerability in Chrome.",
    category: str = "Zero-Day",
    rag_context: str = "Zero-day vulnerabilities are flaws unknown to the vendor.",
    rag_sources: list[str] = None,
) -> EnrichedArticle:
    """Factory function to create test EnrichedArticle objects."""
    return EnrichedArticle(
        title=title,
        link=f"https://example.com/{title[:20].lower().replace(' ', '-')}",
        source="Test Source",
        published="2026-07-21",
        summary=summary,
        category=category,
        confidence=0.9,
        rag_context=rag_context,
        rag_sources=rag_sources or ["owasp_top_10.md"],
    )


# ============================================
# Tests for _parse_llm_sections()
# ============================================

class TestParseLlmSections:
    """Tests for parsing LLM markdown responses into sections."""

    def test_parses_hash_headings(self):
        """Should parse ## Heading style sections."""
        text = """## Executive Summary
This is the summary.

## Background
This is the background.

## Technical Analysis
This is the analysis."""

        sections = _parse_llm_sections(text)
        assert "Executive Summary" in sections
        assert "Background" in sections
        assert "Technical Analysis" in sections

    def test_extracts_content(self):
        """Should extract content between headings."""
        text = """## Summary
This is the summary content.

## Background
This is background content."""

        sections = _parse_llm_sections(text)
        assert "summary content" in sections.get("Summary", "")

    def test_empty_text(self):
        """Should handle empty text."""
        sections = _parse_llm_sections("")
        assert isinstance(sections, dict)


# ============================================
# Tests for _extract_section()
# ============================================

class TestExtractSection:
    """Tests for flexible section extraction."""

    def test_exact_match(self):
        """Should find section with exact heading."""
        sections = {"Executive Summary": "content here"}
        result = _extract_section(sections, "executive summary")
        assert result == "content here"

    def test_partial_match(self):
        """Should match if keyword is contained in heading."""
        sections = {"Technical Analysis & Deep Dive": "tech content"}
        result = _extract_section(sections, "technical", "analysis")
        assert result == "tech content"

    def test_fallback_keywords(self):
        """Should try multiple keywords and return first match."""
        sections = {"Overview": "overview content"}
        result = _extract_section(
            sections, "executive summary", "summary", "overview"
        )
        assert result == "overview content"

    def test_no_match_returns_empty(self):
        """Should return empty string if no keywords match."""
        sections = {"Unrelated": "some content"}
        result = _extract_section(sections, "executive summary")
        assert result == ""


# ============================================
# Tests for _write_by_template()
# ============================================

class TestTemplateWriting:
    """Tests for the template-based writing fallback."""

    def test_returns_magazine_article(self):
        """Should return a MagazineArticle object."""
        article = make_enriched()
        result = _write_by_template(article)
        assert isinstance(result, MagazineArticle)

    def test_title_includes_analysis(self):
        """Generated title should include 'Analysis:' prefix."""
        article = make_enriched(title="Chrome Zero-Day Found")
        result = _write_by_template(article)
        assert "Analysis:" in result.title

    def test_executive_summary_from_original(self):
        """Executive summary should use original article summary."""
        article = make_enriched(
            summary="Google patches a critical vulnerability."
        )
        result = _write_by_template(article)
        assert "Google patches" in result.executive_summary

    def test_background_uses_rag_context(self):
        """Background section should incorporate RAG context."""
        article = make_enriched(
            rag_context="OWASP lists injection as a top vulnerability."
        )
        result = _write_by_template(article)
        assert "OWASP" in result.background

    def test_background_fallback_when_no_context(self):
        """Should provide generic background when no RAG context."""
        article = make_enriched(rag_context="")
        result = _write_by_template(article)
        assert article.category in result.background

    def test_preserves_original_link(self):
        """Should preserve the link to the original article."""
        article = make_enriched()
        result = _write_by_template(article)
        assert result.original_link == article.link

    def test_preserves_category(self):
        """Should preserve the article category."""
        article = make_enriched(category="Malware")
        result = _write_by_template(article)
        assert result.category == "Malware"

    def test_all_sections_populated(self):
        """All magazine article sections should have content."""
        article = make_enriched()
        result = _write_by_template(article)

        assert result.title != ""
        assert result.executive_summary != ""
        assert result.background != ""
        assert result.technical_analysis != ""
        assert result.impact != ""
        assert result.recommendations != ""
        assert result.references != ""

    def test_references_include_source(self):
        """References should include the original source."""
        article = make_enriched()
        result = _write_by_template(article)
        assert article.source in result.references

    def test_references_include_rag_sources(self):
        """References should list RAG source documents."""
        article = make_enriched(rag_sources=["owasp_top_10.md", "nist_csf.md"])
        result = _write_by_template(article)
        assert "owasp_top_10.md" in result.references

    def test_generated_at_timestamp(self):
        """Should have a generated_at timestamp."""
        article = make_enriched()
        result = _write_by_template(article)
        assert result.generated_at != ""


# ============================================
# Tests for write_article() (with fallback)
# ============================================

class TestWriteArticle:
    """Tests for the main write_article function."""

    def test_returns_magazine_article(self):
        """Should return MagazineArticle regardless of method."""
        article = make_enriched()
        result = write_article(article)
        assert isinstance(result, MagazineArticle)

    def test_handles_empty_summary(self):
        """Should work even with empty summary."""
        article = make_enriched(summary="")
        result = write_article(article)
        assert result.executive_summary != ""

    def test_handles_empty_rag_context(self):
        """Should work even with no RAG context."""
        article = make_enriched(rag_context="", rag_sources=[])
        result = write_article(article)
        assert result.background != ""

    def test_revision_falls_back_to_template(self):
        """Revision without LLM should fall back to template writing."""
        enriched = make_enriched()
        previous = _write_by_template(enriched)
        review = ReviewResult(
            quality_score=5,
            approved=False,
            issues=["Technical analysis too shallow"],
            rag_issues=["Missing OWASP references"],
            rag_fidelity_score=4,
        )
        result = write_article(
            enriched,
            previous_article=previous,
            review_result=review,
        )
        assert isinstance(result, MagazineArticle)
        assert result.title != ""


# ============================================
# Tests for RAG context limits
# ============================================

class TestRagContextLimits:
    """Tests for RAG context handling in writer."""

    def test_template_uses_extended_context(self):
        """Template should use more than 800 chars of RAG context."""
        long_context = "injection vulnerability " * 200
        article = make_enriched(rag_context=long_context)
        result = _write_by_template(article)
        assert len(result.background) > 800

    def test_max_chars_constant(self):
        """RAG context max should be 3000 chars."""
        assert RAG_CONTEXT_MAX_CHARS == 3000


# ============================================
# Tests for write_articles() (batch)
# ============================================

class TestWriteArticles:
    """Tests for batch article writing."""

    def test_writes_multiple_articles(self):
        """Should write all articles in the list."""
        articles = [
            make_enriched(title="Ransomware Hits Bank", category="Malware"),
            make_enriched(title="Zero-Day in Chrome", category="Zero-Day"),
            make_enriched(title="AWS Data Breach", category="Data Breach"),
        ]
        result = write_articles(articles)

        assert len(result) == 3
        assert all(isinstance(a, MagazineArticle) for a in result)

    def test_empty_list(self):
        """Should handle empty list."""
        result = write_articles([])
        assert result == []

    def test_each_article_has_category(self):
        """Each generated article should preserve its category."""
        articles = [
            make_enriched(category="Malware"),
            make_enriched(category="Zero-Day"),
        ]
        result = write_articles(articles)
        assert result[0].category == "Malware"
        assert result[1].category == "Zero-Day"


# ============================================
# Edge Case Tests
# ============================================

class TestEdgeCases:
    """Edge case tests for the Writer Agent."""

    def test_very_long_summary(self):
        """Should handle very long summaries."""
        long_summary = "Security vulnerability found. " * 100
        article = make_enriched(summary=long_summary)
        result = write_article(article)
        assert isinstance(result, MagazineArticle)

    def test_special_characters_in_title(self):
        """Should handle special characters in title."""
        article = make_enriched(
            title="CVE-2026-1234: Critical Flaw in 'Chrome' <v120>"
        )
        result = write_article(article)
        assert isinstance(result, MagazineArticle)

    def test_unicode_content(self):
        """Should handle unicode characters."""
        article = make_enriched(
            title="Análisis de Seguridad — Vulnerabilidad Crítica"
        )
        result = write_article(article)
        assert isinstance(result, MagazineArticle)
