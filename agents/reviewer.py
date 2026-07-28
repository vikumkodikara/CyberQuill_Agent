"""
CyberQuill Reviewer Agent
============================

Purpose:
    Reviews magazine articles for quality, completeness, and accuracy.
    Acts as an automated "editor" that checks articles before publication.
    Now includes RAG-grounded verification against the knowledge base.
"""

import re

from config.prompts import REVIEWER_PROMPT
from config.settings import settings
from models.schemas import MagazineArticle, ReviewResult
from utils.logger import get_logger

logger = get_logger(__name__)

APPROVAL_THRESHOLD = 7
RAG_FIDELITY_THRESHOLD = 6
MAX_REVISIONS = 2

MIN_SECTION_WORDS = {
    "executive_summary": 10,
    "background": 15,
    "technical_analysis": 15,
    "impact": 10,
    "recommendations": 10,
    "references": 3,
}


def _compute_rag_fidelity(
    article: MagazineArticle,
    rag_context: str,
) -> tuple[int, list[str]]:
    """
    Rule-based RAG fidelity scoring via keyword overlap.

    Compares article text against RAG context keywords.
    """
    if not rag_context.strip():
        return 10, []

    article_text = _format_article_for_review(article).lower()
    rag_lower = rag_context.lower()

    rag_words = {
        word
        for word in re.findall(r"[a-z]{4,}", rag_lower)
        if word not in {"that", "this", "with", "from", "have", "been", "will"}
    }

    if not rag_words:
        return 10, []

    overlap = sum(1 for word in rag_words if word in article_text)
    overlap_ratio = overlap / len(rag_words)

    if overlap_ratio >= 0.15:
        score = 10
    elif overlap_ratio >= 0.10:
        score = 8
    elif overlap_ratio >= 0.05:
        score = 6
    elif overlap_ratio >= 0.02:
        score = 4
    else:
        score = 2

    issues = []
    if score < RAG_FIDELITY_THRESHOLD:
        issues.append(
            "Article has low alignment with knowledge base context "
            f"(overlap: {overlap_ratio:.1%})"
        )

    return score, issues


def _review_by_rules(
    article: MagazineArticle,
    rag_context: str = "",
) -> ReviewResult:
    """Reviews an article using rule-based checks (fallback method)."""
    issues = []
    score = 10

    if not article.title or len(article.title.strip()) < 5:
        issues.append("Missing or too short title")
        score -= 3

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

    score = max(1, min(10, score))

    rag_fidelity_score, rag_issues = _compute_rag_fidelity(article, rag_context)
    approved = (
        score >= APPROVAL_THRESHOLD
        and rag_fidelity_score >= RAG_FIDELITY_THRESHOLD
    )

    review_notes = "Rule-based review completed. "
    if approved:
        review_notes += "Article meets quality and RAG fidelity standards."
    else:
        review_notes += f"Article needs improvement. {len(issues)} issue(s) found."

    return ReviewResult(
        quality_score=score,
        approved=approved,
        issues=issues,
        revised_article=None,
        review_notes=review_notes,
        rag_fidelity_score=rag_fidelity_score,
        rag_issues=rag_issues,
    )


def _format_article_for_review(article: MagazineArticle) -> str:
    """Formats a MagazineArticle as a readable string for LLM review."""
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
    """Parses the LLM's review response into a ReviewResult."""
    score_match = re.search(r"\**Quality Score\**[:\s]*(\d+)", text, re.IGNORECASE)
    score = int(score_match.group(1)) if score_match else 5
    score = max(1, min(10, score))

    rag_match = re.search(
        r"\**RAG Fidelity Score\**[:\s]*(\d+)", text, re.IGNORECASE
    )
    rag_fidelity_score = int(rag_match.group(1)) if rag_match else score
    rag_fidelity_score = max(1, min(10, rag_fidelity_score))

    approved_match = re.search(r"\**Approved\**[:\s]*(YES|NO)", text, re.IGNORECASE)
    if approved_match:
        approved = approved_match.group(1).upper() == "YES"
    else:
        approved = (
            score >= APPROVAL_THRESHOLD
            and rag_fidelity_score >= RAG_FIDELITY_THRESHOLD
        )

    issues = []
    issues_match = re.search(
        r"\**Issues Found\**[:\s]*(.*?)(?=\n\s*[-*]?\s*\**RAG|\n\s*[-*]?\s*\**Revised|\Z)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if issues_match:
        issues_text = issues_match.group(1).strip()
        if issues_text.lower() not in ("none", "none.", "no issues", "no issues found"):
            for line in issues_text.split("\n"):
                line = line.strip().lstrip("-*• ").strip()
                if line and len(line) > 3:
                    issues.append(line)

    rag_issues = []
    rag_issues_match = re.search(
        r"\**RAG Issues\**[:\s]*(.*?)(?=\n\s*[-*]?\s*\**Revised|\Z)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if rag_issues_match:
        rag_text = rag_issues_match.group(1).strip()
        if rag_text.lower() not in ("none", "none.", "no issues", "no rag issues"):
            for line in rag_text.split("\n"):
                line = line.strip().lstrip("-*• ").strip()
                if line and len(line) > 3:
                    rag_issues.append(line)

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
        review_notes=f"LLM review completed. Score: {score}/10, RAG: {rag_fidelity_score}/10.",
        rag_fidelity_score=rag_fidelity_score,
        rag_issues=rag_issues,
    )


def _review_by_llm(
    article: MagazineArticle,
    rag_context: str = "",
) -> ReviewResult:
    """Reviews an article using the Groq LLM (primary method)."""
    from langchain_groq import ChatGroq

    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=0.3,
        max_tokens=2000,
    )

    article_text = _format_article_for_review(article)
    prompt = REVIEWER_PROMPT.format(
        article=article_text,
        rag_context=rag_context or "No knowledge base context available.",
    )
    response = llm.invoke(prompt)
    raw_text = response.content.strip()

    logger.debug(f"LLM review response length: {len(raw_text)} chars")

    return _parse_review_response(raw_text)


def review_article(
    article: MagazineArticle,
    rag_context: str = "",
    rag_sources: list[str] | None = None,
) -> ReviewResult:
    """Reviews a single magazine article with optional RAG verification."""
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here":
        try:
            result = _review_by_llm(article, rag_context=rag_context)
            logger.debug(
                f"LLM reviewed '{article.title[:40]}...' — "
                f"Score: {result.quality_score}/10, "
                f"RAG: {result.rag_fidelity_score}/10, "
                f"Approved: {result.approved}"
            )
            return result
        except Exception as e:
            logger.warning(f"LLM review failed: {e}. Using rule-based fallback.")

    result = _review_by_rules(article, rag_context=rag_context)
    logger.debug(
        f"Rule-based reviewed '{article.title[:40]}...' — "
        f"Score: {result.quality_score}/10, "
        f"RAG: {result.rag_fidelity_score}/10, "
        f"Approved: {result.approved}"
    )
    return result


def review_articles(
    articles: list[MagazineArticle],
    rag_contexts: list[str] | None = None,
) -> list[ReviewResult]:
    """Reviews a list of magazine articles with optional RAG contexts."""
    if not articles:
        logger.info("No articles to review")
        return []

    logger.info(f"Reviewing {len(articles)} articles...")

    using_llm = (
        settings.GROQ_API_KEY
        and settings.GROQ_API_KEY != "your_groq_api_key_here"
    )
    method = "LLM (Groq)" if using_llm else "rule-based (fallback)"
    logger.info(f"Review method: {method}")

    contexts = rag_contexts or [""] * len(articles)
    results = []
    approved_count = 0

    for article, rag_context in zip(articles, contexts):
        result = review_article(article, rag_context=rag_context)
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


def reviewer_node(state: dict) -> dict:
    """LangGraph node function for the Reviewer Agent."""
    logger.info("Reviewer Agent starting...")

    magazine_articles = state.get("magazine_articles", [])
    enriched_articles = state.get("enriched_articles", [])

    rag_contexts = [
        ea.rag_context if hasattr(ea, "rag_context") else ea.get("rag_context", "")
        for ea in enriched_articles
    ]

    while len(rag_contexts) < len(magazine_articles):
        rag_contexts.append("")

    review_results = review_articles(magazine_articles, rag_contexts=rag_contexts)

    approved = sum(1 for r in review_results if r.approved)
    logger.info(
        f"Reviewer Agent finished. "
        f"{approved}/{len(review_results)} articles approved."
    )

    return {
        "review_results": review_results,
        "current_stage": "review_complete",
    }
