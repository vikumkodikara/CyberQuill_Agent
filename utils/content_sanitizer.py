"""
CyberQuill Content Sanitizer
===============================

Purpose:
    Strips all internal RAG artifacts from article content before
    display in the Streamlit UI or PDF output.  The reader should
    never see MITRE technique IDs, vector-database metadata, source
    filenames, or chunk separators.

What it removes / rewrites:
    - MITRE ATT&CK identifiers  (TA0001, T1059, T1059.001 …)
    - Markdown headings that leak from retrieved chunks
    - Chunk-boundary separators  (---)
    - Source filenames  (owasp_top_10.md, mitre_attack.md, nist.md …)
    - Embedding / vector-DB references
    - Raw markdown bold markers left in plain-text contexts

This module is presentation-only.  It does NOT touch agent logic,
pipeline state, or the data stored in ChromaDB.
"""

import re

from models.schemas import MagazineArticle


# ============================================
# MITRE ATT&CK Technique → Human Description
# ============================================

_MITRE_TACTIC_MAP: dict[str, str] = {
    # Tactics (TA00xx)
    "TA0001": "Initial Access",
    "TA0002": "Execution",
    "TA0003": "Persistence",
    "TA0004": "Privilege Escalation",
    "TA0005": "Defense Evasion",
    "TA0006": "Credential Access",
    "TA0007": "Discovery",
    "TA0008": "Lateral Movement",
    "TA0009": "Collection",
    "TA0010": "Exfiltration",
    "TA0011": "Command and Control",
    "TA0040": "Impact",
    "TA0042": "Resource Development",
    "TA0043": "Reconnaissance",
}

_TACTIC_DESCRIPTIONS: dict[str, str] = {
    "TA0001": "Threat actors typically gain entry through phishing campaigns, compromised software packages, or exposed services.",
    "TA0002": "Once inside a target environment, attackers execute malicious code to achieve their objectives.",
    "TA0003": "Attackers establish footholds to maintain access to compromised systems across restarts and credential changes.",
    "TA0004": "After initial access, adversaries attempt to gain higher-level permissions within the target environment.",
    "TA0005": "Sophisticated threat actors employ techniques to avoid detection by security tools and monitoring systems.",
    "TA0006": "Attackers target authentication credentials such as passwords, tokens, and keys to expand their access.",
    "TA0007": "Adversaries explore the target environment to understand the network topology, installed software, and available resources.",
    "TA0008": "After compromising one system, attackers move through the network to reach additional targets and high-value assets.",
    "TA0009": "Attackers often collect sensitive information after gaining access to a target environment before proceeding to later stages of an attack.",
    "TA0010": "Adversaries steal data from the target network, often using encrypted channels or cloud services to avoid detection.",
    "TA0011": "Compromised systems communicate with attacker-controlled infrastructure to receive commands and exfiltrate data.",
    "TA0040": "In some cases, attackers aim to disrupt availability or destroy data rather than steal it, causing direct operational damage.",
    "TA0042": "Before launching an attack, threat actors develop capabilities, acquire infrastructure, and gather resources.",
    "TA0043": "Adversaries gather information about the target organization to plan and execute future operations.",
}

# Source filenames → human-readable names
_SOURCE_FILE_MAP: dict[str, str] = {
    "owasp_top_10.md": "OWASP Top 10",
    "mitre_attack.md": "MITRE ATT&CK Framework",
    "nist.md": "NIST Cybersecurity Framework",
    "nist_csf.md": "NIST Cybersecurity Framework",
    "cisa.md": "CISA Advisories",
    "sql_injection.md": "OWASP SQL Injection Guide",
    "ransomware.md": "Ransomware Threat Intelligence",
}


# ============================================
# Core Sanitization Functions
# ============================================

def sanitize_article(article: MagazineArticle) -> MagazineArticle:
    """
    Returns a sanitized copy of a MagazineArticle with all
    internal RAG artifacts removed.

    The original article object is NOT modified.
    """
    return MagazineArticle(
        title=_clean_title(article.title),
        executive_summary=sanitize_text(article.executive_summary),
        background=sanitize_text(article.background),
        technical_analysis=sanitize_text(article.technical_analysis),
        impact=sanitize_text(article.impact),
        recommendations=sanitize_text(article.recommendations),
        references=sanitize_references(article.references),
        original_link=article.original_link,
        category=article.category,
        generated_at=article.generated_at,
    )


def sanitize_text(text: str) -> str:
    """
    Master sanitization pipeline for any block of article text.
    Applies all cleaning passes in the correct order.
    """
    if not text:
        return ""

    text = strip_owasp_codes(text)
    text = rewrite_mitre_references(text)
    text = strip_mitre_heading_blocks(text)
    text = clean_rag_separators(text)
    text = strip_source_filenames(text)
    text = strip_vector_metadata(text)
    text = clean_markdown_artifacts(text)
    text = collapse_whitespace(text)

    return text.strip()


def strip_owasp_codes(text: str) -> str:
    """
    Strips OWASP codes (e.g., A01:2021, A02:2021) and CWE numbers.
    """
    # Remove A01:2021 style codes with optional dashes/colons after them
    text = re.sub(r"\bA\d{2}:\d{4}\s*[-–—:]?\s*", "", text)
    # Remove CWE-xxx codes
    text = re.sub(r"\bCWE-\d+\s*[-–—:]?\s*", "", text, flags=re.IGNORECASE)
    return text


# ============================================
# Individual Cleaning Passes
# ============================================

def rewrite_mitre_references(text: str) -> str:
    """
    Replaces MITRE ATT&CK tactic/technique IDs with human descriptions.

    Examples:
        '### Initial Access (TA0001)'
            → 'Threat actors typically gain entry through phishing …'

        'uses T1059 for execution'
            → 'uses scripting techniques for execution'

        'TA0008 - Lateral Movement'
            → 'After compromising one system, attackers move …'
    """
    # Pass 1: Replace heading-style patterns like "### Tactic Name (TAxxxx)"
    def _replace_heading_with_tactic(m: re.Match) -> str:
        tactic_id = m.group(2)
        desc = _TACTIC_DESCRIPTIONS.get(tactic_id)
        if desc:
            return desc
        name = _MITRE_TACTIC_MAP.get(tactic_id, m.group(1))
        return name

    text = re.sub(
        r"#{1,4}\s*(.+?)\s*\(?(TA\d{4})\)?\s*",
        _replace_heading_with_tactic,
        text,
    )

    # Pass 2: Replace standalone "TAxxxx" or "TAxxxx - Name" patterns
    def _replace_standalone_tactic(m: re.Match) -> str:
        tactic_id = m.group(1)
        desc = _TACTIC_DESCRIPTIONS.get(tactic_id)
        if desc:
            return desc
        return _MITRE_TACTIC_MAP.get(tactic_id, "")

    text = re.sub(
        r"\b(TA\d{4})\s*(?:-\s*[\w\s]+)?",
        _replace_standalone_tactic,
        text,
    )

    # Pass 3: Replace technique IDs (T1xxx, T1xxx.xxx)
    text = re.sub(
        r"\bT\d{4}(?:\.\d{3})?\b",
        "",
        text,
    )

    return text


def strip_mitre_heading_blocks(text: str) -> str:
    """
    Removes markdown heading lines that contain MITRE-style content
    but were not already caught by rewrite_mitre_references.
    """
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that are just markdown headings with no real content
        if re.match(r"^#{1,4}\s*$", stripped):
            continue
        # Skip lines that are purely tactic/technique references
        if re.match(r"^#{1,4}\s*(TA|T)\d{3,4}", stripped):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def clean_rag_separators(text: str) -> str:
    """
    Removes chunk-boundary separators inserted during RAG retrieval.
    The RAG agent joins chunks with '\\n\\n---\\n\\n'.
    """
    # Remove --- separators (with surrounding whitespace)
    text = re.sub(r"\n\s*---\s*\n", "\n\n", text)
    # Remove standalone --- lines
    text = re.sub(r"^\s*---\s*$", "", text, flags=re.MULTILINE)
    return text


def strip_source_filenames(text: str) -> str:
    """
    Removes or replaces internal source filenames with
    human-readable framework names.
    """
    for filename, human_name in _SOURCE_FILE_MAP.items():
        # Replace "Source: filename" patterns
        text = re.sub(
            rf"(?:Source|source|From|from):\s*{re.escape(filename)}",
            f"Source: {human_name}",
            text,
        )
        # Replace standalone filename references
        text = text.replace(filename, human_name)

    # Catch any remaining .md file references
    text = re.sub(r"\b[\w_-]+\.md\b", "", text)

    return text


def strip_vector_metadata(text: str) -> str:
    """
    Removes vector database metadata that may leak through.
    """
    # Remove chunk ID references (chunk_0, chunk_42, etc.)
    text = re.sub(r"\bchunk_\d+\b", "", text, flags=re.IGNORECASE)

    # Remove embedding dimension references
    text = re.sub(
        r"\b\d+[- ]?dimensional?\s*(?:vector|embedding)s?\b",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove ChromaDB / vector store references
    text = re.sub(
        r"\b(?:chromadb|chroma|vector\s*(?:store|database|db|index)|"
        r"embedding\s*(?:model|function)|cosine\s*similarity)\b",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove "Retrieved from collection:" style lines
    text = re.sub(
        r"(?:Retrieved|Fetched|Queried)\s+from\s+(?:collection|index|database).*?[\.\n]",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text


def clean_markdown_artifacts(text: str) -> str:
    """
    Cleans up residual markdown formatting artifacts.
    """
    # Remove heading markers (#, ##, ###, ####, etc.) from start of lines
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

    # Remove double-asterisk bold markers
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)

    return text


def sanitize_rag_context_chunks(context_str: str) -> list[str]:
    """
    Splits a joined RAG context string on '---' separators and sanitizes each chunk.
    Strips markdown heading symbols (#, ##, ###), OWASP codes (A01:2021), MITRE IDs (TA0008),
    source filenames, and metadata. Returns a list of clean, readable text blocks.
    """
    if not context_str:
        return []

    # Split on --- separators
    raw_chunks = re.split(r"\n\s*---\s*\n|^\s*---\s*$", context_str, flags=re.MULTILINE)

    cleaned_chunks = []
    for chunk in raw_chunks:
        if not chunk or not chunk.strip():
            continue

        cleaned = sanitize_text(chunk)
        # Ensure all heading symbols are stripped
        cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = collapse_whitespace(cleaned).strip()

        if cleaned:
            cleaned_chunks.append(cleaned)

    return cleaned_chunks


def collapse_whitespace(text: str) -> str:
    """
    Collapses excessive whitespace left by previous cleaning passes.
    """
    # Collapse 3+ consecutive newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove trailing whitespace on each line
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    # Remove leading blank lines
    text = re.sub(r"^\n+", "", text)
    return text


# ============================================
# Specialized Cleaners
# ============================================

def sanitize_references(text: str) -> str:
    """
    Cleans up the references section specifically.
    Replaces source filenames with proper names and formats
    as a clean list.
    """
    if not text:
        return ""

    # First apply general sanitization
    text = strip_source_filenames(text)
    text = strip_vector_metadata(text)
    text = clean_rag_separators(text)

    # Clean up bullet formatting
    lines = text.strip().split("\n")
    cleaned_refs = []
    seen = set()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Remove bullet markers and re-add consistently
        line = re.sub(r"^[-•*]\s*", "", line)
        line = line.strip()

        if not line:
            continue

        # Deduplicate references
        normalized = line.lower().strip()
        if normalized not in seen:
            seen.add(normalized)
            cleaned_refs.append(f"- {line}")

    return "\n".join(cleaned_refs)


def _clean_title(title: str) -> str:
    """
    Cleans article titles — remove technique IDs but
    preserve the meaningful parts.
    """
    if not title:
        return ""

    # Remove MITRE IDs from titles
    title = re.sub(r"\s*\(?(TA|T)\d{3,4}(?:\.\d{3})?\)?\s*", " ", title)
    # Remove source filenames from titles
    for filename in _SOURCE_FILE_MAP:
        title = title.replace(filename, "")
    # Clean up whitespace
    title = re.sub(r"\s{2,}", " ", title).strip()
    return title
