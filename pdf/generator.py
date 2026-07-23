"""
CyberQuill PDF Generator
==========================

Purpose:
    Generates a professional magazine-style PDF from reviewed articles.
    Takes a list of MagazineArticle objects and produces a downloadable
    PDF file called "CyberQuill Weekly".

How it works:
    1. Creates a cover page with magazine title, date, and article count
    2. Adds a table of contents listing all articles by category
    3. Renders each article with all 6 sections, styled with headers,
       body text, and bullet points
    4. Adds page numbers to every page (except the cover)

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
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
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
)

from models.schemas import MagazineArticle
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================
# Constants
# ============================================

# Output directory for generated PDFs
OUTPUT_DIR = Path("data/output")

# Page dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.27 x 841.89 points

# Margins
LEFT_MARGIN = 2 * cm
RIGHT_MARGIN = 2 * cm
TOP_MARGIN = 2.5 * cm
BOTTOM_MARGIN = 2.5 * cm

# Colours (professional, muted palette)
DARK_BLUE = colors.HexColor("#1a237e")
MEDIUM_BLUE = colors.HexColor("#283593")
ACCENT_BLUE = colors.HexColor("#42a5f5")
DARK_GREY = colors.HexColor("#333333")
MEDIUM_GREY = colors.HexColor("#666666")
LIGHT_GREY = colors.HexColor("#eeeeee")
WHITE = colors.white


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
        fontSize=36,
        leading=42,
        textColor=DARK_BLUE,
        alignment=TA_CENTER,
        spaceAfter=10 * mm,
    )

    styles["cover_subtitle"] = ParagraphStyle(
        "cover_subtitle",
        parent=base["Normal"],
        fontSize=16,
        leading=20,
        textColor=MEDIUM_BLUE,
        alignment=TA_CENTER,
        spaceAfter=5 * mm,
    )

    styles["cover_date"] = ParagraphStyle(
        "cover_date",
        parent=base["Normal"],
        fontSize=12,
        leading=16,
        textColor=MEDIUM_GREY,
        alignment=TA_CENTER,
        spaceAfter=15 * mm,
    )

    styles["cover_stats"] = ParagraphStyle(
        "cover_stats",
        parent=base["Normal"],
        fontSize=11,
        leading=15,
        textColor=DARK_GREY,
        alignment=TA_CENTER,
        spaceAfter=3 * mm,
    )

    # ---- Table of Contents Styles ----
    styles["toc_heading"] = ParagraphStyle(
        "toc_heading",
        parent=base["Heading1"],
        fontSize=22,
        leading=28,
        textColor=DARK_BLUE,
        spaceAfter=8 * mm,
    )

    styles["toc_entry"] = ParagraphStyle(
        "toc_entry",
        parent=base["Normal"],
        fontSize=11,
        leading=16,
        textColor=DARK_GREY,
        leftIndent=5 * mm,
        spaceAfter=2 * mm,
    )

    styles["toc_category"] = ParagraphStyle(
        "toc_category",
        parent=base["Normal"],
        fontSize=9,
        leading=12,
        textColor=MEDIUM_GREY,
        leftIndent=5 * mm,
    )

    # ---- Article Styles ----
    styles["article_title"] = ParagraphStyle(
        "article_title",
        parent=base["Heading1"],
        fontSize=20,
        leading=26,
        textColor=DARK_BLUE,
        spaceAfter=4 * mm,
    )

    styles["article_category"] = ParagraphStyle(
        "article_category",
        parent=base["Normal"],
        fontSize=9,
        leading=12,
        textColor=ACCENT_BLUE,
        spaceBefore=0,
        spaceAfter=6 * mm,
    )

    styles["section_heading"] = ParagraphStyle(
        "section_heading",
        parent=base["Heading2"],
        fontSize=14,
        leading=18,
        textColor=MEDIUM_BLUE,
        spaceBefore=6 * mm,
        spaceAfter=3 * mm,
    )

    styles["body"] = ParagraphStyle(
        "body",
        parent=base["Normal"],
        fontSize=10,
        leading=15,
        textColor=DARK_GREY,
        alignment=TA_JUSTIFY,
        spaceAfter=3 * mm,
    )

    styles["reference_item"] = ParagraphStyle(
        "reference_item",
        parent=base["Normal"],
        fontSize=9,
        leading=13,
        textColor=MEDIUM_GREY,
        leftIndent=5 * mm,
        spaceAfter=1.5 * mm,
    )

    styles["footer"] = ParagraphStyle(
        "footer",
        parent=base["Normal"],
        fontSize=8,
        textColor=MEDIUM_GREY,
        alignment=TA_CENTER,
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
    import re
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    return text


# ============================================
# Page Number Footer Callback
# ============================================

def _add_page_number(canvas, doc):
    """
    Draws the page number at the bottom of each page.

    This is a callback function used by ReportLab's BaseDocTemplate.
    It's called automatically for every page that uses the "content"
    PageTemplate.

    Args:
        canvas: The ReportLab canvas to draw on
        doc: The document being built
    """
    page_num = doc.page
    text = f"CyberQuill Weekly  •  Page {page_num}"
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MEDIUM_GREY)
    canvas.drawCentredString(PAGE_WIDTH / 2, BOTTOM_MARGIN - 10 * mm, text)
    canvas.restoreState()


def _cover_page_background(canvas, doc):
    """
    Draws a clean background for the cover page.

    Adds a subtle top colour bar and a divider line to give the
    cover a professional, magazine-style appearance.

    Args:
        canvas: The ReportLab canvas to draw on
        doc: The document being built
    """
    canvas.saveState()

    # Top accent bar
    canvas.setFillColor(DARK_BLUE)
    canvas.rect(0, PAGE_HEIGHT - 15 * mm, PAGE_WIDTH, 15 * mm, fill=1, stroke=0)

    # Thin accent line below the bar
    canvas.setStrokeColor(ACCENT_BLUE)
    canvas.setLineWidth(2)
    canvas.line(
        LEFT_MARGIN, PAGE_HEIGHT - 17 * mm,
        PAGE_WIDTH - RIGHT_MARGIN, PAGE_HEIGHT - 17 * mm,
    )

    canvas.restoreState()


# ============================================
# Build: Cover Page
# ============================================

def _build_cover(
    articles: list[MagazineArticle],
    styles: dict[str, ParagraphStyle],
) -> list:
    """
    Builds the cover page elements.

    The cover includes:
        - Magazine title: "CyberQuill Weekly"
        - Tagline: "AI-Powered Cybersecurity Intelligence"
        - Current date
        - Article count and category summary

    Args:
        articles: List of articles to summarise on the cover
        styles: Paragraph styles dictionary

    Returns:
        List of Flowable objects for the cover page
    """
    elements = []

    # Push content down from the top accent bar
    elements.append(Spacer(1, 30 * mm))

    # Magazine title
    elements.append(Paragraph("CyberQuill Weekly", styles["cover_title"]))

    # Tagline
    elements.append(
        Paragraph(
            "AI-Powered Cybersecurity Intelligence",
            styles["cover_subtitle"],
        )
    )

    # Date
    date_str = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(date_str, styles["cover_date"]))

    # Divider spacer
    elements.append(Spacer(1, 10 * mm))

    # Stats summary
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

    Note: We don't include page numbers here because ReportLab's
    SimpleDocTemplate doesn't easily support forward-referencing
    page numbers. The TOC serves as an overview, not a precise index.

    Args:
        articles: List of articles
        styles: Paragraph styles dictionary

    Returns:
        List of Flowable objects for the TOC page
    """
    elements = []

    elements.append(Paragraph("Table of Contents", styles["toc_heading"]))

    for i, article in enumerate(articles, 1):
        title = _sanitize(article.title)
        category = _sanitize(article.category or "Uncategorized")

        elements.append(
            Paragraph(f"{i}. {title}", styles["toc_entry"])
        )
        elements.append(
            Paragraph(f"Category: {category}", styles["toc_category"])
        )
        elements.append(Spacer(1, 2 * mm))

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
        5. Impact
        6. Recommendations
        7. References

    Each section gets a styled heading followed by body text.
    Bullet points in recommendations and references are handled
    by splitting on newlines.

    Args:
        article: A MagazineArticle to render
        styles: Paragraph styles dictionary

    Returns:
        List of Flowable objects for this article
    """
    elements = []

    # Article title
    elements.append(
        Paragraph(_sanitize(article.title), styles["article_title"])
    )

    # Category badge
    if article.category:
        elements.append(
            Paragraph(
                f"Category: {_sanitize(article.category)}",
                styles["article_category"],
            )
        )

    # Section definitions: (heading_text, content, style_key)
    sections = [
        ("Executive Summary", article.executive_summary, "body"),
        ("Background", article.background, "body"),
        ("Technical Analysis", article.technical_analysis, "body"),
        ("Impact", article.impact, "body"),
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

    # Original source link
    if article.original_link:
        elements.append(Spacer(1, 3 * mm))
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
) -> str | None:
    """
    Generates a complete magazine PDF from a list of articles.

    This is the main entry point for the PDF Generator.

    How it works:
        1. Ensures the output directory exists
        2. Creates a ReportLab document with two page templates:
           - "cover" template (with accent bar background)
           - "content" template (with page numbers)
        3. Builds cover page, table of contents, and all articles
        4. Saves the PDF to disk

    Args:
        articles: List of MagazineArticle objects to include
        output_filename: Optional filename for the PDF.
                         Defaults to "cyberquill_YYYYMMDD_HHMMSS.pdf"

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

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate filename
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"cyberquill_{timestamp}.pdf"

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
        title="CyberQuill Weekly",
        author="CyberQuill AI",
    )

    # Define the usable frame for content
    content_frame = Frame(
        LEFT_MARGIN,
        BOTTOM_MARGIN,
        PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN,
        PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN,
        id="content_frame",
    )

    # Cover page template (with background graphics, no page number)
    cover_template = PageTemplate(
        id="cover",
        frames=[content_frame],
        onPage=_cover_page_background,
    )

    # Content page template (with page numbers)
    content_template = PageTemplate(
        id="content",
        frames=[content_frame],
        onPage=_add_page_number,
    )

    doc.addPageTemplates([cover_template, content_template])

    # ---- Build all elements ----
    elements = []

    # Cover page (uses "cover" template — the first template is used by default)
    elements.extend(_build_cover(articles, styles))

    # Switch to content template for remaining pages
    elements.append(NextPageTemplate("content"))

    # Table of contents
    elements.extend(_build_toc(articles, styles))

    # Each article
    for article in articles:
        elements.extend(_build_article(article, styles))

    # ---- Build the PDF ----
    doc.build(elements)

    abs_path = str(output_path.resolve())
    logger.info(f"PDF generated successfully: {abs_path}")

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
