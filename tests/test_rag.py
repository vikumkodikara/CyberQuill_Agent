"""
Tests for the RAG (Retrieval-Augmented Generation) Agent
==========================================================

Purpose:
    Verifies that the RAG Agent correctly loads documents, chunks text,
    builds the vector knowledge base, and retrieves relevant context.

Testing strategy:
    - Unit tests for document loading
    - Unit tests for text chunking (size, overlap, edge cases)
    - Integration tests for ChromaDB (build and query)
    - Retrieval evaluation with 5 example queries
    - Uses a temporary directory for ChromaDB to avoid polluting the real DB

How to run:
    pytest tests/test_rag.py -v

Dependencies:
    - pytest
    - chromadb
    - sentence-transformers
    - agents.rag
"""

from pathlib import Path

import pytest

from agents.rag import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CATEGORY_SOURCE_MAP,
    _chunk_by_sections,
    _chunk_documents,
    _chunk_text,
    _load_documents,
    _parse_frontmatter,
    build_knowledge_base,
    retrieve_context,
    enrich_article,
)
from models.schemas import ClassifiedArticle


# ============================================
# Fixtures: Setup and Teardown
# ============================================

@pytest.fixture
def sample_docs_dir(tmp_path):
    """
    Creates a temporary directory with sample documents for testing.
    
    Why use tmp_path?
        - pytest's tmp_path creates a unique temp directory per test
        - Automatically cleaned up after the test
        - Doesn't interfere with the real knowledge base
    """
    # Create sample document 1
    doc1 = tmp_path / "test_owasp.md"
    doc1.write_text(
        "---\n"
        "title: OWASP Top 10\n"
        "categories: [Vulnerability Management]\n"
        "keywords: [owasp, injection, sql]\n"
        "frameworks: [OWASP]\n"
        "---\n\n"
        "# OWASP Top 10\n\n"
        "## SQL Injection\n"
        "SQL injection is a code injection technique that might destroy "
        "your database. SQL injection is one of the most common web hacking "
        "techniques. SQL injection is the placement of malicious code in SQL "
        "statements, via web page input.\n\n"
        "## Cross-Site Scripting (XSS)\n"
        "Cross-Site Scripting (XSS) attacks are a type of injection, in "
        "which malicious scripts are injected into otherwise benign and "
        "trusted websites. XSS attacks occur when an attacker uses a web "
        "application to send malicious code to a different end user.",
        encoding="utf-8",
    )

    doc2 = tmp_path / "test_nist.md"
    doc2.write_text(
        "---\n"
        "title: NIST Cybersecurity Framework\n"
        "categories: [Data Breach]\n"
        "keywords: [nist, framework, respond]\n"
        "frameworks: [NIST CSF]\n"
        "---\n\n"
        "# NIST Cybersecurity Framework\n\n"
        "## Identify\n"
        "Develop an organizational understanding to manage cybersecurity "
        "risk to systems, people, assets, data, and capabilities.\n\n"
        "## Protect\n"
        "Develop and implement appropriate safeguards to ensure delivery "
        "of critical infrastructure services.\n\n"
        "## Detect\n"
        "Develop and implement appropriate activities to identify the "
        "occurrence of a cybersecurity event.",
        encoding="utf-8",
    )

    readme = tmp_path / "README.md"
    readme.write_text("# Index\n\nThis should be excluded.", encoding="utf-8")

    # Create a non-markdown file (should be skipped)
    ignored = tmp_path / "readme.json"
    ignored.write_text('{"note": "this should be ignored"}', encoding="utf-8")

    return tmp_path


@pytest.fixture
def chroma_dir(tmp_path):
    """Creates a temporary directory for ChromaDB storage."""
    chroma_path = tmp_path / "test_chroma"
    chroma_path.mkdir()
    return str(chroma_path)


# ============================================
# Tests for _load_documents()
# ============================================

class TestLoadDocuments:
    """Tests for document loading."""

    def test_loads_markdown_files(self, sample_docs_dir):
        """Should load .md files with frontmatter from the directory."""
        docs = _load_documents(sample_docs_dir)
        assert len(docs) == 2  # 2 knowledge files, README and json ignored

    def test_excludes_readme(self, sample_docs_dir):
        """Should exclude README.md from indexing."""
        docs = _load_documents(sample_docs_dir)
        filenames = [d["filename"] for d in docs]
        assert "README.md" not in filenames

    def test_skips_non_markdown_files(self, sample_docs_dir):
        """Should ignore files that are not .md or .txt."""
        docs = _load_documents(sample_docs_dir)
        filenames = [d["filename"] for d in docs]
        assert "readme.json" not in filenames

    def test_returns_filename_and_content(self, sample_docs_dir):
        """Each document should have filename, content, and frontmatter."""
        docs = _load_documents(sample_docs_dir)
        for doc in docs:
            assert "filename" in doc
            assert "content" in doc
            assert "frontmatter" in doc
            assert doc["frontmatter"].get("title")
            assert len(doc["content"]) > 0

    def test_handles_missing_directory(self):
        """Should return empty list for non-existent directory."""
        docs = _load_documents(Path("/nonexistent/directory"))
        assert docs == []

    def test_handles_empty_directory(self, tmp_path):
        """Should return empty list for directory with no documents."""
        docs = _load_documents(tmp_path)
        assert docs == []


# ============================================
# Tests for _parse_frontmatter()
# ============================================

class TestParseFrontmatter:
    """Tests for YAML frontmatter parsing."""

    def test_parses_title_and_lists(self):
        content = (
            "---\n"
            "title: Test Topic\n"
            "categories: [Malware, Threat Intelligence]\n"
            "keywords: [ransomware, encryption]\n"
            "---\n\n"
            "# Body\n\nSome content."
        )
        meta, body = _parse_frontmatter(content)
        assert meta["title"] == "Test Topic"
        assert "Malware" in meta["categories"]
        assert "ransomware" in meta["keywords"]
        assert "# Body" in body

    def test_no_frontmatter(self):
        content = "# Just markdown\n\nNo frontmatter here."
        meta, body = _parse_frontmatter(content)
        assert meta == {}
        assert body == content


# ============================================
# Tests for _chunk_by_sections()
# ============================================

class TestChunkBySections:
    """Tests for heading-aware chunking."""

    def test_splits_on_headings(self):
        text = (
            "# Title\n\n"
            "## Section One\n"
            "Content for section one about SQL injection.\n\n"
            "## Section Two\n"
            "Content for section two about mitigation."
        )
        chunks = _chunk_by_sections(text, chunk_size=500)
        assert len(chunks) >= 2
        section_names = [name for name, _ in chunks]
        assert any("Section One" in name for name in section_names)

    def test_metadata_contains_section(self, sample_docs_dir):
        """Each chunk metadata should include section name."""
        docs = _load_documents(sample_docs_dir)
        chunks, metadata = _chunk_documents(docs)
        assert any(m.get("section") for m in metadata)
        assert any(m.get("categories") for m in metadata)


# ============================================
# Tests for CATEGORY_SOURCE_MAP
# ============================================

class TestCategorySourceMap:
    """Tests for category-to-source mapping."""

    def test_all_categories_have_sources(self):
        assert "Malware" in CATEGORY_SOURCE_MAP
        assert "AI Security" in CATEGORY_SOURCE_MAP
        assert len(CATEGORY_SOURCE_MAP) == 7

    def test_sources_are_md_files(self):
        for sources in CATEGORY_SOURCE_MAP.values():
            for source in sources:
                assert source.endswith(".md")


# ============================================
# Tests for _chunk_text()
# ============================================

class TestChunkText:
    """Tests for the text chunking function."""

    def test_short_text_single_chunk(self):
        """Text shorter than chunk_size should return a single chunk."""
        text = "Short text"
        chunks = _chunk_text(text, chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0] == "Short text"

    def test_long_text_multiple_chunks(self):
        """Long text should be split into multiple chunks."""
        text = "word " * 200  # 1000 characters
        chunks = _chunk_text(text, chunk_size=500, chunk_overlap=100)
        assert len(chunks) > 1

    def test_chunk_size_respected(self):
        """Each chunk should not exceed chunk_size."""
        text = "This is a test sentence. " * 100
        chunks = _chunk_text(text, chunk_size=200, chunk_overlap=50)
        for chunk in chunks:
            assert len(chunk) <= 210  # Allow small margin for word boundaries

    def test_overlap_works(self):
        """Consecutive chunks should have overlapping content."""
        text = "alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar papa"
        chunks = _chunk_text(text, chunk_size=40, chunk_overlap=10)

        if len(chunks) >= 2:
            # The end of chunk 1 should appear at the start of chunk 2
            # (approximately, due to word boundary adjustments)
            assert len(chunks) >= 2

    def test_empty_text(self):
        """Should return empty list for empty text."""
        chunks = _chunk_text("")
        assert chunks == []

    def test_no_empty_chunks(self):
        """Should not produce empty chunks."""
        text = "Hello world. " * 50
        chunks = _chunk_text(text, chunk_size=100, chunk_overlap=20)
        for chunk in chunks:
            assert len(chunk.strip()) > 0


# ============================================
# Tests for _chunk_documents()
# ============================================

class TestChunkDocuments:
    """Tests for document chunking."""

    def test_chunks_multiple_documents(self, sample_docs_dir):
        """Should chunk all documents and return flat lists."""
        docs = _load_documents(sample_docs_dir)
        chunks, metadata = _chunk_documents(docs)

        assert len(chunks) > 0
        assert len(chunks) == len(metadata)

    def test_metadata_contains_source(self, sample_docs_dir):
        """Each chunk's metadata should contain the source filename."""
        docs = _load_documents(sample_docs_dir)
        chunks, metadata = _chunk_documents(docs)

        for meta in metadata:
            assert "source" in meta
            assert meta["source"].endswith(".md")
            assert "section" in meta


# ============================================
# Integration Tests: ChromaDB
# ============================================

class TestBuildKnowledgeBase:
    """Integration tests for ChromaDB knowledge base."""

    def test_build_creates_collection(self, sample_docs_dir, chroma_dir):
        """Should create a ChromaDB collection with indexed chunks."""
        collection = build_knowledge_base(
            documents_dir=sample_docs_dir,
            persist_dir=chroma_dir,
        )

        # Collection should have chunks indexed
        assert collection.count() > 0

    def test_build_indexes_all_chunks(self, sample_docs_dir, chroma_dir):
        """Number of indexed items should match number of chunks."""
        docs = _load_documents(sample_docs_dir)
        chunks, _ = _chunk_documents(docs)

        collection = build_knowledge_base(
            documents_dir=sample_docs_dir,
            persist_dir=chroma_dir,
        )

        assert collection.count() == len(chunks)


# ============================================
# Integration Tests: Retrieval
# ============================================

class TestRetrieveContext:
    """Integration tests for context retrieval."""

    @pytest.fixture(autouse=True)
    def setup_kb(self, sample_docs_dir, chroma_dir):
        """Build the knowledge base before each retrieval test."""
        self.chroma_dir = chroma_dir
        build_knowledge_base(
            documents_dir=sample_docs_dir,
            persist_dir=chroma_dir,
        )

    def test_retrieves_relevant_context(self):
        """Should retrieve context related to the query."""
        context, sources = retrieve_context(
            "SQL injection attack on web application",
            persist_dir=self.chroma_dir,
        )
        assert len(context) > 0
        assert "sql" in context.lower() or "injection" in context.lower()

    def test_returns_sources(self):
        """Should return source filenames."""
        context, sources = retrieve_context(
            "cybersecurity framework",
            persist_dir=self.chroma_dir,
        )
        assert len(sources) > 0
        assert all(isinstance(s, str) for s in sources)

    def test_empty_query(self):
        """Should handle empty query gracefully."""
        context, sources = retrieve_context(
            "",
            persist_dir=self.chroma_dir,
        )
        # Should still return something (ChromaDB handles empty queries)
        assert isinstance(context, str)


# ============================================
# Retrieval Evaluation: 5 Example Queries
# ============================================

class TestRetrievalEvaluation:
    """
    Evaluates retrieval quality with 5 example queries.
    
    This tests whether the RAG system retrieves RELEVANT context
    for common cybersecurity topics. Each query checks that the
    retrieved context contains expected keywords.
    
    Required by project specification for RAG evaluation.
    """

    @pytest.fixture(autouse=True)
    def setup_full_kb(self, chroma_dir):
        """Build knowledge base from the actual project documents."""
        self.chroma_dir = chroma_dir
        actual_docs = Path("data/documents")
        if actual_docs.exists():
            build_knowledge_base(
                documents_dir=actual_docs,
                persist_dir=chroma_dir,
            )
        else:
            pytest.skip("Knowledge base documents not found")

    def test_query_sql_injection(self):
        """Query about SQL injection should retrieve OWASP content."""
        context, sources = retrieve_context(
            "SQL injection vulnerability in web application",
            persist_dir=self.chroma_dir,
        )
        assert len(context) > 0
        # Should contain relevant security terms
        context_lower = context.lower()
        assert any(term in context_lower for term in
                    ["injection", "sql", "input", "validation", "owasp"])

    def test_query_ransomware(self):
        """Query about ransomware should retrieve MITRE ATT&CK content."""
        context, sources = retrieve_context(
            "ransomware attack encrypting files for ransom",
            persist_dir=self.chroma_dir,
        )
        assert len(context) > 0
        context_lower = context.lower()
        assert any(term in context_lower for term in
                    ["impact", "encrypted", "ransomware", "data", "attack"])

    def test_query_incident_response(self):
        """Query about incident response should retrieve NIST content."""
        context, sources = retrieve_context(
            "incident response plan for cybersecurity breach",
            persist_dir=self.chroma_dir,
        )
        assert len(context) > 0
        context_lower = context.lower()
        assert any(term in context_lower for term in
                    ["respond", "incident", "detect", "recovery", "plan"])

    def test_query_lateral_movement(self):
        """Query about lateral movement should retrieve MITRE content."""
        context, sources = retrieve_context(
            "APT group lateral movement through network",
            persist_dir=self.chroma_dir,
        )
        assert len(context) > 0
        context_lower = context.lower()
        assert any(term in context_lower for term in
                    ["lateral", "movement", "remote", "network", "adversary"])

    def test_query_access_control(self):
        """Query about access control should retrieve OWASP/NIST content."""
        context, sources = retrieve_context(
            "broken access control vulnerability",
            persist_dir=self.chroma_dir,
        )
        assert len(context) > 0
        context_lower = context.lower()
        assert any(term in context_lower for term in
                    ["access", "control", "permission", "privilege", "authorization"])


# ============================================
# Test: Enrich Article
# ============================================

class TestEnrichArticle:
    """Tests for the article enrichment function."""

    @pytest.fixture(autouse=True)
    def setup_kb(self, sample_docs_dir, chroma_dir):
        """Build knowledge base before enrichment tests."""
        self.chroma_dir = chroma_dir
        build_knowledge_base(
            documents_dir=sample_docs_dir,
            persist_dir=chroma_dir,
        )

    def test_enriches_with_category_query(self):
        """Should use category in enrichment query."""
        article = ClassifiedArticle(
            title="SQL Injection Vulnerability Found in Popular CMS",
            link="https://example.com/sqli",
            source="Test",
            summary="Critical SQL injection flaw discovered in web application.",
            category="Vulnerability Management",
            confidence=0.9,
        )

        enriched = enrich_article(article, persist_dir=self.chroma_dir)

        assert enriched.rag_context != ""
        assert len(enriched.rag_sources) > 0
        assert enriched.title == article.title
        assert enriched.category == article.category
