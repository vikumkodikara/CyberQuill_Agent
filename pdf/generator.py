"""
CyberQuill PDF Generator — Magazine Edition
==============================================

Purpose:
    Generates a professional magazine-style PDF from reviewed articles.
    Takes a list of MagazineArticle objects and produces a downloadable
    PDF file styled like a premium cybersecurity publication.

How it works:
    1. Creates a branded cover page with magazine title, issue number,
       date, and article count
    2. Adds a table of contents listing all articles by category
    3. Renders each article with all 6 sections, styled with headers,
       body text, and bullet points
    4. Adds page numbers, headers, footers and section separators

Why ReportLab?
    - Pure-Python PDF generation (no system dependencies like wkhtmltopdf)
    - Full control over layout, fonts, and styling
    - Works on all platforms (Windows, Mac, Linux)
    - Free and open source (BSD licence)
    - Deployable to Streamlit Community Cloud (no binaries needed)

Inputs:
    - List[MagazineArticle] — reviewed and approved magazine articles

Outputs:
    - A PDF file saved to data/output/ directory
    - Returns the file path as a string

Dependencies:
    - reportlab: PDF generation library
    - models.schemas: MagazineArticle
    - utils.logger: Logging
    - utils.content_sanitizer: Strip RAG artifacts
    - utils.issue_tracker: Issue numbering
    - config.settings: (indirectly, for output directory)

Testing strategy:
    - Test with sample articles → PDF file should be created
    - Test cover page content (title, date)
    - Test with empty list → should return None gracefully
    - Test with articles containing special characters
    - Test file cleanup (temp files)

Possible improvements:
    - Add article images or charts
    - Add colour-coded category badges
    - Add a "Top Stories" highlight section
    - Support custom fonts and branding
    - Add page headers with category names
"""

import os
import re
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

from models.schemas import MagazineArticle
from utils.logger import get_logger
from utils.content_sanitizer import sanitize_article

logger = get_logger(__name__)


# ============================================
# Constants
# ============================================

# Output directory for generated PDFs
OUTPUT_DIR = Path("data/output")

# Page dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.27 x 841.89 points

# Margins
LEFT_MARGIN = 2.2 * cm
RIGHT_MARGIN = 2.2 * cm
TOP_MARGIN = 2.5 * cm
BOTTOM_MARGIN = 2.8 * cm

# Colours — Professional magazine palette
NAVY = colors.HexColor("#0f172a")
DARK_BLUE = colors.HexColor("#1e293b")
MEDIUM_BLUE = colors.HexColor("#334155")
ACCENT_CYAN = colors.HexColor("#0ea5e9")
ACCENT_INDIGO = colors.HexColor("#6366f1")
GOLD_ACCENT = colors.HexColor("#f59e0b")
DARK_TEXT = colors.HexColor("#1e293b")
BODY_TEXT = colors.HexColor("#334155")
MUTED_TEXT = colors.HexColor("#64748b")
LIGHT_GREY = colors.HexColor("#e2e8f0")
COVER_BG = colors.HexColor("#0b0f19")
WHITE = colors.white
SEPARATOR_COLOR = colors.HexColor("#cbd5e1")


# ============================================
# Custom Styles
# ============================================

def _get_styles() -> dict[str, ParagraphStyle]:
    """
    Creates all paragraph styles used in the magazine PDF.

    Why custom styles?
        - Consistent typography across all pages
        - Professional appearance (not generic "report" look)
        - Easy to modify in one place if the design changes

    Returns:
        Dictionary mapping style names to ParagraphStyle objects
    """
    base = getSampleStyleSheet()

    styles = {}

    # ---- Cover Page Styles ----
    styles["cover_title"] = ParagraphStyle(
        "cover_title",
        parent=base["Title"],
        fontName="Times-Bold",
        fontSize=42,
        leading=48,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
    )

    styles["cover_subtitle"] = ParagraphStyle(
        "cover_subtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#94a3b8"),
        alignment=TA_CENTER,
        spaceAfter=12 * mm,
    )

    styles["cover_issue"] = ParagraphStyle(
        "cover_issue",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=ACCENT_CYAN,
        alignment=TA_CENTER,
        spaceAfter=3 * mm,
    )

    styles["cover_date"] = ParagraphStyle(
        "cover_date",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#94a3b8"),
        alignment=TA_CENTER,
        spaceAfter=18 * mm,
    )

    styles["cover_stats"] = ParagraphStyle(
        "cover_stats",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#cbd5e1"),
        alignment=TA_CENTER,
        spaceAfter=3 * mm,
    )

    # ---- Table of Contents Styles ----
    styles["toc_heading"] = ParagraphStyle(
        "toc_heading",
        parent=base["Heading1"],
        fontName="Times-Bold",
        fontSize=24,
        leading=30,
        textColor=NAVY,
        spaceAfter=10 * mm,
    )

    styles["toc_entry"] = ParagraphStyle(
        "toc_entry",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=DARK_TEXT,
        leftIndent=5 * mm,
        spaceAfter=1.5 * mm,
    )

    styles["toc_category"] = ParagraphStyle(
        "toc_category",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12,
        textColor=MUTED_TEXT,
        leftIndent=5 * mm,
        spaceAfter=4 * mm,
    )

    # ---- Article Styles ----
    styles["article_title"] = ParagraphStyle(
        "article_title",
        parent=base["Heading1"],
        fontName="Times-Bold",
        fontSize=22,
        leading=28,
        textColor=NAVY,
        spaceAfter=3 * mm,
    )

    styles["article_meta"] = ParagraphStyle(
        "article_meta",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12,
        textColor=MUTED_TEXT,
        spaceBefore=0,
        spaceAfter=8 * mm,
    )

    styles["section_heading"] = ParagraphStyle(
        "section_heading",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=DARK_BLUE,
        spaceBefore=8 * mm,
        spaceAfter=3 * mm,
    )

    styles["body"] = ParagraphStyle(
        "body",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=11,
        leading=16.5,
        textColor=BODY_TEXT,
        alignment=TA_JUSTIFY,
        spaceAfter=3 * mm,
    )

    styles["reference_item"] = ParagraphStyle(
        "reference_item",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=MUTED_TEXT,
        leftIndent=5 * mm,
        spaceAfter=1.5 * mm,
    )

    styles["footer"] = ParagraphStyle(
        "footer",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=MUTED_TEXT,
        alignment=TA_CENTER,
    )

    styles["reading_time"] = ParagraphStyle(
        "reading_time",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=ACCENT_CYAN,
        spaceAfter=4 * mm,
    )

    return styles


# ============================================
# Helper: Sanitize text for ReportLab
# ============================================

def _sanitize(text: str) -> str:
    """
    Sanitizes text for safe use in ReportLab Paragraph objects.

    ReportLab's Paragraph uses a subset of HTML for formatting.
    Raw text containing &, <, or > will break the XML parser.
    We must escape these characters.

    Also strips markdown bold markers (**text**) since ReportLab
    uses <b>text</b> instead.

    Args:
        text: Raw text to sanitize

    Returns:
        Escaped text safe for ReportLab
    """
    if not text:
        return ""

    # Escape XML special characters (order matters: & must be first)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    # Convert markdown bold to ReportLab bold
    # **text** → <b>text</b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    return text


# ============================================
# Helper: Estimate reading time
# ============================================

def _estimate_reading_time(article: MagazineArticle) -> int:
    """Returns estimated reading time in minutes (200 WPM)."""
    total_words = 0
    for field in [
        article.executive_summary,
        article.background,
        article.technical_analysis,
        article.impact,
        article.recommendations,
        article.references,
    ]:
        if field:
            total_words += len(field.split())
    minutes = max(1, round(total_words / 200))
    return minutes


# ============================================
# Section separator
# ============================================

def _section_separator():
    """Returns a styled horizontal rule for section breaks."""
    return HRFlowable(
        width="100%",
        thickness=0.5,
        color=SEPARATOR_COLOR,
        spaceBefore=2 * mm,
        spaceAfter=2 * mm,
    )


# ============================================
# Page Number & Header/Footer Callbacks
# ============================================

_current_issue_number = 1  # Set before building


def _add_page_header_footer(canvas, doc):
    """
    Draws the running header, page number, and footer on content pages.
    """
    page_num = doc.page

    canvas.saveState()

    # --- Running Header ---
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED_TEXT)
    canvas.drawString(
        LEFT_MARGIN,
        PAGE_HEIGHT - 15 * mm,
        f"CyberQuill  •  Issue #{_current_issue_number:03d}",
    )
    # Thin line below header
    canvas.setStrokeColor(LIGHT_GREY)
    canvas.setLineWidth(0.5)
    canvas.line(
        LEFT_MARGIN,
        PAGE_HEIGHT - 17 * mm,
        PAGE_WIDTH - RIGHT_MARGIN,
        PAGE_HEIGHT - 17 * mm,
    )

    # --- Footer ---
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED_TEXT)
    # Left: "Generated by CyberQuill"
    canvas.drawString(
        LEFT_MARGIN,
        BOTTOM_MARGIN - 14 * mm,
        "Generated by CyberQuill",
    )
    # Right: Page number
    canvas.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        BOTTOM_MARGIN - 14 * mm,
        f"Page {page_num}",
    )
    # Thin line above footer
    canvas.setStrokeColor(LIGHT_GREY)
    canvas.setLineWidth(0.5)
    canvas.line(
        LEFT_MARGIN,
        BOTTOM_MARGIN - 10 * mm,
        PAGE_WIDTH - RIGHT_MARGIN,
        BOTTOM_MARGIN - 10 * mm,
    )

    canvas.restoreState()


def _cover_page_background(canvas, doc):
    """
    Draws a professional dark background for the cover page.
    """
    canvas.saveState()

    # Full-page dark background
    canvas.setFillColor(COVER_BG)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    # Top accent bar
    canvas.setFillColor(ACCENT_CYAN)
    canvas.rect(0, PAGE_HEIGHT - 6 * mm, PAGE_WIDTH, 6 * mm, fill=1, stroke=0)

    # Bottom accent line
    canvas.setStrokeColor(ACCENT_CYAN)
    canvas.setLineWidth(1)
    canvas.line(
        LEFT_MARGIN + 40 * mm,
        45 * mm,
        PAGE_WIDTH - RIGHT_MARGIN - 40 * mm,
        45 * mm,
    )

    # Decorative side lines
    canvas.setStrokeColor(colors.HexColor("#1e293b"))
    canvas.setLineWidth(0.5)
    canvas.line(LEFT_MARGIN, 60 * mm, LEFT_MARGIN, PAGE_HEIGHT - 20 * mm)
    canvas.line(
        PAGE_WIDTH - RIGHT_MARGIN,
        60 * mm,
        PAGE_WIDTH - RIGHT_MARGIN,
        PAGE_HEIGHT - 20 * mm,
    )

    canvas.restoreState()


# ============================================
# Build: Cover Page
# ============================================

def _build_cover(
    articles: list[MagazineArticle],
    styles: dict[str, ParagraphStyle],
    issue_number: int,
) -> list:
    """
    Builds the cover page elements.

    The cover includes:
        - Magazine title: "CyberQuill"
        - Subtitle: "Cybersecurity Intelligence & Magazine"
        - Issue number and publication date
        - Article count and category summary
    """
    elements = []

    # Push content down
    elements.append(Spacer(1, 55 * mm))

    # Magazine title
    elements.append(Paragraph("CyberQuill", styles["cover_title"]))

    # Subtitle
    elements.append(
        Paragraph(
            "Cybersecurity Intelligence &amp; Magazine",
            styles["cover_subtitle"],
        )
    )

    # Horizontal separator (built via spacer + the canvas background line)
    elements.append(Spacer(1, 8 * mm))

    # Issue number
    elements.append(
        Paragraph(
            f"Issue #{issue_number:03d}",
            styles["cover_issue"],
        )
    )

    # Date
    date_str = datetime.now().strftime("%B %Y")
    elements.append(Paragraph(date_str, styles["cover_date"]))

    # Stats summary
    elements.append(Spacer(1, 5 * mm))
    elements.append(
        Paragraph(
            f"<b>{len(articles)}</b> Articles in This Issue",
            styles["cover_stats"],
        )
    )

    # Category breakdown
    categories: dict[str, int] = {}
    for article in articles:
        cat = article.category or "Uncategorized"
        categories[cat] = categories.get(cat, 0) + 1

    if categories:
        cat_summary = " &bull; ".join(
            f"{cat}: {count}" for cat, count in sorted(categories.items())
        )
        elements.append(Paragraph(cat_summary, styles["cover_stats"]))

    # Total reading time
    total_time = sum(_estimate_reading_time(a) for a in articles)
    elements.append(Spacer(1, 5 * mm))
    elements.append(
        Paragraph(
            f"Estimated Reading Time: {total_time} minutes",
            styles["cover_stats"],
        )
    )

    # Push to next page
    elements.append(PageBreak())

    return elements


# ============================================
# Build: Table of Contents
# ============================================

def _build_toc(
    articles: list[MagazineArticle],
    styles: dict[str, ParagraphStyle],
) -> list:
    """
    Builds a table of contents page.

    Lists all articles grouped visually. Each entry shows:
        - Article title
        - Category label
        - Reading time
    """
    elements = []

    elements.append(Paragraph("Contents", styles["toc_heading"]))
    elements.append(_section_separator())
    elements.append(Spacer(1, 4 * mm))

    for i, article in enumerate(articles, 1):
        title = _sanitize(article.title)
        category = _sanitize(article.category or "Uncategorized")
        read_time = _estimate_reading_time(article)

        elements.append(
            Paragraph(f"{i}. {title}", styles["toc_entry"])
        )
        elements.append(
            Paragraph(
                f"{category}  &bull;  {read_time} min read",
                styles["toc_category"],
            )
        )

    elements.append(PageBreak())

    return elements


# ============================================
# Build: Article Pages
# ============================================

def _build_article(
    article: MagazineArticle,
    styles: dict[str, ParagraphStyle],
) -> list:
    """
    Builds the page elements for a single magazine article.

    Renders all 6 sections of the article:
        1. Title
        2. Executive Summary
        3. Background
        4. Technical Analysis
        5. Impact Assessment
        6. Recommendations
        7. References

    Each section gets a styled heading followed by body text.
    """
    elements = []

    # Article title
    elements.append(
        Paragraph(_sanitize(article.title), styles["article_title"])
    )

    # Article metadata: category + reading time
    read_time = _estimate_reading_time(article)
    meta_parts = []
    if article.category:
        meta_parts.append(f"{_sanitize(article.category)}")
    meta_parts.append(f"{read_time} min read")
    meta_parts.append(datetime.now().strftime("%B %d, %Y"))

    elements.append(
        Paragraph(
            "  |  ".join(meta_parts),
            styles["article_meta"],
        )
    )

    # Section separator after meta
    elements.append(_section_separator())

    # Section definitions: (heading_text, content, style_key)
    sections = [
        ("Executive Summary", article.executive_summary, "body"),
        ("Background", article.background, "body"),
        ("Technical Analysis", article.technical_analysis, "body"),
        ("Impact Assessment", article.impact, "body"),
        ("Recommendations", article.recommendations, "body"),
        ("References", article.references, "reference_item"),
    ]

    for heading, content, style_key in sections:
        if not content or not content.strip():
            continue

        # Section heading
        elements.append(
            Paragraph(heading, styles["section_heading"])
        )

        # Render content — handle multi-line/bullet content
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            elements.append(
                Paragraph(_sanitize(line), styles[style_key])
            )

        # Section separator
        elements.append(_section_separator())

    # Original source link
    if article.original_link:
        elements.append(Spacer(1, 2 * mm))
        elements.append(
            Paragraph(
                f"Original Source: {_sanitize(article.original_link)}",
                styles["reference_item"],
            )
        )

    # Page break between articles
    elements.append(PageBreak())

    return elements


# ============================================
# Main: Generate PDF
# ============================================

def generate_pdf(
    articles: list[MagazineArticle],
    output_filename: str | None = None,
    issue_number: int | None = None,
) -> str | None:
    """
    Generates a complete magazine PDF from a list of articles.

    This is the main entry point for the PDF Generator.

    How it works:
        1. Sanitizes all articles (removes RAG artifacts)
        2. Ensures the output directory exists
        3. Creates a ReportLab document with two page templates:
           - "cover" template (with dark background)
           - "content" template (with headers, footers, page numbers)
        4. Builds cover page, table of contents, and all articles
        5. Saves the PDF to disk

    Args:
        articles: List of MagazineArticle objects to include
        output_filename: Optional filename for the PDF.
                         Defaults to "cyberquill_YYYYMMDD_HHMMSS.pdf"
        issue_number: Optional issue number. If None, auto-generated.

    Returns:
        The absolute file path of the generated PDF, or None if
        no articles were provided.

    Example:
        >>> from pdf.generator import generate_pdf
        >>> path = generate_pdf(magazine_articles)
        >>> print(f"PDF saved to: {path}")
    """
    if not articles:
        logger.info("No articles to generate PDF for")
        return None

    logger.info(f"Generating PDF for {len(articles)} articles...")

    # ---- Sanitize all articles (strip RAG artifacts) ----
    sanitized_articles = [sanitize_article(a) for a in articles]

    # ---- Issue numbering ----
    global _current_issue_number
    if issue_number is not None:
        _current_issue_number = issue_number
    else:
        try:
            from utils.issue_tracker import get_next_issue_number
            _current_issue_number = get_next_issue_number()
        except Exception:
            _current_issue_number = 1

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate filename
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"cyberquill_issue{_current_issue_number:03d}_{timestamp}.pdf"

    output_path = OUTPUT_DIR / output_filename

    # Get styles
    styles = _get_styles()

    # ---- Create document with page templates ----
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="CyberQuill — Cybersecurity Intelligence & Magazine",
        author="CyberQuill",
    )

    # Define the usable frame for content
    content_frame = Frame(
        LEFT_MARGIN,
        BOTTOM_MARGIN,
        PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN,
        PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN,
        id="content_frame",
    )

    # Cover page template (with dark background, no page number)
    cover_template = PageTemplate(
        id="cover",
        frames=[content_frame],
        onPage=_cover_page_background,
    )

    # Content page template (with headers, footers, page numbers)
    content_template = PageTemplate(
        id="content",
        frames=[content_frame],
        onPage=_add_page_header_footer,
    )

    doc.addPageTemplates([cover_template, content_template])

    # ---- Build all elements ----
    elements = []

    # Cover page (uses "cover" template — the first template is used by default)
    elements.extend(_build_cover(sanitized_articles, styles, _current_issue_number))

    # Switch to content template for remaining pages
    elements.append(NextPageTemplate("content"))

    # Table of contents
    elements.extend(_build_toc(sanitized_articles, styles))

    # Each article
    for article in sanitized_articles:
        elements.extend(_build_article(article, styles))

    # ---- Build the PDF ----
    doc.build(elements)

    abs_path = str(output_path.resolve())
    logger.info(f"PDF generated successfully: {abs_path}")

    # Record in issue history
    try:
        from utils.issue_tracker import record_issue
        categories = {}
        for a in sanitized_articles:
            cat = a.category or "Uncategorized"
            categories[cat] = categories.get(cat, 0) + 1
        record_issue(
            issue_number=_current_issue_number,
            article_count=len(sanitized_articles),
            pdf_path=abs_path,
            categories=categories,
        )
    except Exception as e:
        logger.warning(f"Failed to record issue history: {e}")

    return abs_path


# ============================================
# LangGraph Node Function
# ============================================

def pdf_node(state: dict) -> dict:
    """
    LangGraph node function for the PDF Generator.

    Reads magazine_articles and review_results from state.
    Generates a PDF containing only approved articles.

    If no articles were approved, generates a PDF with all articles
    anyway (with a warning) so the user still gets output.

    Args:
        state: The current pipeline state dictionary

    Returns:
        Dictionary with state updates:
        - "pdf_path": path to the generated PDF file
        - "current_stage": updated to "pdf_complete"
    """
    logger.info("PDF Generator starting...")

    magazine_articles = state.get("magazine_articles", [])
    review_results = state.get("review_results", [])

    # Filter to approved articles only (if we have review results)
    if review_results and len(review_results) == len(magazine_articles):
        approved_articles = [
            article
            for article, review in zip(magazine_articles, review_results)
            if review.approved
        ]

        if approved_articles:
            logger.info(
                f"Generating PDF with {len(approved_articles)} approved articles "
                f"(out of {len(magazine_articles)} total)"
            )
            pdf_path = generate_pdf(approved_articles)
        else:
            # No articles approved — generate with all anyway
            logger.warning(
                "No articles were approved. Generating PDF with all articles."
            )
            pdf_path = generate_pdf(magazine_articles)
    else:
        # No review results — use all articles
        pdf_path = generate_pdf(magazine_articles)

    logger.info(f"PDF Generator finished. Output: {pdf_path}")

    return {
        "pdf_path": pdf_path,
        "current_stage": "pdf_complete",
    }
