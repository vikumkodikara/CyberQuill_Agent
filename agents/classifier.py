"""
CyberQuill Classification Agent
==================================

Purpose:
    Classifies cybersecurity articles into threat categories.
    Takes deduplicated articles and assigns each one a category like
    "Malware", "Data Breach", "Zero-Day", etc.

Why classify?
    - The magazine is organized by category (sections)
    - Readers can filter articles by interest area
    - The Writer Agent uses category context to generate better articles
    - It enables analytics (e.g., "60% of this week's news is about malware")

Classification strategy (2 modes):
    Mode 1: LLM-based (primary)
        - Sends article title + summary to Groq LLM
        - LLM returns the most appropriate category
        - High accuracy, but requires API key and credits

    Mode 2: Keyword-based (fallback)
        - Matches keywords in title and summary against category dictionaries
        - No API needed — works offline
        - Lower accuracy, but always available
        - Used automatically when Groq API key is missing

    Why have a fallback?
        - During development, you may not have API credits
        - During testing, we don't want to burn API calls
        - During viva demos, the API might be slow or down
        - This demonstrates graceful degradation (important design pattern)

Inputs:
    - List[Article] — deduplicated articles from the Duplicate Agent

Outputs:
    - List[ClassifiedArticle] — articles with category and confidence score

Dependencies:
    - langchain-groq: LLM calls to Groq
    - config.settings: API keys, model names, categories
    - config.prompts: Classification prompt template
    - models.schemas: Article, ClassifiedArticle
    - utils.logger: Logging

Agentic AI Design Pattern:
    **Router Pattern** — This agent acts as a router, directing articles
    into different category "lanes". The classification decision determines
    how downstream agents (Writer, RAG) process each article.

Testing strategy:
    - Unit tests for keyword-based classification (no API needed)
    - Unit tests for prompt formatting
    - Integration tests with Groq API (optional, requires API key)
    - Edge case tests (empty title, unknown category response)

Possible improvements:
    - Multi-label classification (article can be in multiple categories)
    - Confidence calibration using temperature tuning
    - Fine-tuned classification model for higher accuracy
    - Cache classification results for repeated articles
"""

from models.schemas import Article, ClassifiedArticle
from config.settings import settings
from config.prompts import CLASSIFICATION_PROMPT
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================
# Keyword Dictionaries for Fallback Classifier
# ============================================
# Each category has a list of keywords that strongly suggest that category.
# If the article title or summary contains these keywords, we assign that category.
#
# Why dictionaries?
#   - Simple, explainable, debuggable
#   - No API costs
#   - During viva, you can easily explain: "if the title contains 'ransomware',
#     we classify it as Malware"
#
# These keywords were chosen based on common cybersecurity terminology.

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Malware": [
        "malware", "ransomware", "trojan", "worm", "botnet", "spyware",
        "adware", "keylogger", "rootkit", "backdoor", "virus", "payload",
        "infostealer", "stealer", "rat ", "remote access trojan",
    ],
    "Data Breach": [
        "data breach", "breach", "leaked", "leak", "exposed", "data stolen",
        "records stolen", "personal data", "data exposure", "compromised data",
        "database leak", "credential leak", "data dump",
    ],
    "AI Security": [
        "ai security", "artificial intelligence", "machine learning", "llm",
        "deepfake", "ai-generated", "chatgpt", "generative ai", "ai model",
        "prompt injection", "ai threat", "ai vulnerability",
    ],
    "Cloud Security": [
        "cloud security", "aws", "azure", "gcp", "cloud misconfiguration",
        "s3 bucket", "cloud breach", "saas", "kubernetes", "k8s", "docker",
        "container security", "cloud-native", "serverless",
    ],
    "Zero-Day": [
        "zero-day", "zero day", "0-day", "0day", "actively exploited",
        "unpatched", "critical vulnerability", "cve-", "exploit",
        "in-the-wild", "proof of concept", "poc",
    ],
    "Threat Intelligence": [
        "threat intelligence", "apt", "threat actor", "nation-state",
        "cyber espionage", "campaign", "threat group", "ioc",
        "indicators of compromise", "ttps", "attribution",
        "state-sponsored", "cyber warfare",
    ],
    "Vulnerability Management": [
        "vulnerability", "patch", "update", "security fix", "cve",
        "security advisory", "patched", "security update",
        "firmware update", "critical flaw", "bug bounty", "disclosure",
    ],
}


def _classify_by_keywords(title: str, summary: str) -> tuple[str, float]:
    """
    Classifies an article using keyword matching (fallback method).

    How it works:
        1. Combine title and summary into one text block (lowercase)
        2. For each category, count how many of its keywords appear
        3. The category with the most keyword matches wins
        4. Confidence = number of matches / total keywords in that category

    Why count matches instead of just checking for ANY match?
        An article about a "cloud vulnerability patch" contains keywords for
        BOTH "Cloud Security" and "Vulnerability Management". By counting,
        we pick the category with the STRONGEST signal.

    Args:
        title: Article title
        summary: Article summary

    Returns:
        Tuple of (category_name, confidence_score)
        If no keywords match, returns ("Uncategorized", 0.0)
    """
    text = f"{title} {summary}".lower()

    best_category = "Uncategorized"
    best_score = 0.0

    for category, keywords in CATEGORY_KEYWORDS.items():
        # Count how many keywords from this category appear in the text
        matches = sum(1 for keyword in keywords if keyword in text)

        if matches > 0:
            # Confidence = proportion of keywords that matched
            # Capped at 0.9 because keyword matching is never 100% certain
            confidence = min(matches / len(keywords), 0.9)

            if matches > best_score:
                best_score = matches
                best_category = category
                best_confidence = confidence

    if best_category == "Uncategorized":
        return "Uncategorized", 0.0

    return best_category, best_confidence


def _classify_by_llm(title: str, summary: str) -> tuple[str, float]:
    """
    Classifies an article using the Groq LLM (primary method).

    How it works:
        1. Formats the classification prompt with the article data
        2. Sends the prompt to Groq's LLM (fast inference)
        3. Parses the LLM's response to extract the category
        4. Validates the category against our allowed categories

    Why Groq for classification?
        - Groq is extremely fast (< 1 second per request)
        - Classification is a simple task — doesn't need a large model
        - Groq has a generous free tier
        - Low latency means we can classify articles quickly

    Args:
        title: Article title
        summary: Article summary

    Returns:
        Tuple of (category_name, confidence_score)

    Raises:
        Exception: If the API call fails (caught by the caller)
    """
    from langchain_groq import ChatGroq

    # Create the Groq LLM client
    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=0.0,  # Zero temperature for deterministic classification
        max_tokens=50,    # Category name is short — no need for long output
    )

    # Format the prompt with article data and available categories
    prompt = CLASSIFICATION_PROMPT.format(
        categories=", ".join(settings.CATEGORIES),
        title=title,
        summary=summary,
    )

    # Call the LLM
    response = llm.invoke(prompt)
    raw_response = response.content.strip()

    logger.debug(f"LLM classification response: '{raw_response}'")

    # Validate: Check if the response matches one of our categories
    # The LLM might return extra text, so we check if any category
    # is contained in the response
    for category in settings.CATEGORIES:
        if category.lower() in raw_response.lower():
            return category, 0.95  # High confidence for LLM classification

    # If the LLM returned something unexpected, log it and fall back
    logger.warning(
        f"LLM returned unexpected category '{raw_response}'. "
        f"Falling back to keyword classification."
    )
    return _classify_by_keywords(title, summary)


def classify_article(article: Article) -> ClassifiedArticle:
    """
    Classifies a single article using the best available method.

    Strategy:
        1. Try LLM classification (if API key is available)
        2. Fall back to keyword classification (if LLM fails)
        3. Return "Uncategorized" if both fail

    This pattern is called **graceful degradation** — the system
    continues to work even when the preferred method fails, just
    with lower quality results.

    Args:
        article: An Article object to classify

    Returns:
        A ClassifiedArticle with the category and confidence score added
    """
    category = "Uncategorized"
    confidence = 0.0

    # Try LLM classification first (if API key is configured)
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here":
        try:
            category, confidence = _classify_by_llm(article.title, article.summary)
            logger.debug(
                f"LLM classified '{article.title[:50]}...' as {category} "
                f"(confidence: {confidence:.2f})"
            )
        except Exception as e:
            logger.warning(f"LLM classification failed: {e}. Using keyword fallback.")
            category, confidence = _classify_by_keywords(
                article.title, article.summary
            )
    else:
        # No API key — use keyword fallback
        category, confidence = _classify_by_keywords(
            article.title, article.summary
        )
        logger.debug(
            f"Keyword classified '{article.title[:50]}...' as {category} "
            f"(confidence: {confidence:.2f})"
        )

    # Create a ClassifiedArticle by copying all original fields and adding category
    return ClassifiedArticle(
        title=article.title,
        link=article.link,
        source=article.source,
        published=article.published,
        summary=article.summary,
        category=category,
        confidence=confidence,
    )


def classify_articles(articles: list[Article]) -> list[ClassifiedArticle]:
    """
    Classifies a list of articles.

    This is the main entry point for the Classification Agent.

    Args:
        articles: List of Article objects (from Duplicate Agent)

    Returns:
        List of ClassifiedArticle objects with categories assigned

    Example:
        >>> from agents.classifier import classify_articles
        >>> classified = classify_articles(unique_articles)
        >>> for a in classified:
        ...     print(f"{a.category}: {a.title}")
    """
    if not articles:
        logger.info("No articles to classify")
        return []

    logger.info(f"Classifying {len(articles)} articles...")

    # Determine which method we're using (for logging)
    using_llm = (
        settings.GROQ_API_KEY
        and settings.GROQ_API_KEY != "your_groq_api_key_here"
    )
    method = "LLM (Groq)" if using_llm else "keyword matching (fallback)"
    logger.info(f"Classification method: {method}")

    classified = []
    for article in articles:
        classified_article = classify_article(article)
        classified.append(classified_article)

    # Log category distribution
    categories = {}
    for article in classified:
        categories[article.category] = categories.get(article.category, 0) + 1

    logger.info(f"Classification complete. Distribution: {categories}")

    return classified


# ============================================
# LangGraph Node Function
# ============================================

def classifier_node(state: dict) -> dict:
    """
    LangGraph node function for the Classification Agent.

    Reads unique_articles from state, classifies each one,
    and writes classified_articles back to state.

    Args:
        state: The current pipeline state dictionary
               Expected to contain "unique_articles" key

    Returns:
        Dictionary with state updates:
        - "classified_articles": list of ClassifiedArticle objects
        - "current_stage": updated to "classification_complete"
    """
    logger.info("Classification Agent starting...")

    unique_articles = state.get("unique_articles", [])
    classified_articles = classify_articles(unique_articles)

    logger.info(
        f"Classification Agent finished. "
        f"Classified {len(classified_articles)} articles."
    )

    return {
        "classified_articles": classified_articles,
        "current_stage": "classification_complete",
    }
