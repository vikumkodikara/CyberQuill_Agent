"""
CyberQuill LangGraph Orchestrator Pipeline
=============================================

Purpose:
    Wires all agents into a single LangGraph StateGraph pipeline.
    This is the "brain" of CyberQuill — it defines the order of
    execution, data flow, and the reflection loop for the Reviewer.

How LangGraph StateGraph works:
    1. Define a STATE schema (TypedDict) with all shared fields
    2. Add NODES (functions) that read/write state
    3. Add EDGES that connect nodes in order
    4. Add CONDITIONAL EDGES for branching logic (e.g., revision loop)
    5. Compile and run the graph

Pipeline flow:
    ┌──────────┐    ┌───────────┐    ┌────────────┐    ┌─────┐
    │ Collector │───▶│ Duplicate │───▶│ Classifier │───▶│ RAG │
    └──────────┘    └───────────┘    └────────────┘    └──┬──┘
                                                          │
                   ┌──────────────────────────────────────┘
                   ▼
               ┌────────┐    ┌──────────┐    ┌─────────────┐
               │ Writer │───▶│ Reviewer │───▶│  should_     │
               └───▲────┘    └──────────┘    │  revise?     │
                   │                         └──────┬───────┘
                   │                                │
                   │  score < 7 &                   │ score >= 7
                   │  revisions < max               │ or max revisions
                   └────────────────────────────────▼
                                                ┌─────┐
                                                │ PDF │
                                                └─────┘

Agentic AI Design Patterns implemented:
    1. **Orchestrator-Worker** — Central pipeline delegates to agents
    2. **Router/Conditional** — Conditional edge decides revision vs PDF
    3. **Reflection** — Reviewer → Writer loop for quality improvement
    4. **Tool Use** — Collector uses feedparser, RAG uses ChromaDB
    5. **Planning/Decomposition** — Pipeline breaks task into sub-tasks

Inputs:
    - None (the Collector Agent fetches data from RSS feeds)

Outputs:
    - A compiled LangGraph graph that can be invoked
    - Final state contains all pipeline results + PDF path

Dependencies:
    - langgraph: StateGraph, conditional edges
    - All agent node functions
    - PDF generator node function

Testing strategy:
    - Test graph compilation (no runtime needed)
    - Test with mocked nodes (replace real agents with simple functions)
    - Test conditional edge logic (revision routing)
    - Test full pipeline (integration, requires API or fallbacks)

Possible improvements:
    - Add parallel execution for independent agents
    - Add checkpoint/resume for long-running pipelines
    - Add human-in-the-loop approval step
    - Add retry logic for individual nodes
"""

from typing import TypedDict

from langgraph.graph import END, StateGraph

from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================
# Pipeline State Definition
# ============================================

class PipelineState(TypedDict, total=False):
    """
    The shared state that flows through the entire LangGraph pipeline.

    LangGraph requires TypedDict for its StateGraph. Each agent node
    reads what it needs and returns partial updates that merge into state.

    How state merging works:
        When a node returns {"raw_articles": [...]}, LangGraph REPLACES
        the "raw_articles" key in state. For list fields, we want
        replacement semantics (not append), so no reducer is needed.
    """
    # Stage outputs
    raw_articles: list          # Collector → list[Article]
    unique_articles: list       # Duplicate → list[Article]
    classified_articles: list   # Classifier → list[ClassifiedArticle]
    enriched_articles: list     # RAG → list[EnrichedArticle]
    magazine_articles: list     # Writer → list[MagazineArticle]
    review_results: list        # Reviewer → list[ReviewResult]

    # PDF output
    pdf_path: str               # PDF Generator → file path

    # Pipeline metadata
    errors: list                # Any errors encountered
    current_stage: str          # Current pipeline stage
    revision_count: int         # Number of Writer→Reviewer cycles completed


# ============================================
# Configuration
# ============================================

# Maximum number of Writer→Reviewer revision cycles
MAX_REVISION_CYCLES = 2


# ============================================
# Node Wrappers (with error handling)
# ============================================
# These wrapper functions add error handling around each agent's
# node function. If an agent crashes, the error is recorded in
# state instead of killing the entire pipeline.


def _safe_collector_node(state: PipelineState) -> dict:
    """Collector node with error handling."""
    try:
        from agents.collector import collector_node
        return collector_node(state)
    except Exception as e:
        logger.error(f"Collector Agent failed: {e}")
        return {
            "raw_articles": [],
            "errors": state.get("errors", []) + [f"Collector failed: {e}"],
            "current_stage": "collection_failed",
        }


def _safe_duplicate_node(state: PipelineState) -> dict:
    """Duplicate node with error handling."""
    try:
        from agents.duplicate import duplicate_node
        return duplicate_node(state)
    except Exception as e:
        logger.error(f"Duplicate Agent failed: {e}")
        return {
            "unique_articles": state.get("raw_articles", []),
            "errors": state.get("errors", []) + [f"Duplicate failed: {e}"],
            "current_stage": "deduplication_failed",
        }


def _safe_classifier_node(state: PipelineState) -> dict:
    """Classifier node with error handling."""
    try:
        from agents.classifier import classifier_node
        return classifier_node(state)
    except Exception as e:
        logger.error(f"Classifier Agent failed: {e}")
        return {
            "classified_articles": [],
            "errors": state.get("errors", []) + [f"Classifier failed: {e}"],
            "current_stage": "classification_failed",
        }


def _safe_rag_node(state: PipelineState) -> dict:
    """RAG node with error handling."""
    try:
        from agents.rag import rag_node
        return rag_node(state)
    except Exception as e:
        logger.error(f"RAG Agent failed: {e}")
        # If RAG fails, pass classified articles through as enriched
        # (with empty RAG context) — graceful degradation
        from models.schemas import EnrichedArticle
        classified = state.get("classified_articles", [])
        enriched = []
        for article in classified:
            enriched_data = article if isinstance(article, dict) else article.model_dump()
            enriched_data["rag_context"] = ""
            enriched_data["rag_sources"] = []
            enriched.append(EnrichedArticle(**enriched_data))
        return {
            "enriched_articles": enriched,
            "errors": state.get("errors", []) + [f"RAG failed: {e}"],
            "current_stage": "enrichment_failed",
        }


def _safe_writer_node(state: PipelineState) -> dict:
    """Writer node with error handling."""
    try:
        from agents.writer import writer_node
        return writer_node(state)
    except Exception as e:
        logger.error(f"Writer Agent failed: {e}")
        return {
            "magazine_articles": [],
            "errors": state.get("errors", []) + [f"Writer failed: {e}"],
            "current_stage": "writing_failed",
        }


def _safe_reviewer_node(state: PipelineState) -> dict:
    """
    Reviewer node with error handling and revision tracking.

    Also increments the revision_count so the conditional edge
    can check if we've hit the max revision limit.
    """
    try:
        from agents.reviewer import reviewer_node
        result = reviewer_node(state)
        # Increment revision count
        result["revision_count"] = state.get("revision_count", 0) + 1
        return result
    except Exception as e:
        logger.error(f"Reviewer Agent failed: {e}")
        return {
            "review_results": [],
            "revision_count": state.get("revision_count", 0) + 1,
            "errors": state.get("errors", []) + [f"Reviewer failed: {e}"],
            "current_stage": "review_failed",
        }


def _safe_pdf_node(state: PipelineState) -> dict:
    """PDF Generator node with error handling."""
    try:
        from pdf.generator import pdf_node
        return pdf_node(state)
    except Exception as e:
        logger.error(f"PDF Generator failed: {e}")
        return {
            "pdf_path": "",
            "errors": state.get("errors", []) + [f"PDF Generator failed: {e}"],
            "current_stage": "pdf_failed",
        }


# ============================================
# Conditional Edge: Should We Revise?
# ============================================

def _should_revise(state: PipelineState) -> str:
    """
    Determines whether articles should be sent back to the Writer
    for revision or forwarded to the PDF Generator.

    This implements the REFLECTION PATTERN conditional logic:
        - If ANY article scored below threshold AND we haven't exceeded
          the max revision cycles → route to "writer" for revision
        - Otherwise → route to "pdf_generator" for final output

    Why limit revisions?
        - Prevents infinite loops
        - LLMs can "overthink" and degrade quality after too many passes
        - 2 cycles is typically sufficient for quality improvement

    Args:
        state: Current pipeline state

    Returns:
        "writer" to revise, or "pdf_generator" to finalise
    """
    review_results = state.get("review_results", [])
    revision_count = state.get("revision_count", 0)

    # Check if we've hit the revision limit
    if revision_count >= MAX_REVISION_CYCLES:
        logger.info(
            f"Max revision cycles ({MAX_REVISION_CYCLES}) reached. "
            f"Proceeding to PDF generation."
        )
        return "pdf_generator"

    # Check if any articles need revision
    if review_results:
        needs_revision = any(
            not result.approved
            for result in review_results
            if hasattr(result, "approved")
        )

        if needs_revision:
            logger.info(
                f"Revision cycle {revision_count + 1}/{MAX_REVISION_CYCLES}: "
                f"Some articles need improvement. Sending back to Writer."
            )
            return "writer"

    # All articles approved or no review results
    logger.info("All articles approved. Proceeding to PDF generation.")
    return "pdf_generator"


# ============================================
# Build the LangGraph Pipeline
# ============================================

def build_pipeline() -> StateGraph:
    """
    Constructs and compiles the CyberQuill LangGraph pipeline.

    This is the main function that wires all agents together.

    How it works:
        1. Create a StateGraph with PipelineState
        2. Add all agent nodes
        3. Connect nodes with edges (linear flow)
        4. Add conditional edge for the reflection loop
        5. Compile and return the executable graph

    Returns:
        A compiled LangGraph StateGraph ready to be invoked

    Example:
        >>> from orchestrator.pipeline import build_pipeline
        >>> pipeline = build_pipeline()
        >>> result = pipeline.invoke({"revision_count": 0})
        >>> print(result["pdf_path"])
    """
    logger.info("Building CyberQuill pipeline...")

    # Create the graph
    graph = StateGraph(PipelineState)

    # ---- Add Nodes ----
    # Each node is a function that takes state and returns state updates
    graph.add_node("collector", _safe_collector_node)
    graph.add_node("duplicate", _safe_duplicate_node)
    graph.add_node("classifier", _safe_classifier_node)
    graph.add_node("rag", _safe_rag_node)
    graph.add_node("writer", _safe_writer_node)
    graph.add_node("reviewer", _safe_reviewer_node)
    graph.add_node("pdf_generator", _safe_pdf_node)

    # ---- Add Edges ----
    # Linear flow: Collector → Duplicate → Classifier → RAG → Writer → Reviewer
    graph.set_entry_point("collector")
    graph.add_edge("collector", "duplicate")
    graph.add_edge("duplicate", "classifier")
    graph.add_edge("classifier", "rag")
    graph.add_edge("rag", "writer")
    graph.add_edge("writer", "reviewer")

    # ---- Conditional Edge: Reflection Pattern ----
    # After review, decide: revise (back to Writer) or generate PDF
    graph.add_conditional_edges(
        "reviewer",
        _should_revise,
        {
            "writer": "writer",           # Loop back for revision
            "pdf_generator": "pdf_generator",  # Move to PDF generation
        },
    )

    # PDF generator is the final node
    graph.add_edge("pdf_generator", END)

    # ---- Compile ----
    compiled = graph.compile()
    logger.info("Pipeline compiled successfully.")

    return compiled


# ============================================
# Convenience: Run the Full Pipeline
# ============================================

def run_pipeline() -> dict:
    """
    Builds and runs the full CyberQuill pipeline.

    This is the simplest way to run the entire system.
    It handles the full flow from RSS collection to PDF generation.

    Returns:
        The final pipeline state dictionary with all results

    Example:
        >>> from orchestrator.pipeline import run_pipeline
        >>> result = run_pipeline()
        >>> print(f"PDF: {result.get('pdf_path')}")
        >>> print(f"Articles: {len(result.get('magazine_articles', []))}")
        >>> print(f"Errors: {result.get('errors', [])}")
    """
    logger.info("=" * 60)
    logger.info("CyberQuill Pipeline Starting")
    logger.info("=" * 60)

    # Build the graph
    pipeline = build_pipeline()

    # Initial state
    initial_state = {
        "raw_articles": [],
        "unique_articles": [],
        "classified_articles": [],
        "enriched_articles": [],
        "magazine_articles": [],
        "review_results": [],
        "pdf_path": "",
        "errors": [],
        "current_stage": "starting",
        "revision_count": 0,
    }

    # Run the pipeline
    try:
        final_state = pipeline.invoke(initial_state)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        final_state = {
            **initial_state,
            "errors": [f"Pipeline failed: {e}"],
            "current_stage": "pipeline_failed",
        }

    # Log summary
    logger.info("=" * 60)
    logger.info("CyberQuill Pipeline Complete")
    logger.info(f"  Articles collected:  {len(final_state.get('raw_articles', []))}")
    logger.info(f"  Unique articles:     {len(final_state.get('unique_articles', []))}")
    logger.info(f"  Classified:          {len(final_state.get('classified_articles', []))}")
    logger.info(f"  Enriched:            {len(final_state.get('enriched_articles', []))}")
    logger.info(f"  Magazine articles:   {len(final_state.get('magazine_articles', []))}")
    logger.info(f"  Review results:      {len(final_state.get('review_results', []))}")
    logger.info(f"  PDF path:            {final_state.get('pdf_path', 'N/A')}")
    logger.info(f"  Revision cycles:     {final_state.get('revision_count', 0)}")
    logger.info(f"  Errors:              {len(final_state.get('errors', []))}")
    logger.info("=" * 60)

    return final_state
