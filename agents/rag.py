"""
CyberQuill RAG (Retrieval-Augmented Generation) Agent
=======================================================

Purpose:
    Enriches classified articles with relevant context from a cybersecurity
    knowledge base. Before the Writer Agent generates a magazine article,
    this agent retrieves related information from documents like OWASP Top 10,
    NIST CSF, and MITRE ATT&CK to provide deeper technical context.

What is RAG?
    RAG = Retrieval-Augmented Generation. Instead of relying solely on the
    LLM's training data (which may be outdated), we:
    1. Store our own documents in a vector database
    2. When we need to write about a topic, RETRIEVE relevant chunks
    3. Pass those chunks to the LLM alongside the article
    4. The LLM GENERATES a better article using this extra context

    Why is this better than just using the LLM alone?
    - The LLM's training data has a cutoff date
    - Our knowledge base contains the latest frameworks and advisories
    - We can control exactly what context the LLM sees
    - It reduces hallucinations (the LLM invents fewer facts)

How it works (step by step):
    1. LOAD documents from data/documents/ (markdown files)
    2. CHUNK documents into smaller pieces (500 chars each)
    3. EMBED each chunk into a vector (using sentence-transformers)
    4. STORE vectors in ChromaDB (a vector database)
    5. When enriching an article:
       a. Convert the article title+summary into a query vector
       b. Find the top-k most similar chunks in ChromaDB
       c. Return those chunks as context for the Writer Agent

Inputs:
    - List[ClassifiedArticle] — articles from the Classification Agent
    - Knowledge base documents in data/documents/

Outputs:
    - List[EnrichedArticle] — articles with RAG context added

Dependencies:
    - chromadb: Vector database for storing and searching embeddings
    - sentence-transformers: Generates text embeddings
    - models.schemas: ClassifiedArticle, EnrichedArticle
    - config.settings: ChromaDB configuration
    - utils.logger: Logging

RAG Configuration:
    - Chunk size: 500 characters
    - Chunk overlap: 100 characters
    - Embedding model: all-MiniLM-L6-v2
    - Top-k retrieval: 3 chunks per query
    - Distance metric: cosine similarity

    Why these values?
    - Chunk size 500: Large enough to contain meaningful context,
      small enough to be specific. Larger chunks waste LLM tokens.
    - Overlap 100: Prevents cutting sentences in half at chunk boundaries.
    - all-MiniLM-L6-v2: Fast, small (80MB), good quality for English text.
      A good balance between speed and accuracy.
    - Top-k 3: More chunks = more context but more tokens. 3 is the sweet spot.

Testing strategy:
    - Test document loading (read markdown files)
    - Test chunking (correct sizes and overlap)
    - Test ChromaDB indexing (store and retrieve)
    - Test retrieval quality (relevant chunks for a query)
    - 5 example queries for retrieval evaluation

Possible improvements:
    - Add metadata filtering (e.g., only retrieve from OWASP for web vulns)
    - Implement hybrid search (keyword + semantic)
    - Add re-ranking of retrieved chunks
    - Support PDF document loading
    - Add incremental indexing (only re-index new documents)
"""

import os
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

CHUNK_SIZE = 500          # Characters per chunk
CHUNK_OVERLAP = 100       # Overlap between consecutive chunks
TOP_K = 3                 # Number of chunks to retrieve per query
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence transformer model
COLLECTION_NAME = "cyberquill_knowledge_base"

# Path to knowledge base documents
DOCUMENTS_DIR = Path("data/documents")


def _load_documents(documents_dir: Path = DOCUMENTS_DIR) -> list[dict]:
    """
    Loads all markdown documents from the knowledge base directory.

    How it works:
        1. Scans the documents directory for .md and .txt files
        2. Reads each file's content
        3. Returns a list of dicts with filename and content

    Args:
        documents_dir: Path to the directory containing knowledge base documents

    Returns:
        List of dicts: [{"filename": "owasp_top_10.md", "content": "..."}]

    Why only .md and .txt?
        These are plain text formats that don't need special parsers.
        PDF support could be added later with PyPDF2 or pdfplumber.
    """
    documents = []
    supported_extensions = {".md", ".txt"}

    if not documents_dir.exists():
        logger.warning(f"Documents directory not found: {documents_dir}")
        return []

    for filepath in sorted(documents_dir.iterdir()):
        if filepath.suffix.lower() in supported_extensions:
            try:
                content = filepath.read_text(encoding="utf-8")
                if content.strip():  # Skip empty files
                    documents.append({
                        "filename": filepath.name,
                        "content": content,
                    })
                    logger.info(
                        f"Loaded document: {filepath.name} "
                        f"({len(content)} characters)"
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
    """
    Splits text into overlapping chunks of a specified size.

    Why chunk?
        - Embedding models have input length limits
        - Smaller chunks are more specific → better retrieval precision
        - Large documents would dilute the meaning in a single embedding

    Why overlap?
        Without overlap, we might cut a sentence in half:
        Chunk 1: "...SQL injection is a technique where an attacker"
        Chunk 2: "sends malicious SQL code to the database..."
        With overlap, Chunk 2 starts earlier and captures the full sentence.

    How it works:
        Text: "AAAA BBBB CCCC DDDD EEEE FFFF"
        Chunk size: 10, Overlap: 3
        Chunk 1: "AAAA BBBB " (positions 0-9)
        Chunk 2: "BB CCCC DD" (positions 7-16, overlaps 3 chars)
        Chunk 3: "DD EEEE FF" (positions 14-23, overlaps 3 chars)

    Args:
        text: The full text to chunk
        chunk_size: Maximum characters per chunk
        chunk_overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Don't cut in the middle of a word — find the nearest space
        if end < len(text):
            # Look backwards from 'end' to find a space
            space_pos = text.rfind(" ", start, end)
            if space_pos > start:
                end = space_pos

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move forward by (chunk_size - overlap) characters
        start = end - chunk_overlap if end < len(text) else len(text)

    return chunks


def _chunk_documents(documents: list[dict]) -> tuple[list[str], list[dict]]:
    """
    Chunks all documents and prepares metadata for ChromaDB.

    Args:
        documents: List of {"filename": ..., "content": ...} dicts

    Returns:
        Tuple of (chunks_list, metadata_list)
        - chunks_list: List of text chunks
        - metadata_list: List of {"source": filename} dicts (one per chunk)

    Why separate metadata?
        ChromaDB stores metadata alongside each vector. When we retrieve
        a chunk, we also get its metadata, so we know WHICH document
        the chunk came from. This is useful for the references section.
    """
    all_chunks = []
    all_metadata = []

    for doc in documents:
        chunks = _chunk_text(doc["content"])
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadata.append({"source": doc["filename"]})

    logger.info(
        f"Created {len(all_chunks)} chunks from {len(documents)} documents"
    )
    return all_chunks, all_metadata


def _get_embedding_function():
    """
    Creates the embedding function used by ChromaDB.

    Uses SentenceTransformerEmbeddingFunction which wraps the
    sentence-transformers library. The model is downloaded on first use
    and cached locally.

    Model: all-MiniLM-L6-v2
        - Size: ~80MB
        - Dimensions: 384
        - Speed: Fast (can embed hundreds of texts per second)
        - Quality: Good for English text similarity tasks
        - Why this model? Best balance of speed, size, and quality
          for a project that runs on Streamlit Community Cloud (1GB RAM limit)

    Returns:
        A ChromaDB-compatible embedding function
    """
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )


def build_knowledge_base(
    documents_dir: Path = DOCUMENTS_DIR,
    persist_dir: str = None,
) -> chromadb.Collection:
    """
    Builds (or rebuilds) the vector knowledge base from documents.

    This is the INDEXING step of RAG:
        1. Load documents from disk
        2. Chunk them into smaller pieces
        3. Create embeddings and store in ChromaDB

    Args:
        documents_dir: Path to the knowledge base documents
        persist_dir: Directory to persist ChromaDB data.
                     If None, uses settings.CHROMA_PERSIST_DIR

    Returns:
        ChromaDB Collection object (ready for queries)

    When to call this:
        - Once during initial setup
        - When new documents are added to the knowledge base
        - The Streamlit UI will have a "Rebuild Knowledge Base" button
    """
    persist_path = persist_dir or settings.CHROMA_PERSIST_DIR

    logger.info("Building knowledge base...")

    # Step 1: Load documents
    documents = _load_documents(documents_dir)
    if not documents:
        logger.warning("No documents found. Knowledge base will be empty.")

    # Step 2: Chunk documents
    chunks, metadata = _chunk_documents(documents)

    # Step 3: Create ChromaDB client and collection
    client = chromadb.PersistentClient(path=persist_path)
    embedding_fn = _get_embedding_function()

    # Delete existing collection if it exists (rebuild from scratch)
    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info(f"Deleted existing collection: {COLLECTION_NAME}")
    except Exception:
        pass  # Collection didn't exist — that's fine

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"description": "CyberQuill cybersecurity knowledge base"},
    )

    # Step 4: Add chunks to collection
    if chunks:
        # ChromaDB requires unique IDs for each document
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
    """
    Gets the existing ChromaDB collection (without rebuilding).

    Args:
        persist_dir: Directory where ChromaDB data is persisted

    Returns:
        ChromaDB Collection object

    Raises:
        ValueError: If the collection doesn't exist (need to build first)
    """
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


def retrieve_context(
    query: str,
    top_k: int = TOP_K,
    persist_dir: str = None,
) -> tuple[str, list[str]]:
    """
    Retrieves relevant context from the knowledge base for a given query.

    This is the RETRIEVAL step of RAG:
        1. Convert the query into an embedding vector
        2. Search ChromaDB for the top-k most similar chunks
        3. Return the chunks as context text

    Args:
        query: The search query (usually article title + summary)
        top_k: Number of chunks to retrieve
        persist_dir: ChromaDB persist directory

    Returns:
        Tuple of (context_text, source_list)
        - context_text: Combined text of retrieved chunks
        - source_list: List of source document filenames

    How similarity search works:
        ChromaDB converts the query into a vector (384 dimensions)
        and finds the vectors in the database that are closest to it
        using cosine similarity. Closer vectors = more relevant content.
    """
    collection = _get_collection(persist_dir=persist_dir)

    # Check if collection has any data
    if collection.count() == 0:
        logger.warning("Knowledge base is empty. No context to retrieve.")
        return "", []

    # Query ChromaDB
    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count()),
    )

    # Extract chunks and sources from results
    chunks = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    sources = list({m.get("source", "Unknown") for m in metadatas})

    # Combine chunks into a single context string
    context = "\n\n---\n\n".join(chunks)

    logger.debug(
        f"Retrieved {len(chunks)} chunks from {len(sources)} sources "
        f"for query: '{query[:50]}...'"
    )

    return context, sources


def enrich_article(
    article: ClassifiedArticle,
    persist_dir: str = None,
) -> EnrichedArticle:
    """
    Enriches a single classified article with RAG context.

    Takes the article's title and summary, queries the knowledge base,
    and creates an EnrichedArticle with the retrieved context.

    Args:
        article: A ClassifiedArticle to enrich
        persist_dir: ChromaDB persist directory

    Returns:
        An EnrichedArticle with rag_context and rag_sources added
    """
    # Build query from article title and summary
    query = f"{article.title} {article.summary}"

    # Retrieve relevant context
    context, sources = retrieve_context(query, persist_dir=persist_dir)

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
    """
    Enriches a list of classified articles with RAG context.

    This is the main entry point for the RAG Agent.

    Args:
        articles: List of ClassifiedArticle objects
        persist_dir: ChromaDB persist directory

    Returns:
        List of EnrichedArticle objects with context added

    Example:
        >>> from agents.rag import enrich_articles, build_knowledge_base
        >>> build_knowledge_base()  # Run once
        >>> enriched = enrich_articles(classified_articles)
    """
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


# ============================================
# LangGraph Node Function
# ============================================

def rag_node(state: dict) -> dict:
    """
    LangGraph node function for the RAG Agent.

    Reads classified_articles from state, enriches each one with
    RAG context, and writes enriched_articles back to state.

    Also ensures the knowledge base is built before enrichment.

    Args:
        state: The current pipeline state dictionary

    Returns:
        Dictionary with state updates:
        - "enriched_articles": list of EnrichedArticle objects
        - "current_stage": updated to "enrichment_complete"
    """
    logger.info("RAG Agent starting...")

    # Ensure knowledge base exists
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
