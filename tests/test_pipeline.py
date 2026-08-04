"""
Tests for the LangGraph Orchestrator Pipeline
=================================================

Purpose:
    Verifies that the LangGraph pipeline compiles correctly,
    nodes are wired in the right order, and the conditional
    edge (reflection loop) routes correctly.

Testing strategy:
    - Test graph compilation (no actual agent execution)
    - Test conditional edge logic (_should_revise)
    - Test with mock nodes (replace agents with simple functions)
    - Test error handling in node wrappers
    - Test full pipeline structure

How to run:
    pytest tests/test_pipeline.py -v
"""

import pytest

from models.schemas import MagazineArticle, ReviewResult


# ============================================
# Test Pipeline Compilation
# ============================================

class TestBuildPipeline:
    """Tests for pipeline construction and compilation."""

    def test_pipeline_compiles(self):
        """Pipeline should compile without errors."""
        from orchestrator.pipeline import build_pipeline
        pipeline = build_pipeline()
        assert pipeline is not None

    def test_pipeline_has_graph(self):
        """Compiled pipeline should have a graph structure."""
        from orchestrator.pipeline import build_pipeline
        pipeline = build_pipeline()
        # Compiled graph should be invocable
        assert hasattr(pipeline, "invoke")

    def test_pipeline_nodes_present(self):
        """All expected nodes should be in the graph."""
        from orchestrator.pipeline import build_pipeline
        pipeline = build_pipeline()

        # The compiled graph's node names are keys in the nodes dict
        graph = pipeline.get_graph()
        node_ids = list(graph.nodes.keys())

        expected_nodes = [
            "collector", "duplicate", "classifier",
            "rag", "writer", "reviewer", "pdf_generator",
        ]
        for node_name in expected_nodes:
            assert node_name in node_ids, f"Missing node: {node_name}"


# ============================================
# Test Conditional Edge Logic
# ============================================

class TestShouldRevise:
    """Tests for the revision routing logic."""

    def test_all_approved_goes_to_pdf(self):
        """When all articles are approved, should route to PDF."""
        from orchestrator.pipeline import _should_revise

        state = {
            "review_results": [
                ReviewResult(quality_score=8, approved=True, review_notes="Good"),
                ReviewResult(quality_score=9, approved=True, review_notes="Great"),
            ],
            "revision_count": 1,
        }
        assert _should_revise(state) == "pdf_generator"

    def test_unapproved_triggers_revision(self):
        """When articles are not approved and revisions left, route to Writer."""
        from orchestrator.pipeline import _should_revise, MAX_REVISION_CYCLES

        state = {
            "review_results": [
                ReviewResult(quality_score=4, approved=False, review_notes="Needs work"),
            ],
            "revision_count": 0,
        }
        # Only expect revision if we're below the max
        if MAX_REVISION_CYCLES > 0:
            assert _should_revise(state) == "writer"

    def test_max_revisions_forces_pdf(self):
        """When max revision cycles reached, route to PDF regardless."""
        from orchestrator.pipeline import _should_revise, MAX_REVISION_CYCLES

        state = {
            "review_results": [
                ReviewResult(quality_score=3, approved=False, review_notes="Bad"),
            ],
            "revision_count": MAX_REVISION_CYCLES,
        }
        assert _should_revise(state) == "pdf_generator"

    def test_empty_review_results_goes_to_pdf(self):
        """When no review results exist, route to PDF."""
        from orchestrator.pipeline import _should_revise

        state = {
            "review_results": [],
            "revision_count": 0,
        }
        assert _should_revise(state) == "pdf_generator"

    def test_mixed_results_triggers_revision(self):
        """When some articles approved and some not, should revise."""
        from orchestrator.pipeline import _should_revise

        state = {
            "review_results": [
                ReviewResult(quality_score=9, approved=True, review_notes="Good"),
                ReviewResult(quality_score=4, approved=False, review_notes="Bad"),
            ],
            "revision_count": 0,
        }
        assert _should_revise(state) == "writer"


# ============================================
# Test Safe Node Wrappers
# ============================================

class TestSafeNodeWrappers:
    """Tests for error-handling node wrappers."""

    def test_safe_collector_handles_error(self):
        """Collector wrapper should catch errors gracefully."""
        from orchestrator.pipeline import _safe_collector_node
        from unittest.mock import patch

        # Mock the collector to raise an error
        with patch(
            "agents.collector.collector_node",
            side_effect=RuntimeError("Network error"),
        ):
            result = _safe_collector_node({"errors": []})
            assert result["raw_articles"] == []
            assert len(result["errors"]) > 0
            assert "Collector failed" in result["errors"][0]

    def test_safe_duplicate_handles_error(self):
        """Duplicate wrapper should pass through raw articles on error."""
        from orchestrator.pipeline import _safe_duplicate_node
        from unittest.mock import patch

        with patch(
            "agents.duplicate.duplicate_node",
            side_effect=RuntimeError("Processing error"),
        ):
            raw = [{"title": "Test"}]
            result = _safe_duplicate_node({"errors": [], "raw_articles": raw})
            assert result["unique_articles"] == raw
            assert len(result["errors"]) > 0

    def test_safe_writer_handles_error(self):
        """Writer wrapper should return empty list on error."""
        from orchestrator.pipeline import _safe_writer_node
        from unittest.mock import patch

        with patch(
            "agents.writer.writer_node",
            side_effect=RuntimeError("LLM error"),
        ):
            result = _safe_writer_node({"errors": []})
            assert result["magazine_articles"] == []
            assert len(result["errors"]) > 0

    def test_safe_reviewer_increments_revision(self):
        """Reviewer wrapper should increment revision_count."""
        from orchestrator.pipeline import _safe_reviewer_node
        from unittest.mock import patch

        mock_result = {
            "review_results": [],
            "current_stage": "review_complete",
        }
        with patch(
            "agents.reviewer.reviewer_node",
            return_value=mock_result,
        ):
            result = _safe_reviewer_node({"revision_count": 0, "errors": []})
            assert result["revision_count"] == 1

    def test_safe_reviewer_handles_error(self):
        """Reviewer wrapper should still increment count on error."""
        from orchestrator.pipeline import _safe_reviewer_node
        from unittest.mock import patch

        with patch(
            "agents.reviewer.reviewer_node",
            side_effect=RuntimeError("API error"),
        ):
            result = _safe_reviewer_node({"revision_count": 1, "errors": []})
            assert result["revision_count"] == 2
            assert len(result["errors"]) > 0

    def test_safe_pdf_handles_error(self):
        """PDF wrapper should return empty path on error."""
        from orchestrator.pipeline import _safe_pdf_node
        from unittest.mock import patch

        with patch(
            "pdf.generator.pdf_node",
            side_effect=RuntimeError("Disk error"),
        ):
            result = _safe_pdf_node({"errors": []})
            assert result["pdf_path"] == ""
            assert len(result["errors"]) > 0


# ============================================
# Test Pipeline Constants
# ============================================

class TestConstants:
    """Tests for pipeline configuration constants."""

    def test_max_revision_cycles_positive(self):
        """Max revision cycles should be a positive integer."""
        from orchestrator.pipeline import MAX_REVISION_CYCLES
        assert isinstance(MAX_REVISION_CYCLES, int)
        assert MAX_REVISION_CYCLES > 0


# ============================================
# Test Run Pipeline Function Exists
# ============================================

class TestRunPipeline:
    """Tests for the run_pipeline convenience function."""

    def test_run_pipeline_callable(self):
        """run_pipeline should be importable and callable."""
        from orchestrator.pipeline import run_pipeline
        assert callable(run_pipeline)

    def test_build_pipeline_callable(self):
        """build_pipeline should be importable and callable."""
        from orchestrator.pipeline import build_pipeline
        assert callable(build_pipeline)
