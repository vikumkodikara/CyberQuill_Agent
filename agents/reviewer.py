"""
CyberQuill Reviewer Agent
============================

Purpose:
    Reviews magazine articles for quality, completeness, and accuracy.
    Acts as an automated "editor" that checks articles before publication.

What is the Reflection Pattern?
    Reflection is an agentic AI design pattern where the agent:
    1. Produces output (or receives output from another agent)
    2. Critiques its own output (self-review)
    3. Revises the output based on the critique
    4. Repeats until satisfied or max iterations reached

    In CyberQuill, the flow is:
        Writer Agent → MagazineArticle
                            ↓
        Reviewer Agent → Reviews article (score 1-10)
                            ↓
        If score < 7:  → Send back to Writer for revision (max 2 cycles)
        If score >= 7: → Approved for PDF generation

    Why limit to 2 revision cycles?
        - Prevents infinite loops
        - LLMs can "overthink" and make articles worse after too many revisions
        - 2 cycles is enough to fix most quality issues

How it works:
    Mode 1: LLM-based (primary)
        - Sends article to Groq LLM with REVIEWER_PROMPT
        - LLM scores the article and identifies issues
        - LLM may provide a revised version
        - High-quality reviews, requires API key

    Mode 2: Rule-based (fallback)
        - Checks article structure (are all sections present?)
        - Checks minimum lengths for each section
        - Assigns a score based on completeness
        - Always works, no API needed

Inputs:
    - List[MagazineArticle] — articles from the Writer Agent

Outputs:
    - List[ReviewResult] — review scores, issues, and revised articles

Dependencies:
    - langchain-groq: LLM calls for review
    - config.settings: API keys, model configuration
    - config.prompts: REVIEWER_PROMPT, REVIEWER_REFLECTION_PROMPT
    - models.schemas: MagazineArticle, ReviewResult
    - utils.logger: Logging

Testing strategy:
    - Test rule-based review (no API needed)
    - Test with complete articles → should score high
    - Test with incomplete articles → should score low and flag issues
    - Test the reflection cycle (mock Writer revisions)
    - Edge cases (empty article, all sections empty)

Possible improvements:
    - Add fact-checking against RAG knowledge base
    - Implement style scoring (readability, tone consistency)
    - Add plagiarism detection
    - Track review history for analytics
"""

from config.prompts import REVIEWER_PROMPT
from config.settings import settings
from models.schemas import MagazineArticle, ReviewResult
from utils.logger import get_logger

logger = get_logger(__name__)

# ============================================
# Configuration
# ============================================

# Minimum score for approval (articles scoring below this are flagged)
APPROVAL_THRESHOLD = 7

# Maximum number of revision cycles
MAX_REVISIONS = 2

# Minimum word count for each section to be considered "complete"
# These are intentionally low — they check for PRESENCE, not quality
MIN_SECTION_WORDS = {
    "executive_summary": 10,
    "background": 15,
    "technical_analysis": 15,
    "impact": 10,
    "recommendations": 10,
    "references": 3,
}


def _review_by_rules(article: MagazineArticle) -> ReviewResult:
    """
    Reviews an article using rule-based checks (fallback method).

    How scoring works:
        Start with a base score of 10 (perfect).
        Deduct points for each issue found:
        - Missing section: -2 points
        - Section too short: -1 point
        - Missing title: -3 points

    Why rule-based?
        - Works without any API
        - Fast and deterministic (same input → same output)
        - Easy to explain in a viva
        - Good enough for testing the pipeline

    Args:
        article: A MagazineArticle to review

    Returns:
        A ReviewResult with score, issues, and approval status
    """
    issues = []
    score = 10  # Start perfect, deduct for problems

    # Check 1: Title must exist
    if not article.title or len(article.title.strip()) < 5:
        issues.append("Missing or too short title")
        score -= 3

    # Check 2: Each section must exist and meet minimum word count
    sections_to_check = {
        "Executive Summary": (article.executive_summary, MIN_SECTION_WORDS["executive_summary"]),
        "Background": (article.background, MIN_SECTION_WORDS["background"]),
        "Technical Analysis": (article.technical_analysis, MIN_SECTION_WORDS["technical_analysis"]),
        "Impact": (article.impact, MIN_SECTION_WORDS["impact"]),
        "Recommendations": (article.recommendations, MIN_SECTION_WORDS["recommendations"]),
        "References": (article.references, MIN_SECTION_WORDS["references"]),
    }

    for section_name, (content, min_words) in sections_to_check.items():
        if not content or not content.strip():
            issues.append(f"Missing section: {section_name}")
            score -= 2
        elif len(content.split()) < min_words:
            issues.append(
                f"{section_name} is too short "
                f"({len(content.split())} words, minimum {min_words})"
            )
            score -= 1

    # Clamp score to valid range [1, 10]
    score = max(1, min(10, score))

    approved = score >= APPROVAL_THRESHOLD

    review_notes = "Rule-based review completed. "
    if approved:
        review_notes += "Article meets quality standards."
    else:
        review_notes += f"Article needs improvement. {len(issues)} issue(s) found."

    return ReviewResult(
        quality_score=score,
        approved=approved,
        issues=issues,
        revised_article=None,  # Rule-based review doesn't revise
        review_notes=review_notes,
    )


def _format_article_for_review(article: MagazineArticle) -> str:
    """
    Formats a MagazineArticle as a readable string for LLM review.

    Why format as a string?
        The LLM prompt expects a single block of text, not a JSON object.
        This function creates a nicely formatted markdown version that the
        LLM can read and critique.

    Args:
        article: The MagazineArticle to format

    Returns:
        A formatted markdown string
    """
    return (
        f"# {article.title}\n\n"
        f"## Executive Summary\n{article.executive_summary}\n\n"
        f"## Background\n{article.background}\n\n"
        f"## Technical Analysis\n{article.technical_analysis}\n\n"
        f"## Impact\n{article.impact}\n\n"
        f"## Recommendations\n{article.recommendations}\n\n"
        f"## References\n{article.references}"
    )


def _parse_review_response(text: str) -> ReviewResult:
    """
    Parses the LLM's review response into a ReviewResult.

    The LLM is prompted to respond in this format:
        - **Quality Score**: [1-10]
        - **Approved**: [YES/NO]
        - **Issues Found**: [list]
        - **Revised Article**: [text]

    This function extracts each field using string matching.

    Args:
        text: The raw LLM review response

    Returns:
        A ReviewResult parsed from the response
    """
    import re

    # Extract quality score
    # Handles both "Quality Score: 9" and "**Quality Score**: 9"
    score_match = re.search(r"\**Quality Score\**[:\s]*(\d+)", text, re.IGNORECASE)
    score = int(score_match.group(1)) if score_match else 5
    score = max(1, min(10, score))

    # Extract approved status
    approved_match = re.search(r"\**Approved\**[:\s]*(YES|NO)", text, re.IGNORECASE)
    approved = approved_match.group(1).upper() == "YES" if approved_match else (score >= APPROVAL_THRESHOLD)

    # Extract issues
    issues = []
    issues_match = re.search(
        r"\**Issues Found\**[:\s]*(.*?)(?=\n\s*[-*]?\s*\**Revised|\Z)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if issues_match:
        issues_text = issues_match.group(1).strip()
        if issues_text.lower() not in ("none", "none.", "no issues", "no issues found"):
            # Split by newlines or bullet points
            for line in issues_text.split("\n"):
                line = line.strip().lstrip("-*• ").strip()
                if line and len(line) > 3:
                    issues.append(line)

    # Extract revised article (if provided)
    revised_match = re.search(
        r"\**Revised Article\**[:\s]*(.*)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    revised_article = None
    if revised_match:
        revised_text = revised_match.group(1).strip()
        if revised_text.lower() not in (
            "no changes needed",
            "no changes needed.",
            "no revision needed",
        ):
            revised_article = revised_text

    return ReviewResult(
        quality_score=score,
        approved=approved,
        issues=issues,
        revised_article=revised_article,
        review_notes=f"LLM review completed. Score: {score}/10.",
    )


def _review_by_llm(article: MagazineArticle) -> ReviewResult:
    """
    Reviews an article using the Groq LLM (primary method).

    How it works:
        1. Formats the article as readable text
        2. Sends to LLM with REVIEWER_PROMPT
        3. Parses the review response

    Args:
        article: A MagazineArticle to review

    Returns:
        A ReviewResult from the LLM review

    Raises:
        Exception: If the API call fails
    """
    from langchain_groq import ChatGroq

    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=0.3,  # Low temperature for consistent reviews
        max_tokens=2000,
    )

    # Format the article for review
    article_text = _format_article_for_review(article)

    # Send to LLM
    prompt = REVIEWER_PROMPT.format(article=article_text)
    response = llm.invoke(prompt)
    raw_text = response.content.strip()

    logger.debug(f"LLM review response length: {len(raw_text)} chars")

    return _parse_review_response(raw_text)


def review_article(article: MagazineArticle) -> ReviewResult:
    """
    Reviews a single magazine article.

    Strategy:
        1. Try LLM review (if API key is available)
        2. Fall back to rule-based review

    Args:
        article: A MagazineArticle to review

    Returns:
        A ReviewResult with score, issues, and approval
    """
    # Try LLM review first
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here":
        try:
            result = _review_by_llm(article)
            logger.debug(
                f"LLM reviewed '{article.title[:40]}...' — "
                f"Score: {result.quality_score}/10, "
                f"Approved: {result.approved}"
            )
            return result
        except Exception as e:
            logger.warning(f"LLM review failed: {e}. Using rule-based fallback.")

    # Fallback: rule-based review
    result = _review_by_rules(article)
    logger.debug(
        f"Rule-based reviewed '{article.title[:40]}...' — "
        f"Score: {result.quality_score}/10, "
        f"Approved: {result.approved}"
    )
    return result


def review_articles(
    articles: list[MagazineArticle],
) -> list[ReviewResult]:
    """
    Reviews a list of magazine articles.

    This is the main entry point for the Reviewer Agent.

    Args:
        articles: List of MagazineArticle objects

    Returns:
        List of ReviewResult objects (one per article)
    """
    if not articles:
        logger.info("No articles to review")
        return []

    logger.info(f"Reviewing {len(articles)} articles...")

    # Determine method
    using_llm = (
        settings.GROQ_API_KEY
        and settings.GROQ_API_KEY != "your_groq_api_key_here"
    )
    method = "LLM (Groq)" if using_llm else "rule-based (fallback)"
    logger.info(f"Review method: {method}")

    results = []
    approved_count = 0

    for article in articles:
        result = review_article(article)
        results.append(result)
        if result.approved:
            approved_count += 1

    logger.info(
        f"Review complete. "
        f"{approved_count}/{len(articles)} articles approved. "
        f"Average score: "
        f"{sum(r.quality_score for r in results) / len(results):.1f}/10"
    )

    return results


# ============================================
# LangGraph Node Function
# ============================================

def reviewer_node(state: dict) -> dict:
    """
    LangGraph node function for the Reviewer Agent.

    Implements the Reflection Pattern:
        1. Review all magazine articles
        2. If any article scores below threshold, log the issues
        3. In a full implementation, low-scoring articles would be
           sent back to the Writer Agent for revision

    Note on the Reflection Pattern:
        The full reflection loop (Writer → Reviewer → Writer → Reviewer)
        is implemented in the LangGraph Orchestrator (Phase 9), not here.
        This node only does the REVIEW step. The Orchestrator handles
        the loop logic with conditional edges.

    Args:
        state: The current pipeline state dictionary

    Returns:
        Dictionary with state updates:
        - "review_results": list of ReviewResult objects
        - "current_stage": updated to "review_complete"
    """
    logger.info("Reviewer Agent starting...")

    magazine_articles = state.get("magazine_articles", [])
    review_results = review_articles(magazine_articles)

    # Log summary
    approved = sum(1 for r in review_results if r.approved)
    logger.info(
        f"Reviewer Agent finished. "
        f"{approved}/{len(review_results)} articles approved."
    )

    return {
        "review_results": review_results,
        "current_stage": "review_complete",
    }
