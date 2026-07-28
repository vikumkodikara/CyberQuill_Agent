"""
CyberQuill Classification Agent
==================================

Purpose:
    Classifies cybersecurity articles into threat categories using a
    multi-pass pipeline: LLM → keywords → forced LLM → best-guess.
"""

import re

from config.prompts import CLASSIFICATION_FORCED_PROMPT, CLASSIFICATION_PROMPT
from config.settings import settings
from models.schemas import Article, ClassifiedArticle
from utils.logger import get_logger

logger = get_logger(__name__)

UNCATEGORIZED = "Uncategorized"

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Malware": [
        "malware", "ransomware", "trojan", "worm", "botnet", "spyware",
        "adware", "keylogger", "rootkit", "backdoor", "virus", "payload",
        "infostealer", "stealer", "rat ", "remote access trojan",
        "phishing", "scam", "cryptominer", "cryptomining", "emotet",
        "lockbit", "blackcat", "wiper", "social engineering", "smishing",
        "vishing", "malicious email", "malicious attachment", "dropper",
        "c2 server", "command and control", "banking trojan",
    ],
    "Data Breach": [
        "data breach", "breach", "leaked", "leak", "exposed", "data stolen",
        "records stolen", "personal data", "data exposure", "compromised data",
        "database leak", "credential leak", "data dump", "hacked", "hackers",
        "stolen data", "pii", "customer data", "records exposed",
        "identity theft", "stolen credentials", "password leak",
        "millions of records", "patient data", "credit card",
    ],
    "AI Security": [
        "ai security", "artificial intelligence", "machine learning", "llm",
        "deepfake", "ai-generated", "chatgpt", "generative ai", "ai model",
        "prompt injection", "ai threat", "ai vulnerability", "openai",
        "gemini", "claude", "ai-powered", "neural", "large language model",
        "hallucination", "model poisoning", "ai chatbot",
    ],
    "Cloud Security": [
        "cloud security", "aws", "azure", "gcp", "cloud misconfiguration",
        "s3 bucket", "cloud breach", "saas", "kubernetes", "k8s", "docker",
        "container security", "cloud-native", "serverless", "misconfigured",
        "blob storage", "entra", "iam", "terraform", "devops", "ec2",
        "lambda", "cloudflare", "multi-cloud", "hybrid cloud",
    ],
    "Zero-Day": [
        "zero-day", "zero day", "0-day", "0day", "actively exploited",
        "unpatched", "critical vulnerability", "cve-", "exploit",
        "in-the-wild", "in the wild", "proof of concept", "poc",
        "emergency patch", "critical flaw", "under attack", "weaponized",
        "remote code execution", "rce vulnerability",
    ],
    "Threat Intelligence": [
        "threat intelligence", "apt", "threat actor", "nation-state",
        "cyber espionage", "campaign", "threat group", "ioc",
        "indicators of compromise", "ttps", "attribution",
        "state-sponsored", "cyber warfare", "hacking group", "cybercrime",
        "fraud ring", "espionage", "sanctions", "cyber gang",
        "hacker group", "lazarus", "fancy bear", "cozy bear",
        "supply chain attack", "cyber criminal",
    ],
    "Vulnerability Management": [
        "vulnerability", "patch", "update", "security fix", "cve",
        "security advisory", "patched", "security update",
        "firmware update", "critical flaw", "bug bounty", "disclosure",
        "security flaw", "bug fix", "fixed", "patch tuesday", "advisory",
        "mitigation", "security bulletin", "hotfix", "version update",
        "end of life", "eol software",
    ],
}

CATEGORY_ALIASES: dict[str, str] = {
    "ransomware": "Malware",
    "phishing": "Malware",
    "trojan": "Malware",
    "botnet": "Malware",
    "virus": "Malware",
    "spyware": "Malware",
    "malicious": "Malware",
    "scam": "Malware",
    "breach": "Data Breach",
    "leak": "Data Breach",
    "leaked": "Data Breach",
    "hacked": "Data Breach",
    "hack": "Data Breach",
    "stolen": "Data Breach",
    "exposed": "Data Breach",
    "ai": "AI Security",
    "llm": "AI Security",
    "chatgpt": "AI Security",
    "deepfake": "AI Security",
    "cloud": "Cloud Security",
    "aws": "Cloud Security",
    "azure": "Cloud Security",
    "kubernetes": "Cloud Security",
    "docker": "Cloud Security",
    "zero day": "Zero-Day",
    "zero-day": "Zero-Day",
    "0-day": "Zero-Day",
    "exploit": "Zero-Day",
    "cve": "Vulnerability Management",
    "patch": "Vulnerability Management",
    "advisory": "Vulnerability Management",
    "vulnerability": "Vulnerability Management",
    "apt": "Threat Intelligence",
    "threat actor": "Threat Intelligence",
    "cybercrime": "Threat Intelligence",
    "espionage": "Threat Intelligence",
}

SECURITY_SIGNALS = [
    "cyber", "security", "hack", "vulnerability", "exploit", "malware",
    "ransomware", "breach", "phishing", "attack", "threat", "cve",
    "patch", "encrypt", "credential", "firewall", "intrusion", "defacement",
    "ddos", "botnet", "spyware", "trojan", "backdoor", "zero-day",
    "zero day", "data leak", "stolen", "compromised", "infosec",
]


def _normalize_category(raw_response: str) -> str | None:
    """Normalize LLM or alias text into a valid category name."""
    if not raw_response or not raw_response.strip():
        return None

    cleaned = raw_response.strip().strip("\"'`.,:;")
    cleaned = re.sub(r"^(category|answer|classification)[:\s]+", "", cleaned, flags=re.I)
    cleaned = cleaned.strip()

    if cleaned.lower() == "uncategorized":
        return None

    for category in settings.CATEGORIES:
        if cleaned.lower() == category.lower():
            return category

    for category in settings.CATEGORIES:
        if category.lower() in cleaned.lower():
            return category

    lower = cleaned.lower()
    for alias, category in CATEGORY_ALIASES.items():
        if alias in lower:
            return category

    return None


def _is_security_article(title: str, summary: str) -> bool:
    """Return True if the article appears security-related."""
    text = f"{title} {summary}".lower()
    return any(signal in text for signal in SECURITY_SIGNALS)


def _classify_by_keywords(title: str, summary: str) -> tuple[str, float]:
    """Classify using keyword matching. Accepts single-keyword matches."""
    text = f"{title} {summary}".lower()

    best_category = UNCATEGORIZED
    best_match_count = 0
    best_confidence = 0.0

    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = sum(1 for keyword in keywords if keyword in text)

        if matches > 0:
            confidence = min(max(matches / len(keywords), 0.35), 0.9)

            if matches > best_match_count:
                best_match_count = matches
                best_category = category
                best_confidence = confidence

    if best_category == UNCATEGORIZED:
        return UNCATEGORIZED, 0.0

    return best_category, best_confidence


def _best_guess_category(title: str, summary: str) -> tuple[str, float]:
    """
    Last-resort classification for security articles with weak signals.
    Picks the category with the highest partial keyword overlap.
    """
    if not _is_security_article(title, summary):
        return UNCATEGORIZED, 0.0

    text = f"{title} {summary}".lower()
    scores: dict[str, float] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0.0
        for keyword in keywords:
            if keyword in text:
                score += 1.0
            elif any(part in text for part in keyword.split() if len(part) > 3):
                score += 0.25
        if score > 0:
            scores[category] = score

    if not scores:
        return "Threat Intelligence", 0.25

    best_category = max(scores, key=scores.get)
    confidence = min(0.25 + scores[best_category] * 0.1, 0.5)
    return best_category, confidence


def _invoke_llm(prompt: str) -> str:
    """Call Groq LLM and return raw response text."""
    from langchain_groq import ChatGroq

    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=0.0,
        max_tokens=50,
    )
    response = llm.invoke(prompt)
    return response.content.strip()


def _classify_by_llm(title: str, summary: str) -> tuple[str, float]:
    """Primary LLM classification."""
    prompt = CLASSIFICATION_PROMPT.format(
        categories=", ".join(settings.CATEGORIES),
        title=title,
        summary=summary or "No summary available.",
    )

    raw_response = _invoke_llm(prompt)
    logger.debug(f"LLM classification response: '{raw_response}'")

    category = _normalize_category(raw_response)
    if category:
        return category, 0.95

    logger.warning(f"LLM returned unexpected category '{raw_response}'")
    return UNCATEGORIZED, 0.0


def _classify_forced_choice(title: str, summary: str) -> tuple[str, float]:
    """Forced-choice LLM retry when other methods fail."""
    prompt = CLASSIFICATION_FORCED_PROMPT.format(
        categories=", ".join(settings.CATEGORIES),
        title=title,
        summary=summary or "No summary available.",
    )

    raw_response = _invoke_llm(prompt)
    logger.debug(f"Forced LLM classification response: '{raw_response}'")

    category = _normalize_category(raw_response)
    if category:
        return category, 0.75

    return UNCATEGORIZED, 0.0


def _llm_available() -> bool:
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        return False
    try:
        import langchain_groq  # noqa: F401
        return True
    except ImportError:
        return False


def classify_article(article: Article) -> ClassifiedArticle:
    """
    Multi-pass classification pipeline:
    1. LLM (if API available)
    2. Expanded keyword matching
    3. Forced-choice LLM retry
    4. Best-guess for security-related articles
    """
    title = article.title
    summary = article.summary
    category = UNCATEGORIZED
    confidence = 0.0
    method = "uncategorized"

    if _llm_available():
        try:
            category, confidence = _classify_by_llm(title, summary)
            if category != UNCATEGORIZED:
                method = "llm"
        except Exception as e:
            logger.warning(f"LLM classification failed: {e}")

    if category == UNCATEGORIZED:
        category, confidence = _classify_by_keywords(title, summary)
        if category != UNCATEGORIZED:
            method = "keyword"

    if category == UNCATEGORIZED and _llm_available():
        try:
            category, confidence = _classify_forced_choice(title, summary)
            if category != UNCATEGORIZED:
                method = "forced_llm"
        except Exception as e:
            logger.warning(f"Forced LLM classification failed: {e}")

    if category == UNCATEGORIZED:
        category, confidence = _best_guess_category(title, summary)
        if category != UNCATEGORIZED:
            method = "best_guess"

    logger.debug(
        f"Classified '{title[:50]}...' as {category} "
        f"(confidence: {confidence:.2f}, method: {method})"
    )

    return ClassifiedArticle(
        title=article.title,
        link=article.link,
        source=article.source,
        published=article.published,
        summary=article.summary,
        category=category,
        confidence=confidence,
        classification_method=method,
    )


def classify_articles(articles: list[Article]) -> list[ClassifiedArticle]:
    """Classifies a list of articles."""
    if not articles:
        logger.info("No articles to classify")
        return []

    logger.info(f"Classifying {len(articles)} articles...")
    method_label = "multi-pass (LLM + keywords)" if _llm_available() else "keyword matching (fallback)"
    logger.info(f"Classification method: {method_label}")

    classified = [classify_article(article) for article in articles]

    categories: dict[str, int] = {}
    for item in classified:
        categories[item.category] = categories.get(item.category, 0) + 1

    uncategorized = categories.get(UNCATEGORIZED, 0)
    rate = (uncategorized / len(classified)) * 100 if classified else 0
    logger.info(
        f"Classification complete. Distribution: {categories} "
        f"(uncategorized: {uncategorized}/{len(classified)} = {rate:.1f}%)"
    )

    return classified


def classifier_node(state: dict) -> dict:
    """LangGraph node function for the Classification Agent."""
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
