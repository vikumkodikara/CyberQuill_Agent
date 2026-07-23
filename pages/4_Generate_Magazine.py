"""
CyberQuill — Generate Magazine Page
=======================================

Runs the full LangGraph pipeline and generates a downloadable PDF magazine.
Shows progress for each pipeline stage with real-time status updates.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Generate Magazine — CyberQuill", page_icon="📰", layout="wide")

st.title("📰 Generate Magazine")
st.markdown(
    "Run the complete CyberQuill pipeline to collect news, classify, enrich, "
    "write, review, and generate a professional PDF magazine."
)
st.divider()


# ============================================
# Pipeline Controls
# ============================================

st.subheader("🚀 Pipeline Controls")

col_run, col_opts = st.columns([1, 2])

with col_opts:
    st.markdown("**Options**")
    use_llm = st.checkbox(
        "Use LLM-powered agents (requires API keys)",
        value=True,
        help="When unchecked, all agents use fallback modes (keyword classification, template writing, rule-based review)",
    )

with col_run:
    run_clicked = st.button(
        "▶️ Run Full Pipeline",
        type="primary",
        use_container_width=True,
    )


# ============================================
# Pipeline Execution
# ============================================

if run_clicked:
    # Progress tracking
    progress = st.progress(0, text="Starting pipeline...")
    status_container = st.container()

    stages = [
        ("📡 Collecting articles from RSS feeds...", 0.10),
        ("🔍 Removing duplicate articles...", 0.25),
        ("🏷️ Classifying articles by category...", 0.40),
        ("📚 Enriching articles with RAG context...", 0.55),
        ("✍️ Writing magazine articles...", 0.70),
        ("📝 Reviewing article quality...", 0.85),
        ("📄 Generating PDF magazine...", 0.95),
    ]

    try:
        # Stage 1: Collect
        progress.progress(stages[0][1], text=stages[0][0])
        from agents.collector import collect_all_feeds
        raw_articles = collect_all_feeds()
        status_container.success(f"📡 Collected {len(raw_articles)} articles")

        if not raw_articles:
            st.error("No articles collected. RSS feeds may be unavailable.")
            st.stop()

        # Stage 2: Deduplicate
        progress.progress(stages[1][1], text=stages[1][0])
        from agents.duplicate import remove_duplicates
        unique_articles = remove_duplicates(raw_articles)
        status_container.success(
            f"🔍 Deduplicated: {len(raw_articles)} → {len(unique_articles)} articles"
        )

        # Stage 3: Classify
        progress.progress(stages[2][1], text=stages[2][0])
        from agents.classifier import classify_articles
        classified = classify_articles(unique_articles)
        cats = {}
        for a in classified:
            cats[a.category] = cats.get(a.category, 0) + 1
        status_container.success(
            f"🏷️ Classified {len(classified)} articles: {dict(cats)}"
        )

        # Stage 4: RAG Enrich
        progress.progress(stages[3][1], text=stages[3][0])
        from agents.rag import enrich_articles, build_knowledge_base
        try:
            from agents.rag import _get_collection
            _get_collection()
        except Exception:
            build_knowledge_base()
        enriched = enrich_articles(classified)
        status_container.success(f"📚 Enriched {len(enriched)} articles with RAG context")

        # Stage 5: Write
        progress.progress(stages[4][1], text=stages[4][0])
        from agents.writer import write_articles
        magazine_articles = write_articles(enriched)
        status_container.success(f"✍️ Generated {len(magazine_articles)} magazine articles")

        # Stage 6: Review
        progress.progress(stages[5][1], text=stages[5][0])
        from agents.reviewer import review_articles
        reviews = review_articles(magazine_articles)
        approved = sum(1 for r in reviews if r.approved)
        avg_score = sum(r.quality_score for r in reviews) / len(reviews) if reviews else 0
        status_container.success(
            f"📝 Reviewed: {approved}/{len(reviews)} approved "
            f"(avg score: {avg_score:.1f}/10)"
        )

        # Stage 7: PDF
        progress.progress(stages[6][1], text=stages[6][0])
        from pdf.generator import generate_pdf
        pdf_path = generate_pdf(magazine_articles)
        progress.progress(1.0, text="✅ Pipeline complete!")
        status_container.success(f"📄 PDF generated: {pdf_path}")

        # Store results in session state
        st.session_state["pipeline_result"] = {
            "raw_count": len(raw_articles),
            "unique_count": len(unique_articles),
            "classified_count": len(classified),
            "enriched_count": len(enriched),
            "magazine_count": len(magazine_articles),
            "approved_count": approved,
            "avg_score": avg_score,
            "pdf_path": pdf_path,
            "categories": cats,
            "magazine_articles": magazine_articles,
            "reviews": reviews,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        progress.progress(1.0, text="❌ Pipeline failed!")
        st.error(f"Pipeline error: {e}")
        import traceback
        st.code(traceback.format_exc())


# ============================================
# Results Display
# ============================================

if "pipeline_result" in st.session_state:
    result = st.session_state["pipeline_result"]

    st.divider()
    st.subheader("📊 Pipeline Results")

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Collected", result["raw_count"])
    m2.metric("Unique", result["unique_count"])
    m3.metric("Approved", f"{result['approved_count']}/{result['magazine_count']}")
    m4.metric("Avg Score", f"{result['avg_score']:.1f}/10")

    # PDF Download
    if result.get("pdf_path"):
        pdf_path = Path(result["pdf_path"])
        if pdf_path.exists():
            st.subheader("📥 Download Magazine")
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download CyberQuill Weekly (PDF)",
                    data=f.read(),
                    file_name=pdf_path.name,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )

    # Article preview
    st.subheader("📖 Article Preview")
    magazine_articles = result.get("magazine_articles", [])
    reviews = result.get("reviews", [])

    for i, article in enumerate(magazine_articles):
        review = reviews[i] if i < len(reviews) else None
        status = "✅" if (review and review.approved) else "⚠️"
        score = review.quality_score if review else "N/A"

        with st.expander(f"{status} {article.title} — Score: {score}/10"):
            st.markdown(f"**Category:** {article.category}")
            if article.executive_summary:
                st.markdown(f"**Executive Summary:** {article.executive_summary}")
            if article.original_link:
                st.markdown(f"[Original Source]({article.original_link})")
            if review and review.issues:
                st.warning("**Issues:** " + ", ".join(review.issues))
