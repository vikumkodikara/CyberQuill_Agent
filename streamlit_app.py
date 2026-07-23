"""
CyberQuill — Streamlit Home Page
==================================

Purpose:
    Entry point for the CyberQuill Streamlit multi-page application.
    Displays the project overview, system status, and navigation guide.

How Streamlit multi-page apps work:
    - This file (streamlit_app.py) is the HOME page
    - Files in the pages/ directory become sidebar navigation items
    - Streamlit auto-discovers pages and orders them by filename prefix

How to run:
    streamlit run streamlit_app.py
"""

import streamlit as st
from pathlib import Path


# ============================================
# Page Configuration (must be first st call)
# ============================================

st.set_page_config(
    page_title="CyberQuill Weekly",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================
# Custom CSS for Professional Styling
# ============================================

st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* Header styling */
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1a237e, #42a5f5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
    }

    .hero-subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
    }

    /* Card styling */
    .status-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid #42a5f5;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a237e;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.3rem;
    }

    /* Pipeline flow diagram */
    .pipeline-step {
        background: #f0f4ff;
        border: 1px solid #c5cae9;
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
        font-size: 0.9rem;
        font-weight: 600;
        color: #283593;
    }

    .pipeline-arrow {
        text-align: center;
        font-size: 1.5rem;
        color: #42a5f5;
        padding: 0.3rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# Hero Section
# ============================================

st.markdown('<p class="hero-title">🛡️ CyberQuill Weekly</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">AI-Powered Cybersecurity Intelligence Platform</p>',
    unsafe_allow_html=True,
)

st.divider()


# ============================================
# System Status
# ============================================

st.subheader("📊 System Status")

# Check component availability
has_groq_key = False
has_openrouter_key = False
try:
    from config.settings import settings
    has_groq_key = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here")
    has_openrouter_key = bool(settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != "your_openrouter_api_key_here")
except Exception:
    pass

has_chroma = False
try:
    import chromadb
    has_chroma = True
except ImportError:
    pass

has_langgraph = False
try:
    import langgraph
    has_langgraph = True
except ImportError:
    pass

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Groq API", "✅ Ready" if has_groq_key else "⚠️ No Key")
with col2:
    st.metric("OpenRouter API", "✅ Ready" if has_openrouter_key else "⚠️ No Key")
with col3:
    st.metric("ChromaDB", "✅ Installed" if has_chroma else "❌ Missing")
with col4:
    st.metric("LangGraph", "✅ Installed" if has_langgraph else "❌ Missing")

if not has_groq_key:
    st.info(
        "💡 **Tip:** Add your Groq API key to `.env` for LLM-powered classification and writing. "
        "Without it, the system uses fallback modes (keyword classification, template writing)."
    )


# ============================================
# Pipeline Overview
# ============================================

st.subheader("🔄 Pipeline Architecture")

st.markdown("""
The CyberQuill pipeline processes cybersecurity news through **6 intelligent agents** 
connected via a **LangGraph StateGraph** with a **reflection loop** for quality assurance.
""")

# Pipeline flow visualization
cols = st.columns(7)
agents = [
    ("📡", "Collector", "RSS Feeds"),
    ("🔍", "Duplicate", "Deduplication"),
    ("🏷️", "Classifier", "Categorization"),
    ("📚", "RAG", "Enrichment"),
    ("✍️", "Writer", "Article Gen"),
    ("📝", "Reviewer", "Quality Check"),
    ("📄", "PDF", "Magazine"),
]

for i, (icon, name, desc) in enumerate(agents):
    with cols[i]:
        st.markdown(
            f"""<div class="pipeline-step">
            {icon}<br><b>{name}</b><br>
            <span style="font-size:0.75rem;font-weight:normal;color:#666">{desc}</span>
            </div>""",
            unsafe_allow_html=True,
        )

st.caption("⟳ Reviewer → Writer reflection loop runs up to 2 revision cycles for quality improvement")


# ============================================
# Quick Navigation
# ============================================

st.subheader("🧭 Quick Navigation")

nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.markdown("""
    #### 📰 Latest News
    Browse the latest cybersecurity articles collected from RSS feeds.
    View raw articles before any processing.
    """)
    st.page_link("pages/1_Latest_News.py", label="Go to Latest News →", icon="📰")

    st.markdown("""
    #### 🏷️ Categories
    Explore articles grouped by threat category.
    See classification results and confidence scores.
    """)
    st.page_link("pages/2_Categories.py", label="Go to Categories →", icon="🏷️")

with nav_col2:
    st.markdown("""
    #### 📚 RAG Testing
    Test the retrieval-augmented generation system interactively.
    Query the knowledge base and see relevant context.
    """)
    st.page_link("pages/3_RAG_Testing.py", label="Go to RAG Testing →", icon="📚")

    st.markdown("""
    #### 📰 Generate Magazine
    Run the full pipeline and generate a PDF magazine.
    Download your CyberQuill Weekly issue.
    """)
    st.page_link("pages/4_Generate_Magazine.py", label="Go to Magazine →", icon="📰")

with nav_col3:
    st.markdown("""
    #### 📋 Agent Logs
    Monitor the pipeline execution in real-time.
    View structured logs from all agents.
    """)
    st.page_link("pages/5_Agent_Logs.py", label="Go to Logs →", icon="📋")

    st.markdown("""
    #### ℹ️ About
    Learn about the project architecture, design patterns,
    and the technology stack.
    """)
    st.page_link("pages/6_About.py", label="Go to About →", icon="ℹ️")


# ============================================
# Footer
# ============================================

st.divider()
st.markdown(
    "<div style='text-align:center; color:#999; font-size:0.85rem;'>"
    "CyberQuill Weekly — Built with LangGraph, Streamlit, and ❤️"
    "</div>",
    unsafe_allow_html=True,
)
