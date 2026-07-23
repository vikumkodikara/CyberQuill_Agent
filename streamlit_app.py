"""
CyberQuill — Streamlit Home Page & Navigation Dashboard
========================================================

Purpose:
    Entry point for the CyberQuill Streamlit multi-page application.
    Displays hero overview, featured articles, and interactive quick navigation cards.
    Supports Magazine Mode (reader-facing) and Debug Mode (developer-facing).

How to run:
    streamlit run streamlit_app.py
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from utils.theme import apply_custom_theme, render_sidebar_controls, get_category_pill_style
from utils.helpers import estimate_article_reading_time

# ============================================
# Page Configuration
# ============================================

st.set_page_config(
    page_title="CyberQuill",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global high-aesthetic design system
apply_custom_theme()

# Sidebar mode & dark toggles
render_sidebar_controls()

# Page Specific Custom CSS Overrides
st.markdown("""
<style>
    /* Hero Banner Styling */
    .hero-banner {
        position: relative;
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #1e1b4b 100%);
        border-radius: 24px;
        padding: 3.5rem 3rem;
        color: #ffffff;
        box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        overflow: hidden;
        margin-bottom: 2.5rem;
    }

    /* Ambient Glow Overlay */
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -40%;
        right: -10%;
        width: 60%;
        height: 180%;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.18) 0%, rgba(99, 102, 241, 0.12) 40%, transparent 75%);
        pointer-events: none;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.35);
        color: #38bdf8;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 1.25rem;
    }

    .hero-badge-pulse {
        width: 8px;
        height: 8px;
        background-color: #38bdf8;
        border-radius: 50%;
        box-shadow: 0 0 10px #38bdf8;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1.1;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 1.25rem 0;
        letter-spacing: -0.03em;
    }

    .hero-subtitle {
        font-size: 1.18rem;
        color: #94a3b8;
        max-width: 850px;
        line-height: 1.65;
        margin: 0 0 2rem 0;
        font-weight: 400;
    }

    .hero-features {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
    }

    .feature-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 8px 18px;
        border-radius: 12px;
        font-size: 0.9rem;
        color: #e2e8f0;
        font-weight: 600;
        backdrop-filter: blur(12px);
    }

    /* Section Headings */
    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #0f172a;
        margin: 2rem 0 1.25rem 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Interactive Nav Grid Cards */
    .nav-grid-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 1.6rem;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1.5rem;
    }
    .nav-grid-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 30px -10px rgba(99, 102, 241, 0.12);
        border-color: #818cf8;
    }

    .nav-icon-wrapper {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    /* Pipeline Cards */
    .pipeline-step-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.25rem 0.75rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease;
        height: 100%;
    }
    .pipeline-step-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px rgba(99, 102, 241, 0.1);
        border-color: #6366f1;
    }
    .pipeline-step-num {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 800;
        color: #6366f1;
        background: #eef2ff;
        padding: 2px 8px;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .pipeline-step-icon {
        font-size: 1.8rem;
        margin-bottom: 0.3rem;
    }
    .pipeline-step-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 0.95rem;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .pipeline-step-desc {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# Hero Section
# ============================================

hero_badge_text = "Cybersecurity Intelligence Platform"
hero_subtitle = (
    "Your trusted platform for curated cybersecurity intelligence, threat analysis, "
    "and multi-agent magazine generation — delivered as professionally formatted publications."
)
feature_pills = [
    "🔍 Threat Intelligence",
    "📊 Security Research",
    "🏢 Industry Analysis",
    "💡 Expert Insights",
]

pills_html = "".join(f'<div class="feature-pill">{p}</div>' for p in feature_pills)

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-badge">
        <span class="hero-badge-pulse"></span>
        {hero_badge_text}
    </div>
    <h1 class="hero-title">CyberQuill</h1>
    <p class="hero-subtitle">{hero_subtitle}</p>
    <div class="hero-features">
        {pills_html}
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# Latest Issue Banner (if pipeline has been run)
# ============================================

if "pipeline_result" in st.session_state:
    res = st.session_state["pipeline_result"]
    issue_num = res.get("issue_number", "—")
    ts = res.get("timestamp", "")
    art_count = res.get("magazine_count", 0)

    st.markdown(f"""
    <div class="issue-banner">
        <div class="issue-number">Issue #{issue_num:03d}</div>
        <div class="issue-title">Latest Issue Available</div>
        <div class="issue-meta">{art_count} articles &bull; Published {ts}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# Featured Article (if articles exist in session)
# ============================================

if "pipeline_result" in st.session_state:
    m_articles = st.session_state["pipeline_result"].get("magazine_articles", [])
    if m_articles:
        featured = m_articles[0]
        read_time = estimate_article_reading_time(featured)
        bg, fg, border = get_category_pill_style(featured.category)

        excerpt = (featured.executive_summary or "")[:250]
        if len(featured.executive_summary or "") > 250:
            excerpt += "..."

        st.markdown(f"""
        <div class="featured-article">
            <div class="featured-label">⭐ Featured Article</div>
            <div class="featured-title">{featured.title}</div>
            <div class="featured-excerpt">{excerpt}</div>
            <div class="featured-meta">
                <span style="background:{bg}; color:{fg}; border:1px solid {border}; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.75rem;">{featured.category}</span>
                <span>📖 {read_time} min read</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# Quick Navigation (Attractive Grid Cards)
# ============================================

st.markdown('<div class="section-title">🧭 Explore CyberQuill</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="nav-card">
        <div>
            <div class="nav-card-top">
                <div class="nav-card-icon" style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); color: #2563eb;">📰</div>
                <span class="nav-card-tag" style="background:#eff6ff; color:#1d4ed8; border-color:#bfdbfe;">LIVE FEED</span>
            </div>
            <div class="nav-card-title">News Feed</div>
            <div class="nav-card-desc">
                Browse the latest cybersecurity news collected in real-time from top security publications and threat intelligence sources.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Latest_News.py", label="Browse News →", icon="📰", use_container_width=True)

with c2:
    st.markdown("""
    <div class="nav-card">
        <div>
            <div class="nav-card-top">
                <div class="nav-card-icon" style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); color: #dc2626;">🏷️</div>
                <span class="nav-card-tag" style="background:#fef2f2; color:#b91c1c; border-color:#fca5a5;">CURATED</span>
            </div>
            <div class="nav-card-title">Topics & Categories</div>
            <div class="nav-card-desc">
                Explore articles organized by topic — malware analysis, data breaches, AI security, cloud threats, and more.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Categories.py", label="View Topics →", icon="🏷️", use_container_width=True)

with c3:
    st.markdown("""
    <div class="nav-card">
        <div>
            <div class="nav-card-top">
                <div class="nav-card-icon" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); color: #16a34a;">📚</div>
                <span class="nav-card-tag" style="background:#f0fdf4; color:#15803d; border-color:#86efac;">VECTOR RAG</span>
            </div>
            <div class="nav-card-title">RAG Testing</div>
            <div class="nav-card-desc">
                Query ChromaDB vector index loaded with OWASP Top 10, NIST CSF 2.0, and MITRE ATT&CK knowledge frameworks.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_RAG_Testing.py", label="Test RAG Queries →", icon="📚", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)

with c4:
    st.markdown("""
    <div class="nav-card">
        <div>
            <div class="nav-card-top">
                <div class="nav-card-icon" style="background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%); color: #9333ea;">📄</div>
                <span class="nav-card-tag" style="background:#faf5ff; color:#7e22ce; border-color:#d8b4fe;">PUBLISH</span>
            </div>
            <div class="nav-card-title">Publish New Issue</div>
            <div class="nav-card-desc">
                Generate a new magazine issue — curated articles are enriched, professionally written, reviewed, and compiled into a downloadable PDF.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_Generate_Magazine.py", label="Publish Issue →", icon="📄", use_container_width=True)

with c5:
    st.markdown("""
    <div class="nav-card">
        <div>
            <div class="nav-card-top">
                <div class="nav-card-icon" style="background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%); color: #ea580c;">📋</div>
                <span class="nav-card-tag" style="background:#fff7ed; color:#c2410c; border-color:#fdba74;">TELEMETRY</span>
            </div>
            <div class="nav-card-title">Agent Logs</div>
            <div class="nav-card-desc">
                Monitor agent execution logs, reflection cycles, state updates, and system telemetry in real-time.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/5_Agent_Logs.py", label="View System Logs →", icon="📋", use_container_width=True)

with c6:
    st.markdown("""
    <div class="nav-card">
        <div>
            <div class="nav-card-top">
                <div class="nav-card-icon" style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); color: #475569;">ℹ️</div>
                <span class="nav-card-tag" style="background:#f8fafc; color:#334155; border-color:#cbd5e1;">ABOUT</span>
            </div>
            <div class="nav-card-title">About CyberQuill</div>
            <div class="nav-card-desc">
                Learn about CyberQuill's mission, the intelligence sources we monitor, and the technology behind the platform.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/6_About.py", label="Learn More →", icon="ℹ️", use_container_width=True)


# ============================================
# Pipeline Architecture Visualization
# ============================================

st.markdown('<div class="section-title" style="margin-top: 3rem;">⚡ LangGraph Pipeline Flow</div>', unsafe_allow_html=True)

p_cols = st.columns(7)
pipeline_steps = [
    ("1", "📡", "Collector", "RSS Feeds"),
    ("2", "🔍", "Duplicate", "Deduplication"),
    ("3", "🏷️", "Classifier", "Attack Vector"),
    ("4", "📚", "RAG", "Knowledge Base"),
    ("5", "✍️", "Writer", "Article Gen"),
    ("6", "📝", "Reviewer", "Quality Check"),
    ("7", "📄", "PDF", "Publication"),
]

for i, (num, icon, name, desc) in enumerate(pipeline_steps):
    with p_cols[i]:
        st.markdown(
            f"""<div class="pipeline-step-card">
                <span class="pipeline-step-num">STEP {num}</span>
                <div class="pipeline-step-icon">{icon}</div>
                <div class="pipeline-step-title">{name}</div>
                <div class="pipeline-step-desc">{desc}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("""
<div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 0.9rem 1.25rem; text-align: center; font-size: 0.88rem; color: #475569; margin-top: 1.25rem;">
    ⟳ <b>Reflection Quality Loop:</b> Reviewer Agent validates compliance & scores output. Triggers automated revision up to 2 cycles if required.
</div>
""", unsafe_allow_html=True)

# ============================================
# Footer
# ============================================

st.divider()
st.markdown(
    "<div style='text-align:center; color:#94a3b8; font-size:0.85rem; font-weight: 500; margin-bottom:1rem;'>"
    "Generated by CyberQuill"
    "</div>",
    unsafe_allow_html=True,
)
