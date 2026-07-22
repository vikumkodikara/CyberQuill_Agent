"""
CyberQuill — Generate Magazine Page
======================================

Runs the full LangGraph pipeline and generates a downloadable PDF magazine.
Shows progress for each pipeline stage with real-time status updates.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from utils.theme import render_page_header, get_category_badge_html

st.set_page_config(page_title="Generate Magazine — CyberQuill", page_icon="📰", layout="wide")

render_page_header(
    title="Generate CyberQuill Weekly",
    subtitle="Execute the autonomous 7-agent pipeline to aggregate, deduplicate, classify, enrich, write, review, and render a PDF issue.",
    icon="📰"
)

# ============================================
# Pipeline Controls
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; color:#0f172a; margin-bottom:1rem;'>🚀 Pipeline Orchestration Controls</h4>", unsafe_allow_html=True)

col_run, col_opts = st.columns([1, 2])

with col_opts:
    st.markdown("""
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:1rem 1.25rem;">
        <div style="font-weight:700; color:#0f172a; margin-bottom:4px;">Execution Mode</div>
        <div style="font-size:0.85rem; color:#64748b;">LangGraph orchestrator will trigger Collector → Duplicate → Classifier → RAG → Writer → Reviewer → PDF Generator.</div>
    </div>
    """, unsafe_allow_html=True)

with col_run:
    run_clicked = st.button(
        "▶️ Launch Full Pipeline",
        type="primary",
        use_container_width=True,
    )

# ============================================
# Pipeline Execution
# ============================================

if run_clicked:
    progress_bar = st.progress(0, text="Initializing LangGraph engine...")
    status_box = st.container()

    stages = [
        ("📡 Stage 1: Collecting articles from RSS feeds...", 0.14),
        ("🔍 Stage 2: Deduplicating articles via fuzzy matching...", 0.28),
        ("🏷️ Stage 3: Classifying threat categories...", 0.42),
        ("📚 Stage 4: Enriching with RAG vector search...", 0.56),
        ("✍️ Stage 5: Generating executive article summaries...", 0.70),
        ("📝 Stage 6: Running Reviewer Agent quality reflection loop...", 0.85),
        ("📄 Stage 7: Compiling PDF magazine layout...", 0.95),
    ]

    try:
        # Stage 1: Collect
        progress_bar.progress(stages[0][1], text=stages[0][0])
        from agents.collector import collect_all_feeds
        raw_articles = collect_all_feeds()
        status_box.success(f"📡 Stage 1 Complete: Collected {len(raw_articles)} raw threat feeds")

        if not raw_articles:
            st.error("No articles collected. Feeds unavailable.")
            st.stop()

        # Stage 2: Deduplicate
        progress_bar.progress(stages[1][1], text=stages[1][0])
        from agents.duplicate import remove_duplicates
        unique_articles = remove_duplicates(raw_articles)
        status_box.success(f"🔍 Stage 2 Complete: Filtered duplicates ({len(raw_articles)} → {len(unique_articles)} unique)")

        # Stage 3: Classify
        progress_bar.progress(stages[2][1], text=stages[2][0])
        from agents.classifier import classify_articles
        classified = classify_articles(unique_articles)
        cats = {}
        for a in classified:
            cats[a.category] = cats.get(a.category, 0) + 1
        status_box.success(f"🏷️ Stage 3 Complete: Classified {len(classified)} articles into categories")

        # Stage 4: RAG Enrich
        progress_bar.progress(stages[3][1], text=stages[3][0])
        from agents.rag import enrich_articles, build_knowledge_base
        try:
            from agents.rag import _get_collection
            _get_collection()
        except Exception:
            build_knowledge_base()
        enriched = enrich_articles(classified)
        status_box.success(f"📚 Stage 4 Complete: Enriched {len(enriched)} articles with vector context")

        # Stage 5: Write
        progress_bar.progress(stages[4][1], text=stages[4][0])
        from agents.writer import write_articles
        magazine_articles = write_articles(enriched)
        status_box.success(f"✍️ Stage 5 Complete: Generated {len(magazine_articles)} magazine articles")

        # Stage 6: Review
        progress_bar.progress(stages[5][1], text=stages[5][0])
        from agents.reviewer import review_articles
        reviews = review_articles(magazine_articles)
        approved = sum(1 for r in reviews if r.approved)
        avg_score = sum(r.quality_score for r in reviews) / len(reviews) if reviews else 0
        status_box.success(f"📝 Stage 6 Complete: Quality Review Passed ({approved}/{len(reviews)} approved, score {avg_score:.1f}/10)")

        # Stage 7: PDF
        progress_bar.progress(stages[6][1], text=stages[6][0])
        from pdf.generator import generate_pdf
        pdf_path = generate_pdf(magazine_articles)
        progress_bar.progress(1.0, text="✅ Pipeline Execution Finished!")
        status_box.success(f"📄 Stage 7 Complete: PDF issue saved to {pdf_path}")

        # Store in session state
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
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        progress_bar.progress(1.0, text="❌ Pipeline Failed!")
        st.error(f"Pipeline error: {e}")
        import traceback
        st.code(traceback.format_exc())

# ============================================
# Results Display
# ============================================

if "pipeline_result" in st.session_state:
    res = st.session_state["pipeline_result"]

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; color:#0f172a; margin-bottom:1rem;'>📊 Pipeline Execution Summary</h4>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Raw Feeds", res["raw_count"])
    m2.metric("Unique Signals", res["unique_count"])
    m3.metric("Approved Articles", f"{res['approved_count']}/{res['magazine_count']}")
    m4.metric("Avg Quality Score", f"{res['avg_score']:.1f} / 10")

    st.markdown("<br>", unsafe_allow_html=True)

    # PDF Download Banner
    if res.get("pdf_path"):
        p_path = Path(res["pdf_path"])
        if p_path.exists():
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color:white; padding:2rem; border-radius:18px; border:1px solid #6366f1; text-align:center; box-shadow:0 15px 30px rgba(15,23,42,0.3); margin-bottom:2rem;">
                <div style="font-size:2rem; margin-bottom:0.5rem;">📄</div>
                <h3 style="font-family:'Space Grotesk', sans-serif; margin:0 0 0.5rem 0; color:#ffffff;">Your PDF Magazine is Ready!</h3>
                <p style="color:#94a3b8; font-size:0.95rem; margin-bottom:1.5rem;">Issue generated on {res['timestamp']} with {res['magazine_count']} curated articles.</p>
            </div>
            """, unsafe_allow_html=True)

            with open(p_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download CyberQuill Weekly (PDF)",
                    data=f.read(),
                    file_name=p_path.name,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )

    # Preview Articles
    st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; color:#0f172a; margin-top:2rem; margin-bottom:1rem;'>📖 Article Previews</h4>", unsafe_allow_html=True)
    
    m_articles = res.get("magazine_articles", [])
    m_reviews = res.get("reviews", [])

    for i, art in enumerate(m_articles):
        rev = m_reviews[i] if i < len(m_reviews) else None
        status_icon = "✅" if (rev and rev.approved) else "⚠️"
        score_val = rev.quality_score if rev else "N/A"

        with st.expander(f"{status_icon} {art.title} (Score: {score_val}/10)"):
            st.markdown(f"**Category:** `{art.category}`")
            if art.executive_summary:
                st.markdown(f"**Executive Summary:** {art.executive_summary}")
            if art.original_link:
                st.markdown(f"🔗 [View Original Article]({art.original_link})")
            if rev and rev.issues:
                st.warning("Quality Review Feedback: " + ", ".join(rev.issues))
