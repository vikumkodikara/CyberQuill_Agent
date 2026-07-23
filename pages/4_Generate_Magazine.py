"""
CyberQuill — Generate Magazine Page
======================================

Runs the full pipeline and generates a downloadable PDF magazine.
Shows progress for each pipeline stage with reader-friendly status updates.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from utils.theme import render_page_header, get_category_badge_html, render_sidebar_controls, get_category_pill_style
from utils.helpers import estimate_article_reading_time
from utils.content_sanitizer import sanitize_article

st.set_page_config(page_title="Generate Magazine — CyberQuill", page_icon="📰", layout="wide")

# Sidebar controls
render_sidebar_controls()

render_page_header(
    title="Generate a Magazine",
    subtitle="Create a new CyberQuill magazine — articles are curated, enriched, professionally written, reviewed, and compiled into a downloadable PDF.",
    icon="📰"
)

# ============================================
# Pipeline Controls
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-bottom:1rem;'>🚀 Generate Magazine</h4>", unsafe_allow_html=True)

col_run, col_opts = st.columns([1, 2])

with col_opts:
    st.markdown("""
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:1rem 1.25rem;">
        <div style="font-weight:700; color:#0f172a; margin-bottom:4px;">How it works</div>
        <div style="font-size:0.85rem; color:#64748b;">CyberQuill gathers the latest cybersecurity news, enriches it with expert context, and compiles a professionally written magazine PDF.</div>
    </div>
    """, unsafe_allow_html=True)

with col_run:
    run_clicked = st.button(
        "📰 Generate Magazine",
        type="primary",
        use_container_width=True,
    )

# ============================================
# Pipeline Execution
# ============================================

if run_clicked:
    progress_bar = st.progress(0, text="Preparing...")
    status_box = st.container()

    stages = [
        ("📡 Gathering latest cybersecurity news...", 0.14),
        ("🔍 Filtering duplicate stories...", 0.28),
        ("🏷️ Categorizing threat intelligence...", 0.42),
        ("📚 Enriching with security context...", 0.56),
        ("✍️ Composing magazine articles...", 0.70),
        ("📝 Editorial quality review...", 0.85),
        ("📄 Preparing magazine layout...", 0.95),
    ]

    try:
        # Stage 1: Collect
        progress_bar.progress(stages[0][1], text=stages[0][0])
        from agents.collector import collect_all_feeds
        raw_articles = collect_all_feeds()
        status_box.success(f"📡 Collected {len(raw_articles)} news articles")

        if not raw_articles:
            st.error("No articles collected. Feeds unavailable.")
            st.stop()

        # Stage 2: Deduplicate
        progress_bar.progress(stages[1][1], text=stages[1][0])
        from agents.duplicate import remove_duplicates
        unique_articles = remove_duplicates(raw_articles)
        status_box.success(f"🔍 Filtered to {len(unique_articles)} unique stories")

        # Stage 3: Classify
        progress_bar.progress(stages[2][1], text=stages[2][0])
        from agents.classifier import classify_articles
        classified = classify_articles(unique_articles)
        cats = {}
        for a in classified:
            cats[a.category] = cats.get(a.category, 0) + 1
        status_box.success(f"🏷️ Categorized {len(classified)} articles")

        # Stage 4: RAG Enrich
        progress_bar.progress(stages[3][1], text=stages[3][0])
        from agents.rag import enrich_articles, build_knowledge_base
        try:
            from agents.rag import _get_collection
            _get_collection()
        except Exception:
            build_knowledge_base()
        enriched = enrich_articles(classified)
        status_box.success(f"📚 Enriched {len(enriched)} articles with expert context")

        # Stage 5: Write
        progress_bar.progress(stages[4][1], text=stages[4][0])
        from agents.writer import write_articles
        magazine_articles = write_articles(enriched)
        status_box.success(f"✍️ Composed {len(magazine_articles)} magazine articles")

        # Stage 6: Review
        progress_bar.progress(stages[5][1], text=stages[5][0])
        from agents.reviewer import review_articles
        reviews = review_articles(magazine_articles)
        approved = sum(1 for r in reviews if r.approved)
        avg_score = sum(r.quality_score for r in reviews) / len(reviews) if reviews else 0
        status_box.success(f"📝 Quality review passed — {approved} articles approved")

        # Stage 7: PDF
        progress_bar.progress(stages[6][1], text=stages[6][0])
        from pdf.generator import generate_pdf
        from utils.issue_tracker import get_current_issue_number
        issue_num = get_current_issue_number()
        pdf_path = generate_pdf(magazine_articles)
        progress_bar.progress(1.0, text="✅ Issue Published Successfully!")
        status_box.success(f"📄 Magazine issue ready for download!")

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
            "issue_number": issue_num,
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

    st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-bottom:1rem;'>📊 Issue Summary</h4>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("News Sources", res["raw_count"])
    m2.metric("Unique Stories", res["unique_count"])
    m3.metric("Published Articles", res["magazine_count"])

    st.markdown("<br>", unsafe_allow_html=True)

    # PDF Download Banner
    if res.get("pdf_path"):
        p_path = Path(res["pdf_path"])
        if p_path.exists():
            issue_num = res.get("issue_number", "—")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color:white; padding:2rem; border-radius:18px; border:1px solid #6366f1; text-align:center; box-shadow:0 15px 30px rgba(15,23,42,0.3); margin-bottom:2rem;">
                <div style="font-size:2rem; margin-bottom:0.5rem;">📄</div>
                <h3 style="font-family:'Space Grotesk', sans-serif; margin:0 0 0.5rem 0; color:#ffffff;">CyberQuill Issue #{issue_num:03d} is Ready!</h3>
                <p style="color:#94a3b8; font-size:0.95rem; margin-bottom:1.5rem;">Published {res['timestamp']} with {res['magazine_count']} curated articles.</p>
            </div>
            """, unsafe_allow_html=True)

            with open(p_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download CyberQuill Magazine (PDF)",
                    data=f.read(),
                    file_name=p_path.name,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )

    # ============================================
    # Article Previews
    # ============================================

    st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-top:2rem; margin-bottom:1rem;'>📖 Article Previews</h4>", unsafe_allow_html=True)

    m_articles = res.get("magazine_articles", [])
    m_reviews = res.get("reviews", [])

    for i, art in enumerate(m_articles):
        rev = m_reviews[i] if i < len(m_reviews) else None

        display_art = sanitize_article(art)

        read_time = estimate_article_reading_time(display_art)
        bg, fg, border = get_category_pill_style(display_art.category)

        excerpt = (display_art.executive_summary or "")[:300]
        if len(display_art.executive_summary or "") > 300:
            excerpt += "..."

        st.markdown(f"""
        <div class="magazine-preview-card">
            <span class="card-category" style="background:{bg}; color:{fg}; border:1px solid {border};">{display_art.category}</span>
            <div class="card-title">{display_art.title}</div>
            <div class="card-excerpt">{excerpt}</div>
            <div class="card-meta">
                <span>📖 {read_time} min read</span>
                {'<span>🔗 <a href="' + display_art.original_link + '" target="_blank" style="color:#4f46e5; text-decoration:none;">Original Source</a></span>' if display_art.original_link else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"📖 Read Full Article: {display_art.title}"):
            if display_art.executive_summary:
                st.markdown("### Executive Summary")
                st.markdown(display_art.executive_summary)
            if display_art.background:
                st.markdown("---")
                st.markdown("### Background")
                st.markdown(display_art.background)
            if display_art.technical_analysis:
                st.markdown("---")
                st.markdown("### Technical Analysis")
                st.markdown(display_art.technical_analysis)
            if display_art.impact:
                st.markdown("---")
                st.markdown("### Impact Assessment")
                st.markdown(display_art.impact)
            if display_art.recommendations:
                st.markdown("---")
                st.markdown("### Recommendations")
                st.markdown(display_art.recommendations)
            if display_art.references:
                st.markdown("---")
                st.markdown("### References")
                st.markdown(display_art.references)

    # ============================================
    # Issue History
    # ============================================

    try:
        from utils.issue_tracker import get_issue_history
        history = get_issue_history()
        if history and len(history) > 1:
            st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-top:2rem; margin-bottom:1rem;'>📚 Past Issues</h4>", unsafe_allow_html=True)
            for issue in history[1:5]:  # Show up to 4 past issues (skip current)
                st.markdown(f"""
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:0.9rem 1.25rem; margin-bottom:0.5rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-weight:700; color:#0f172a;">Issue #{issue['issue_number']:03d}</span>
                            <span style="color:#64748b; font-size:0.85rem; margin-left:12px;">{issue.get('date_display', issue.get('date', ''))}</span>
                        </div>
                        <span style="color:#64748b; font-size:0.85rem;">{issue['article_count']} articles</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    except Exception:
        pass
