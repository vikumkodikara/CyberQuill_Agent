"""
CyberQuill — Streamlit Home Page & Navigation Dashboard
========================================================

Entry point for the CyberQuill Streamlit multi-page application.
Dark cybersecurity terminal aesthetic with threat intelligence branding.
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

# Apply dark theme
apply_custom_theme()
render_sidebar_controls()

# ============================================
# Hero Section — Terminal Style
# ============================================

st.markdown("""
<div style="background: #111827; border: 1px solid #1F2937; border-radius: 12px; padding: 3rem 2.5rem; margin-bottom: 2rem; position: relative; overflow: hidden;">
    <div style="position: absolute; top: -40%; right: -10%; width: 50%; height: 200%; background: radial-gradient(circle, rgba(0, 212, 255, 0.06) 0%, transparent 60%); pointer-events: none;"></div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span class="pulse-dot"></span>
        THREAT INTELLIGENCE PLATFORM
    </div>
    <h1 style="font-family: 'Inter', sans-serif; font-size: 3rem; font-weight: 700; color: #F1F5F9; margin: 0 0 1rem 0; letter-spacing: -0.02em;">
        ◈ CYBERQUILL<span class="cursor-blink">_</span>
    </h1>
    <p style="font-size: 1.05rem; color: #64748B; max-width: 700px; line-height: 1.65; margin: 0 0 1.5rem 0;">
        Autonomous multi-agent intelligence platform for curated cybersecurity threat analysis, delivered as professionally formatted publications.
    </p>
    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #00D4FF; background: #00D4FF12; border: 1px solid #00D4FF33; padding: 6px 14px; border-radius: 4px;">🔍 THREAT INTEL</span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #A78BFA; background: #7C3AED12; border: 1px solid #7C3AED33; padding: 6px 14px; border-radius: 4px;">📊 SECURITY RESEARCH</span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #34D399; background: #10B98112; border: 1px solid #10B98133; padding: 6px 14px; border-radius: 4px;">🏢 INDUSTRY ANALYSIS</span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #FCD34D; background: #F59E0B12; border: 1px solid #F59E0B33; padding: 6px 14px; border-radius: 4px;">💡 EXPERT INSIGHTS</span>
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
        <div class="issue-meta">{art_count} articles &bull; Generated {ts}</div>
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
            <div class="featured-label">◈ FEATURED ARTICLE</div>
            <div class="featured-title">{featured.title}</div>
            <div class="featured-excerpt">{excerpt}</div>
            <div class="featured-meta">
                <span style="background:{bg}; color:{fg}; border:1px solid {border}; padding:3px 10px; border-radius:4px; font-weight:700; font-size:11px; font-family:'JetBrains Mono',monospace;">{featured.category}</span>
                <span style="font-family:'JetBrains Mono',monospace; font-size:12px;">📖 {read_time} min read</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# Navigation Grid
# ============================================

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin: 2rem 0 1rem;">
    // EXPLORE MODULES
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="nav-card">
        <div>
            <div class="nav-card-top">
                <div class="nav-card-icon" style="background: #00D4FF15; color: #00D4FF; border: 1px solid #00D4FF33;">📰</div>
                <span class="nav-card-tag" style="background:#00D4FF15; color:#00D4FF; border:1px solid #00D4FF33;">LIVE FEED</span>
            </div>
            <div class="nav-card-title">News Feed</div>
            <div class="nav-card-desc">
                Real-time cybersecurity news from top security publications and threat intelligence sources.
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
                <div class="nav-card-icon" style="background: #FF336615; color: #FF3366; border: 1px solid #FF336633;">🏷️</div>
                <span class="nav-card-tag" style="background:#FF336615; color:#FF3366; border:1px solid #FF336633;">CURATED</span>
            </div>
            <div class="nav-card-title">Topics & Categories</div>
            <div class="nav-card-desc">
                Articles organized by topic — malware, breaches, AI security, cloud threats, and more.
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
                <div class="nav-card-icon" style="background: #34D39915; color: #34D399; border: 1px solid #34D39933;">📚</div>
                <span class="nav-card-tag" style="background:#34D39915; color:#34D399; border:1px solid #34D39933;">VECTOR RAG</span>
            </div>
            <div class="nav-card-title">RAG Testing</div>
            <div class="nav-card-desc">
                Query ChromaDB vector index with OWASP, NIST CSF, and MITRE ATT&CK frameworks.
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
                <div class="nav-card-icon" style="background: #7C3AED15; color: #A78BFA; border: 1px solid #7C3AED33;">📄</div>
                <span class="nav-card-tag" style="background:#7C3AED15; color:#A78BFA; border:1px solid #7C3AED33;">GENERATE</span>
            </div>
            <div class="nav-card-title">Generate a Magazine</div>
            <div class="nav-card-desc">
                Run the full pipeline — curate, enrich, write, review, and compile a downloadable PDF.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_Generate_Magazine.py", label="Generate Magazine →", icon="📄", use_container_width=True)

with c5:
    st.markdown("""
    <div class="nav-card">
        <div>
            <div class="nav-card-top">
                <div class="nav-card-icon" style="background: #FCD34D15; color: #FCD34D; border: 1px solid #FCD34D33;">📋</div>
                <span class="nav-card-tag" style="background:#FCD34D15; color:#FCD34D; border:1px solid #FCD34D33;">TELEMETRY</span>
            </div>
            <div class="nav-card-title">Agent Logs</div>
            <div class="nav-card-desc">
                Monitor agent execution, reflection cycles, state transitions, and system telemetry.
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
                <div class="nav-card-icon" style="background: #64748B15; color: #94A3B8; border: 1px solid #64748B33;">ℹ️</div>
                <span class="nav-card-tag" style="background:#64748B15; color:#94A3B8; border:1px solid #64748B33;">ABOUT</span>
            </div>
            <div class="nav-card-title">About CyberQuill</div>
            <div class="nav-card-desc">
                Architecture, design patterns, technology stack, and intelligence sources.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/6_About.py", label="Learn More →", icon="ℹ️", use_container_width=True)


# ============================================
# Pipeline Architecture Visualization
# ============================================

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin: 2.5rem 0 1rem;">
    // LANGGRAPH PIPELINE FLOW
</div>
""", unsafe_allow_html=True)

p_cols = st.columns(7)
pipeline_steps = [
    ("01", "📡", "Collector", "RSS Feeds"),
    ("02", "🔍", "Duplicate", "Dedup"),
    ("03", "🏷️", "Classifier", "Categories"),
    ("04", "📚", "RAG", "Knowledge"),
    ("05", "✍️", "Writer", "Articles"),
    ("06", "📝", "Reviewer", "Quality"),
    ("07", "📄", "PDF", "Publication"),
]

for i, (num, icon, name, desc) in enumerate(pipeline_steps):
    with p_cols[i]:
        st.markdown(
            f"""<div class="pipeline-step">
                <div class="step-number">STEP {num}</div>
                <div class="step-icon">{icon}</div>
                <div class="step-name">{name}</div>
                <div class="step-sub">{desc}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("""
<div style="background: #111827; border: 1px solid #1F2937; border-radius: 8px; padding: 0.9rem 1.25rem; text-align: center; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #64748B; margin-top: 1rem;">
    ⟳ <span style="color: #A78BFA;">REFLECTION LOOP</span> — Reviewer validates compliance & scores output. Triggers automated revision up to 2 cycles.
</div>
""", unsafe_allow_html=True)

# ============================================
# Footer
# ============================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top: 1px solid #1F2937; padding-top: 1rem; text-align: center;">
    <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #374151; letter-spacing: 0.1em;">GENERATED BY CYBERQUILL</span>
</div>
""", unsafe_allow_html=True)
