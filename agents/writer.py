"""
CyberQuill Writer Agent

Purpose:
    Transforms enriched articles into professional magazine-style articles.
    Takes the article data + RAG context and generates a well-structured
    cybersecurity article suitable for "CyberQuill Weekly" magazine.

How it works:
    Mode 1: LLM-based (primary)
        - Sends article data + RAG context to Groq LLM
        - LLM generates a full article with all 6 sections
        - Parses the response into MagazineArticle fields
        - High quality, but requires API key and credits

    Mode 2: Template-based (fallback)
        - Uses string templates to structure article content
        - Fills in sections from the original article data
        - Lower quality but always works (no API needed)
        - Useful for testing, demos, and when API credits run out

    Why have a fallback?
        Same reason as the Classification Agent — graceful degradation.
        During a viva demo, you don't want the system to crash because
        the Groq API is slow or your credits ran out.

Inputs:
    - List[EnrichedArticle] — articles with RAG context

Outputs:
    - List[MagazineArticle] — professional magazine articles

Dependencies:
    - langchain-groq: LLM calls
    - config.settings: API keys, model configuration
    - config.prompts: Writer prompt template
    - models.schemas: EnrichedArticle, MagazineArticle
    - utils.logger: Logging

Agentic AI Design Pattern:
    **Generator Pattern** — This agent generates new content based on
    input data and context. It's the core "creative" agent in the pipeline.

Testing strategy:
    - Test template-based writing (no API needed)
    - Test LLM response parsing
    - Test handling of missing fields
    - Test batch writing
    - Edge cases (empty context, empty summary)

Possible improvements:
    - Add style customization (formal, casual, technical)
    - Support different article lengths (brief, standard, deep-dive)
    - Add fact-checking against RAG context
    - Generate article images using AI
"""

import re

from config.prompts import WRITER_PROMPT, WRITER_REVISION_PROMPT
from config.settings import settings
from models.schemas import EnrichedArticle, MagazineArticle, ReviewResult
from utils.logger import get_logger

logger = get_logger(__name__)

RAG_CONTEXT_MAX_CHARS = 3000


def _write_by_template(article: EnrichedArticle) -> MagazineArticle:
    """
    Generates a magazine article using string templates (fallback method).

    How it works:
        Takes the original article fields and wraps them in a structured
        magazine article format. Adds headings, structure, and fills in
        the RAG context as background information.

    Why is this useful?
        - Works without any API
        - Generates consistent, predictable output
        - Great for testing the downstream pipeline (Reviewer, PDF)
        - During viva, you can demo the full pipeline without API costs

    Args:
        article: An EnrichedArticle with category and RAG context

    Returns:
        A MagazineArticle with all sections populated
    """
    # Generate a magazine-style title from the original
    title = f"Analysis: {article.title}"

    # Executive summary from the original article summary
    executive_summary = (
        article.summary
        if article.summary
        else f"This article covers a recent cybersecurity event related to "
             f"{article.category.lower()}."
    )

    # Background section from RAG context
    if article.rag_context:
        context_text = article.rag_context[:RAG_CONTEXT_MAX_CHARS]
        background = (
            f"According to cybersecurity frameworks and knowledge bases, "
            f"this type of threat is well-documented:\n\n"
            f"{context_text}"
        )
    else:
        background = (
            f"This incident falls under the {article.category} category. "
            f"Threats in this category have been increasing in frequency "
            f"and sophistication over the past year."
        )

    # Technical analysis (structured from available data)
    technical_analysis = (
        f"The reported incident involves {article.category.lower()} "
        f"activity as described in the original source ({article.source}). "
        f"The article was originally published on {article.published or 'an unspecified date'}."
    )
    if article.summary:
        technical_analysis += (
            f"\n\nKey details from the source: {article.summary}"
        )

    # Impact assessment
    impact = (
        f"Organizations in affected sectors should assess their exposure "
        f"to this type of {article.category.lower()} threat. "
        f"The impact may include data loss, service disruption, "
        f"financial damage, and reputational harm."
    )

    # Recommendations
    recommendations = (
        f"1. Review and update incident response plans\n"
        f"2. Apply relevant security patches immediately\n"
        f"3. Monitor systems for indicators of compromise (IOCs)\n"
        f"4. Ensure multi-factor authentication is enabled\n"
        f"5. Conduct a security awareness training session"
    )

    # References
    rag_refs = ""
    if article.rag_sources:
        rag_refs = "\n".join(
            f"- {source}" for source in article.rag_sources
        )
    references = (
        f"- Original Source: [{article.source}]({article.link})\n"
        f"{rag_refs}"
    )

    return MagazineArticle(
        title=title,
        executive_summary=executive_summary,
        background=background,
        technical_analysis=technical_analysis,
        impact=impact,
        recommendations=recommendations,
        references=references,
        original_link=article.link,
        category=article.category,
    )


def _parse_llm_sections(text: str) -> dict[str, str]:
    """
    Parses the LLM's markdown response into individual sections.

    The LLM returns a markdown-formatted article with headings like:
        ## Executive Summary
        ... content ...
        ## Background
        ... content ...

    This function extracts each section by finding headings and
    capturing the text between them.

    Why parse instead of using structured output?
        - Structured output (JSON mode) often produces lower quality text
        - Markdown is the LLM's natural writing format
        - Parsing markdown headings is simple and reliable
        - The LLM writes better articles when it can use natural formatting

    Args:
        text: The full markdown text from the LLM

    Returns:
        Dict mapping section names to their content
        e.g., {"Executive Summary": "...", "Background": "..."}
    """
    sections = {}

    # Pattern: Match ## Heading or **Heading** at the start of a line
    # This handles both "## Executive Summary" and "**Executive Summary**"
    pattern = r"(?:^|\n)(?:#{1,3}\s*\**|(?:\*\*))(.+?)(?:\**)\s*\n([\s\S]*?)(?=\n(?:#{1,3}\s*\**|(?:\*\*))|\Z)"
    matches = re.findall(pattern, text, re.MULTILINE)

    for heading, content in matches:
        # Clean up heading text
        clean_heading = heading.strip().strip("*#: ").strip()
        clean_content = content.strip()
        if clean_heading and clean_content:
            sections[clean_heading] = clean_content

    return sections


def _extract_section(sections: dict[str, str], *keywords: str) -> str:
    """
    Finds a section by matching against multiple possible heading names.

    LLMs are unpredictable with exact headings. They might write:
        - "Executive Summary" or "Summary" or "Overview"
        - "Technical Analysis" or "Analysis" or "Technical Details"

    This function checks all provided keywords against all section headings
    and returns the first match.

    Args:
        sections: Dict of {heading: content} from _parse_llm_sections
        *keywords: Variable number of heading keywords to search for

    Returns:
        The content of the matching section, or "" if not found
    """
    for key, value in sections.items():
        key_lower = key.lower()
        for keyword in keywords:
            if keyword.lower() in key_lower:
                return value
    return ""


def _magazine_to_text(article: MagazineArticle) -> str:
    """Formats a MagazineArticle as markdown for revision prompts."""
    return (
        f"# {article.title}\n\n"
        f"## Executive Summary\n{article.executive_summary}\n\n"
        f"## Background\n{article.background}\n\n"
        f"## Technical Analysis\n{article.technical_analysis}\n\n"
        f"## Impact\n{article.impact}\n\n"
        f"## Recommendations\n{article.recommendations}\n\n"
        f"## References\n{article.references}"
    )


def _build_magazine_from_sections(
    sections: dict[str, str],
    raw_text: str,
    article: EnrichedArticle,
    fallback_title: str = "",
) -> MagazineArticle:
    """Builds a MagazineArticle from parsed LLM section dict."""
    generated_title = _extract_section(sections, "title")
    if not generated_title:
        first_line = raw_text.split("\n")[0].strip("# *")
        generated_title = (
            first_line if len(first_line) < 200 else (fallback_title or article.title)
        )

    return MagazineArticle(
        title=generated_title or article.title,
        executive_summary=_extract_section(
            sections, "executive summary", "summary", "overview"
        ),
        background=_extract_section(
            sections, "background", "context", "history"
        ),
        technical_analysis=_extract_section(
            sections, "technical analysis", "analysis", "technical", "details"
        ),
        impact=_extract_section(
            sections, "impact", "affected", "consequences", "impact assessment"
        ),
        recommendations=_extract_section(
            sections, "recommendations", "mitigation", "remediation", "action"
        ),
        references=_extract_section(
            sections, "references", "sources", "further reading"
        ),
        original_link=article.link,
        category=article.category,
    )


def _write_revision_by_llm(
    article: EnrichedArticle,
    previous_article: MagazineArticle,
    review_result: ReviewResult,
) -> MagazineArticle:
    """Revises a magazine article using LLM with review feedback and RAG context."""
    from langchain_groq import ChatGroq

    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=0.5,
        max_tokens=2500,
    )

    all_issues = review_result.issues + review_result.rag_issues
    issues_text = "\n".join(f"- {issue}" for issue in all_issues) or "Improve overall quality."

    rag_context = (article.rag_context or "No additional context available.")[
        :RAG_CONTEXT_MAX_CHARS
    ]

    prompt = WRITER_REVISION_PROMPT.format(
        title=article.title,
        summary=article.summary,
        source=article.source,
        rag_context=rag_context,
        previous_article=_magazine_to_text(previous_article),
        review_issues=issues_text,
    )

    response = llm.invoke(prompt)
    raw_text = response.content.strip()
    sections = _parse_llm_sections(raw_text)

    return _build_magazine_from_sections(
        sections, raw_text, article, fallback_title=previous_article.title
    )


def _write_by_llm(article: EnrichedArticle) -> MagazineArticle:
    """
    Generates a magazine article using the Groq LLM (primary method).

    How it works:
        1. Formats the WRITER_PROMPT with article data
        2. Sends to Groq LLM for generation
        3. Parses the markdown response into sections
        4. Creates a MagazineArticle from the parsed sections

    Args:
        article: An EnrichedArticle with category and RAG context

    Returns:
        A MagazineArticle generated by the LLM

    Raises:
        Exception: If the API call fails (caught by the caller)
    """
    from langchain_groq import ChatGroq

    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=0.7,  # Some creativity for writing
        max_tokens=2000,  # Enough for a full article
    )

    # Format the prompt
    prompt = WRITER_PROMPT.format(
        title=article.title,
        summary=article.summary,
        source=article.source,
        rag_context=(article.rag_context or "No additional context available.")[
            :RAG_CONTEXT_MAX_CHARS
        ],
    )

    # Call the LLM
    response = llm.invoke(prompt)
    raw_text = response.content.strip()

    logger.debug(f"LLM writer response length: {len(raw_text)} chars")

    # Parse the response into sections
    sections = _parse_llm_sections(raw_text)

    return _build_magazine_from_sections(sections, raw_text, article)


def write_article(
    article: EnrichedArticle,
    previous_article: MagazineArticle | None = None,
    review_result: ReviewResult | None = None,
) -> MagazineArticle:
    """
    Writes a magazine article from an enriched article.

    When previous_article and review_result are provided, performs a
    revision pass using editorial feedback and RAG context.
    """
    is_revision = previous_article is not None and review_result is not None

    if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here":
        try:
            if is_revision:
                result = _write_revision_by_llm(article, previous_article, review_result)
                logger.debug(f"LLM revised article: '{result.title[:50]}...'")
            else:
                result = _write_by_llm(article)
                logger.debug(f"LLM wrote article: '{result.title[:50]}...'")
            return result
        except Exception as e:
            logger.warning(f"LLM writing failed: {e}. Using template fallback.")

    result = _write_by_template(article)
    logger.debug(f"Template wrote article: '{result.title[:50]}...'")
    return result


def write_articles(
    articles: list[EnrichedArticle],
    previous_articles: list[MagazineArticle] | None = None,
    review_results: list[ReviewResult] | None = None,
) -> list[MagazineArticle]:
    """
    Writes magazine articles for a list of enriched articles.

    This is the main entry point for the Writer Agent.

    Args:
        articles: List of EnrichedArticle objects

    Returns:
        List of MagazineArticle objects

    Example:
        >>> from agents.writer import write_articles
        >>> magazine = write_articles(enriched_articles)
        >>> for a in magazine:
        ...     print(f"[{a.category}] {a.title}")
    """
    if not articles:
        logger.info("No articles to write")
        return []

    logger.info(f"Writing {len(articles)} magazine articles...")

    # Determine method
    using_llm = (
        settings.GROQ_API_KEY
        and settings.GROQ_API_KEY != "your_groq_api_key_here"
    )
    method = "LLM (Groq)" if using_llm else "template (fallback)"
    logger.info(f"Writing method: {method}")

    magazine_articles = []
    for i, article in enumerate(articles):
        prev = previous_articles[i] if previous_articles and i < len(previous_articles) else None
        review = review_results[i] if review_results and i < len(review_results) else None
        mag_article = write_article(article, previous_article=prev, review_result=review)
        magazine_articles.append(mag_article)

    logger.info(
        f"Writing complete. Generated {len(magazine_articles)} "
        f"magazine articles."
    )

    return magazine_articles


# ============================================
# LangGraph Node Function
# ============================================

def writer_node(state: dict) -> dict:
    """
    LangGraph node function for the Writer Agent.

    Reads enriched_articles from state, generates magazine articles,
    and writes magazine_articles back to state.

    Args:
        state: The current pipeline state dictionary

    Returns:
        Dictionary with state updates:
        - "magazine_articles": list of MagazineArticle objects
        - "current_stage": updated to "writing_complete"
    """
    logger.info("Writer Agent starting...")

    enriched_articles = state.get("enriched_articles", [])
    revision_count = state.get("revision_count", 0)
    review_results = state.get("review_results", [])
    previous_articles = state.get("magazine_articles", [])

    is_revision = revision_count > 0 and review_results and previous_articles

    if is_revision:
        logger.info(f"Revision cycle {revision_count}: revising articles with review feedback.")
        magazine_articles = write_articles(
            enriched_articles,
            previous_articles=previous_articles,
            review_results=review_results,
        )
    else:
        magazine_articles = write_articles(enriched_articles)

    logger.info(
        f"Writer Agent finished. Generated {len(magazine_articles)} articles."
    )

    return {
        "magazine_articles": magazine_articles,
        "current_stage": "writing_complete",
    }
