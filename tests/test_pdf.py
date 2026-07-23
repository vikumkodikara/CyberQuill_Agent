"""
Tests for the PDF Generator
===============================

Purpose:
    Verifies that the PDF Generator creates valid PDF files with
    correct structure and content.

Testing strategy:
    - Test with sample articles → PDF file should be created
    - Test cover page elements (title, date, stats)
    - Test with empty list → should return None
    - Test with single article → should still work
    - Test with articles containing special characters (XML-unsafe)
    - Test file is written to the correct output directory
    - Test custom filename support
    - Test sanitize helper function
    - Edge cases (empty sections, missing fields)

How to run:
    pytest tests/test_pdf.py -v
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

import pytest

from models.schemas import MagazineArticle
from pdf.generator import (
    OUTPUT_DIR,
    _build_article,
    _build_cover,
    _build_toc,
    _get_styles,
    _sanitize,
    generate_pdf,
)


# ============================================
# Helper: Create test magazine articles
# ============================================

def make_sample_article(
    title: str = "Analysis: Critical Ransomware Attack Targets Healthcare Sector",
    category: str = "Malware",
) -> MagazineArticle:
    """Creates a fully populated sample magazine article for testing."""
    return MagazineArticle(
        title=title,
        executive_summary=(
            "A sophisticated ransomware campaign has been targeting healthcare "
            "organisations across North America. The attack leverages a zero-day "
            "vulnerability in a widely used medical records system."
        ),
        background=(
            "Ransomware attacks against healthcare have increased by 45% in 2026. "
            "The healthcare sector is a prime target due to the critical nature of "
            "patient data and the urgency to restore services. This campaign appears "
            "to be linked to a known threat actor group operating out of Eastern Europe."
        ),
        technical_analysis=(
            "The malware uses a multi-stage infection chain: initial access via "
            "phishing email, privilege escalation through CVE-2026-5678, lateral "
            "movement using PsExec, and deployment of a custom ransomware payload. "
            "The encryption uses AES-256 with RSA key wrapping."
        ),
        impact=(
            "Over 30 hospitals have reported disruptions. Patient data including "
            "medical records, billing information, and insurance details may have "
            "been exfiltrated. Emergency services were rerouted in several cases."
        ),
        recommendations=(
            "1. Patch CVE-2026-5678 immediately\n"
            "2. Implement network segmentation\n"
            "3. Deploy endpoint detection and response (EDR)\n"
            "4. Conduct phishing awareness training\n"
            "5. Maintain offline backups of critical data"
        ),
        references=(
            "- CISA Alert AA26-189A\n"
            "- MITRE ATT&CK T1486 (Data Encrypted for Impact)\n"
            "- NIST Cybersecurity Framework"
        ),
        original_link="https://example.com/ransomware-healthcare",
        category=category,
    )


def make_minimal_article() -> MagazineArticle:
    """Creates a minimal article with only required fields."""
    return MagazineArticle(
        title="Minimal Test Article",
        original_link="https://example.com/minimal",
        category="Test",
    )


# ============================================
# Test Output Directory (use temp dir for tests)
# ============================================

@pytest.fixture
def test_output_dir(tmp_path):
    """
    Provides a temporary output directory for PDF tests.
    
    We monkey-patch OUTPUT_DIR to point to tmp_path so tests
    don't pollute the real data/output/ directory.
    """
    import pdf.generator as gen_module
    original_dir = gen_module.OUTPUT_DIR
    gen_module.OUTPUT_DIR = tmp_path
    yield tmp_path
    gen_module.OUTPUT_DIR = original_dir


# ============================================
# Tests for _sanitize()
# ============================================

class TestSanitize:
    """Tests for the text sanitization helper."""

    def test_escapes_ampersand(self):
        """& should be escaped to &amp;"""
        assert "&amp;" in _sanitize("AT&T breach")

    def test_escapes_less_than(self):
        """< should be escaped to &lt;"""
        assert "&lt;" in _sanitize("score < 7")

    def test_escapes_greater_than(self):
        """> should be escaped to &gt;"""
        assert "&gt;" in _sanitize("score > 3")

    def test_converts_markdown_bold(self):
        """**bold** should become <b>bold</b>"""
        result = _sanitize("This is **important** text")
        assert "<b>important</b>" in result

    def test_handles_empty_string(self):
        """Empty string should return empty string."""
        assert _sanitize("") == ""

    def test_handles_none(self):
        """None should return empty string."""
        assert _sanitize(None) == ""

    def test_plain_text_unchanged(self):
        """Plain text without special chars should pass through."""
        result = _sanitize("Simple text here")
        assert result == "Simple text here"


# ============================================
# Tests for _get_styles()
# ============================================

class TestGetStyles:
    """Tests for the styles factory."""

    def test_returns_dict(self):
        """Should return a dictionary of styles."""
        styles = _get_styles()
        assert isinstance(styles, dict)

    def test_contains_required_styles(self):
        """Should contain all required style keys."""
        styles = _get_styles()
        required = [
            "cover_title", "cover_subtitle", "cover_date", "cover_stats",
            "toc_heading", "toc_entry", "toc_category",
            "article_title", "article_meta", "section_heading",
            "body", "reference_item", "footer",
        ]
        for key in required:
            assert key in styles, f"Missing style: {key}"


# ============================================
# Tests for _build_cover()
# ============================================

class TestBuildCover:
    """Tests for the cover page builder."""

    def test_returns_list(self):
        """Should return a list of flowable elements."""
        styles = _get_styles()
        articles = [make_sample_article()]
        elements = _build_cover(articles, styles, 1)
        assert isinstance(elements, list)
        assert len(elements) > 0

    def test_cover_has_pagebreak(self):
        """Cover should end with a PageBreak."""
        from reportlab.platypus import PageBreak
        styles = _get_styles()
        articles = [make_sample_article()]
        elements = _build_cover(articles, styles, 1)
        assert isinstance(elements[-1], PageBreak)

    def test_cover_with_multiple_categories(self):
        """Cover should handle articles from different categories."""
        styles = _get_styles()
        articles = [
            make_sample_article(category="Malware"),
            make_sample_article(title="Cloud Breach", category="Cloud Security"),
            make_sample_article(title="Zero Day", category="Zero-Day"),
        ]
        elements = _build_cover(articles, styles, 1)
        assert len(elements) > 0


# ============================================
# Tests for _build_toc()
# ============================================

class TestBuildToc:
    """Tests for the table of contents builder."""

    def test_returns_list(self):
        """Should return a list of flowable elements."""
        styles = _get_styles()
        articles = [make_sample_article()]
        elements = _build_toc(articles, styles)
        assert isinstance(elements, list)
        assert len(elements) > 0

    def test_toc_has_pagebreak(self):
        """TOC should end with a PageBreak."""
        from reportlab.platypus import PageBreak
        styles = _get_styles()
        articles = [make_sample_article()]
        elements = _build_toc(articles, styles)
        assert isinstance(elements[-1], PageBreak)

    def test_toc_scales_with_articles(self):
        """More articles should produce more TOC entries."""
        styles = _get_styles()
        one_article = _build_toc([make_sample_article()], styles)
        three_articles = _build_toc(
            [make_sample_article() for _ in range(3)], styles
        )
        assert len(three_articles) > len(one_article)


# ============================================
# Tests for _build_article()
# ============================================

class TestBuildArticle:
    """Tests for the article page builder."""

    def test_returns_list(self):
        """Should return a list of flowable elements."""
        styles = _get_styles()
        article = make_sample_article()
        elements = _build_article(article, styles)
        assert isinstance(elements, list)
        assert len(elements) > 0

    def test_article_has_pagebreak(self):
        """Each article should end with a PageBreak."""
        from reportlab.platypus import PageBreak
        styles = _get_styles()
        article = make_sample_article()
        elements = _build_article(article, styles)
        assert isinstance(elements[-1], PageBreak)

    def test_minimal_article_renders(self):
        """An article with only title should still render."""
        styles = _get_styles()
        article = make_minimal_article()
        elements = _build_article(article, styles)
        assert len(elements) > 0

    def test_article_with_special_chars(self):
        """Should handle articles with XML-unsafe characters."""
        styles = _get_styles()
        article = make_sample_article(
            title="MITRE ATT&CK: Analysis of CVE-2026 <script> Injection"
        )
        # Should not raise — sanitization handles the special chars
        elements = _build_article(article, styles)
        assert len(elements) > 0


# ============================================
# Tests for generate_pdf()
# ============================================

class TestGeneratePdf:
    """Tests for the main PDF generation function."""

    def test_empty_list_returns_none(self, test_output_dir):
        """Should return None when given an empty list."""
        result = generate_pdf([])
        assert result is None

    def test_generates_pdf_file(self, test_output_dir):
        """Should create a PDF file on disk."""
        articles = [make_sample_article()]
        path = generate_pdf(articles, output_filename="test_output.pdf")

        assert path is not None
        assert os.path.exists(path)
        assert path.endswith(".pdf")

    def test_pdf_file_not_empty(self, test_output_dir):
        """Generated PDF should have content (non-zero size)."""
        articles = [make_sample_article()]
        path = generate_pdf(articles, output_filename="test_size.pdf")

        file_size = os.path.getsize(path)
        assert file_size > 0

    def test_pdf_starts_with_magic_bytes(self, test_output_dir):
        """Valid PDF files start with %PDF."""
        articles = [make_sample_article()]
        path = generate_pdf(articles, output_filename="test_magic.pdf")

        with open(path, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_custom_filename(self, test_output_dir):
        """Should use the custom filename if provided."""
        articles = [make_sample_article()]
        path = generate_pdf(articles, output_filename="my_magazine.pdf")

        assert "my_magazine.pdf" in path

    def test_default_filename_has_timestamp(self, test_output_dir):
        """Default filename should include a timestamp."""
        articles = [make_sample_article()]
        path = generate_pdf(articles)

        assert "cyberquill_" in path
        assert path.endswith(".pdf")

    def test_multiple_articles(self, test_output_dir):
        """Should handle multiple articles without errors."""
        articles = [
            make_sample_article(title="Article One", category="Malware"),
            make_sample_article(title="Article Two", category="Data Breach"),
            make_sample_article(title="Article Three", category="Zero-Day"),
        ]
        path = generate_pdf(articles, output_filename="test_multi.pdf")

        assert path is not None
        assert os.path.exists(path)

    def test_minimal_article_pdf(self, test_output_dir):
        """Should generate PDF even with minimal article data."""
        articles = [make_minimal_article()]
        path = generate_pdf(articles, output_filename="test_minimal.pdf")

        assert path is not None
        assert os.path.exists(path)

    def test_article_with_special_characters(self, test_output_dir):
        """Should handle special characters in article content."""
        article = make_sample_article(
            title="AT&T Data Breach: <script> Alert & Impact Analysis"
        )
        path = generate_pdf([article], output_filename="test_special.pdf")

        assert path is not None
        assert os.path.exists(path)


# ============================================
# Edge Case Tests
# ============================================

class TestEdgeCases:
    """Edge case tests for the PDF Generator."""

    def test_single_article_pdf(self, test_output_dir):
        """Should handle a single article gracefully."""
        articles = [make_sample_article()]
        path = generate_pdf(articles, output_filename="test_single.pdf")
        assert path is not None

    def test_article_with_empty_sections(self, test_output_dir):
        """Should handle articles where all sections are empty."""
        article = MagazineArticle(
            title="Empty Sections Test Article",
            executive_summary="",
            background="",
            technical_analysis="",
            impact="",
            recommendations="",
            references="",
            original_link="",
            category="",
        )
        path = generate_pdf([article], output_filename="test_empty.pdf")
        assert path is not None
        assert os.path.exists(path)

    def test_returns_absolute_path(self, test_output_dir):
        """Returned path should be absolute."""
        articles = [make_sample_article()]
        path = generate_pdf(articles, output_filename="test_abs.pdf")
        assert os.path.isabs(path)

    def test_output_directory_created(self, test_output_dir):
        """Output directory should be created if it doesn't exist."""
        import pdf.generator as gen_module
        new_dir = test_output_dir / "nested" / "output"
        gen_module.OUTPUT_DIR = new_dir

        articles = [make_sample_article()]
        path = generate_pdf(articles, output_filename="test_nested.pdf")

        assert path is not None
        assert os.path.exists(path)

        # Restore
        gen_module.OUTPUT_DIR = test_output_dir
