"""
CyberQuill RAG (Retrieval-Augmented Generation) Agent


Purpose:
    Enriches classified articles with relevant context from a cybersecurity
    knowledge base. Before the Writer Agent generates a magazine article,
    this agent retrieves related information from documents like OWASP Top 10,
    NIST CSF, and MITRE ATT&CK to provide deeper technical context.
"""

import re
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from config.settings import settings
from models.schemas import ClassifiedArticle, EnrichedArticle
from utils.logger import get_logger

logger = get_logger(__name__)

# ============================================
# RAG Configuration Constants
# ============================================

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K = 3
RETRIEVAL_CANDIDATES = 5
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "cyberquill_knowledge_base"
EXCLUDED_FILES = {"README.md"}

DOCUMENTS_DIR = Path("data/documents")

CATEGORY_SOURCE_MAP: dict[str, list[str]] = {
    "Malware": ["malware_analysis.md", "ransomware.md", "mitre_attack.md"],
    "Data Breach": [
        "incident_response.md",
        "identity_access_management.md",
        "nist_csf.md",
    ],
    "AI Security": ["ai_security.md"],
    "Cloud Security": [
        "cloud_security.md",
        "container_k8s_security.md",
        "zero_trust_architecture.md",
    ],
    "Zero-Day": ["zero_day_exploits.md", "owasp_top_10.md"],
    "Threat Intelligence": ["threat_intelligence.md", "mitre_attack.md"],
    "Vulnerability Management": [
        "owasp_top_10.md",
        "sql_injection.md",
        "api_security.md",
    ],
}


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML-style frontmatter from markdown content.

    Supports simple key: value and key: [list, items] formats.
    """
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_text = parts[1].strip()
    body = parts[2].strip()
    metadata: dict = {}

    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [
                item.strip().strip("'\"")
                for item in value[1:-1].split(",")
                if item.strip()
            ]
            metadata[key] = items
        else:
            metadata[key] = value.strip("'\"")

    return metadata, body


def _load_documents(documents_dir: Path = DOCUMENTS_DIR) -> list[dict]:
    """
    Loads knowledge base markdown documents with parsed frontmatter.

    Skips README.md and files without a title in frontmatter.
    """
    documents = []
    supported_extensions = {".md", ".txt"}

    if not documents_dir.exists():
        logger.warning(f"Documents directory not found: {documents_dir}")
        return []

    for filepath in sorted(documents_dir.iterdir()):
        if filepath.name in EXCLUDED_FILES:
            continue
        if filepath.suffix.lower() not in supported_extensions:
            continue

        try:
            content = filepath.read_text(encoding="utf-8")
            if not content.strip():
                continue

            frontmatter, body = _parse_frontmatter(content)
            if not frontmatter.get("title"):
                logger.warning(
                    f"Skipping {filepath.name}: missing title in frontmatter"
                )
                continue

            documents.append({
                "filename": filepath.name,
                "content": body,
                "frontmatter": frontmatter,
            })
            logger.info(
                f"Loaded document: {filepath.name} "
                f"({len(body)} characters)"
            )
        except Exception as e:
            logger.warning(f"Failed to load {filepath.name}: {e}")

    logger.info(f"Loaded {len(documents)} documents from {documents_dir}")
    return documents


def _chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Splits text into overlapping chunks of a specified size."""
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            space_pos = text.rfind(" ", start, end)
            if space_pos > start:
                end = space_pos

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap if end < len(text) else len(text)

    return chunks


def _chunk_by_sections(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[tuple[str, str]]:
    """
    Split text by ## headings first, then sub-chunk large sections.

    Returns list of (section_name, chunk_text) tuples.
    """
    if not text.strip():
        return []

    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    if len(sections) == 1 and not sections[0].strip().startswith("##"):
        sub_chunks = _chunk_text(text, chunk_size, chunk_overlap)
        return [("Overview", chunk) for chunk in sub_chunks]

    chunks: list[tuple[str, str]] = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        first_line = section.split("\n", 1)[0]
        if first_line.startswith("#"):
            section_name = first_line.lstrip("#").strip()
            section_body = section
        else:
            section_name = "Overview"
            section_body = section

        if len(section_body) <= chunk_size:
            chunks.append((section_name, section_body))
        else:
            for sub_chunk in _chunk_text(section_body, chunk_size, chunk_overlap):
                chunks.append((section_name, sub_chunk))

    return chunks


def _chunk_documents(
    documents: list[dict],
) -> tuple[list[str], list[dict]]:
    """Chunks all documents with heading-aware splitting and rich metadata."""
    all_chunks: list[str] = []
    all_metadata: list[dict] = []

    for doc in documents:
        frontmatter = doc.get("frontmatter", {})
        categories = frontmatter.get("categories", [])
        keywords = frontmatter.get("keywords", [])
        frameworks = frontmatter.get("frameworks", [])

        section_chunks = _chunk_by_sections(doc["content"])
        for section_name, chunk in section_chunks:
            all_chunks.append(chunk)
            all_metadata.append({
                "source": doc["filename"],
                "section": section_name,
                "categories": ", ".join(categories) if categories else "",
                "keywords": ", ".join(keywords) if keywords else "",
                "frameworks": ", ".join(frameworks) if frameworks else "",
            })

    logger.info(
        f"Created {len(all_chunks)} chunks from {len(documents)} documents"
    )
    return all_chunks, all_metadata


def _get_embedding_function():
    """Creates the embedding function used by ChromaDB."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )


def build_knowledge_base(
    documents_dir: Path = DOCUMENTS_DIR,
    persist_dir: str = None,
) -> chromadb.Collection:
    """Builds (or rebuilds) the vector knowledge base from documents."""
    persist_path = persist_dir or settings.CHROMA_PERSIST_DIR

    logger.info("Building knowledge base...")

    documents = _load_documents(documents_dir)
    if not documents:
        logger.warning("No documents found. Knowledge base will be empty.")

    chunks, metadata = _chunk_documents(documents)

    client = chromadb.PersistentClient(path=persist_path)
    embedding_fn = _get_embedding_function()

    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info(f"Deleted existing collection: {COLLECTION_NAME}")
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"description": "CyberQuill cybersecurity knowledge base"},
    )

    if chunks:
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        collection.add(
            documents=chunks,
            metadatas=metadata,
            ids=ids,
        )
        logger.info(
            f"Knowledge base built: {len(chunks)} chunks indexed "
            f"from {len(documents)} documents"
        )
    else:
        logger.warning("No chunks to index. Knowledge base is empty.")

    return collection


def _get_collection(persist_dir: str = None) -> chromadb.Collection:
    """Gets the existing ChromaDB collection (without rebuilding)."""
    persist_path = persist_dir or settings.CHROMA_PERSIST_DIR
    client = chromadb.PersistentClient(path=persist_path)
    embedding_fn = _get_embedding_function()

    try:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
        )
        return collection
    except Exception:
        logger.warning(
            "Knowledge base not found. Building from documents..."
        )
        return build_knowledge_base(persist_dir=persist_path)


def _deduplicate_chunks(
    chunks: list[str],
    metadatas: list[dict],
    max_chunks: int = TOP_K,
) -> tuple[str, list[str]]:
    """Deduplicate by source file and return combined context."""
    seen_sources: set[str] = set()
    selected_chunks: list[str] = []
    sources: list[str] = []

    for chunk, meta in zip(chunks, metadatas):
        source = meta.get("source", "Unknown")
        if source in seen_sources:
            continue
        seen_sources.add(source)
        selected_chunks.append(chunk)
        sources.append(source)
        if len(selected_chunks) >= max_chunks:
            break

    context = "\n\n---\n\n".join(selected_chunks)
    return context, sources


def retrieve_context(
    query: str,
    top_k: int = TOP_K,
    category: str = "",
    persist_dir: str = None,
) -> tuple[str, list[str]]:
    """
    Retrieves relevant context from the knowledge base for a given query.

    Uses category-boosted retrieval when a category mapping exists.
    """
    collection = _get_collection(persist_dir=persist_dir)

    if collection.count() == 0:
        logger.warning("Knowledge base is empty. No context to retrieve.")
        return "", []

    candidate_k = max(RETRIEVAL_CANDIDATES, top_k)
    preferred_sources = CATEGORY_SOURCE_MAP.get(category, [])

    chunks: list[str] = []
    metadatas: list[dict] = []

    if preferred_sources:
        for source in preferred_sources:
            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=min(2, collection.count()),
                    where={"source": source},
                )
                if results["documents"] and results["documents"][0]:
                    chunks.extend(results["documents"][0])
                    metadatas.extend(results["metadatas"][0])
            except Exception as e:
                logger.debug(f"Category-filtered query failed for {source}: {e}")

    remaining = candidate_k - len(chunks)
    if remaining > 0:
        results = collection.query(
            query_texts=[query],
            n_results=min(remaining, collection.count()),
        )
        if results["documents"] and results["documents"][0]:
            for chunk, meta in zip(
                results["documents"][0], results["metadatas"][0]
            ):
                if chunk not in chunks:
                    chunks.append(chunk)
                    metadatas.append(meta)

    if not chunks:
        return "", []

    context, sources = _deduplicate_chunks(chunks, metadatas, max_chunks=top_k)

    logger.debug(
        f"Retrieved {len(sources)} unique sources "
        f"for query: '{query[:50]}...'"
    )

    return context, sources


def retrieve_chunks_with_metadata(
    query: str,
    top_k: int = TOP_K,
    category: str = "",
    persist_dir: str = None,
) -> list[dict]:
    """
    Retrieves chunks with full metadata for UI display and debugging.

    Returns list of dicts with keys: text, source, section, categories, frameworks.
    """
    collection = _get_collection(persist_dir=persist_dir)

    if collection.count() == 0:
        return []

    candidate_k = max(RETRIEVAL_CANDIDATES, top_k)
    preferred_sources = CATEGORY_SOURCE_MAP.get(category, [])

    chunks: list[str] = []
    metadatas: list[dict] = []

    if preferred_sources:
        for source in preferred_sources:
            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=min(2, collection.count()),
                    where={"source": source},
                )
                if results["documents"] and results["documents"][0]:
                    for chunk, meta in zip(
                        results["documents"][0], results["metadatas"][0]
                    ):
                        if chunk not in chunks:
                            chunks.append(chunk)
                            metadatas.append(meta)
            except Exception as e:
                logger.debug(f"Category-filtered query failed for {source}: {e}")

    remaining = candidate_k - len(chunks)
    if remaining > 0:
        results = collection.query(
            query_texts=[query],
            n_results=min(remaining, collection.count()),
        )
        if results["documents"] and results["documents"][0]:
            for chunk, meta in zip(
                results["documents"][0], results["metadatas"][0]
            ):
                if chunk not in chunks:
                    chunks.append(chunk)
                    metadatas.append(meta)

    seen_sources: set[str] = set()
    output: list[dict] = []
    for chunk, meta in zip(chunks, metadatas):
        source = meta.get("source", "Unknown")
        if source in seen_sources:
            continue
        seen_sources.add(source)
        output.append({
            "text": chunk,
            "source": source,
            "section": meta.get("section", ""),
            "categories": meta.get("categories", ""),
            "frameworks": meta.get("frameworks", ""),
        })
        if len(output) >= top_k:
            break

    return output


def enrich_article(
    article: ClassifiedArticle,
    persist_dir: str = None,
) -> EnrichedArticle:
    """Enriches a single classified article with RAG context."""
    query = f"{article.category} {article.title} {article.summary}"

    context, sources = retrieve_context(
        query,
        category=article.category,
        persist_dir=persist_dir,
    )

    return EnrichedArticle(
        title=article.title,
        link=article.link,
        source=article.source,
        published=article.published,
        summary=article.summary,
        category=article.category,
        confidence=article.confidence,
        rag_context=context,
        rag_sources=sources,
    )


def enrich_articles(
    articles: list[ClassifiedArticle],
    persist_dir: str = None,
) -> list[EnrichedArticle]:
    """Enriches a list of classified articles with RAG context."""
    if not articles:
        logger.info("No articles to enrich")
        return []

    logger.info(f"Enriching {len(articles)} articles with RAG context...")

    enriched = []
    for article in articles:
        enriched_article = enrich_article(article, persist_dir=persist_dir)
        enriched.append(enriched_article)

        logger.debug(
            f"Enriched: '{article.title[:50]}...' "
            f"({len(enriched_article.rag_context)} chars context, "
            f"{len(enriched_article.rag_sources)} sources)"
        )

    logger.info(f"Enrichment complete. {len(enriched)} articles enriched.")
    return enriched


def rag_node(state: dict) -> dict:
    """LangGraph node function for the RAG Agent."""
    logger.info("RAG Agent starting...")

    try:
        _get_collection()
    except Exception:
        logger.info("Building knowledge base for the first time...")
        build_knowledge_base()

    classified_articles = state.get("classified_articles", [])
    enriched_articles = enrich_articles(classified_articles)

    logger.info(
        f"RAG Agent finished. Enriched {len(enriched_articles)} articles."
    )

    return {
        "enriched_articles": enriched_articles,
        "current_stage": "enrichment_complete",
    }
