"""
CyberQuill — About Page
==========================

Project information, architecture overview, design patterns used,
and technology stack documentation.
Supports Magazine Mode (simplified) and Debug Mode (full technical details).
"""

import streamlit as st
from utils.theme import render_page_header, render_sidebar_controls

st.set_page_config(page_title="About — CyberQuill", page_icon="ℹ️", layout="wide")

render_sidebar_controls()

magazine_mode = is_magazine_mode()

render_page_header(
    title="About CyberQuill — Architecture & Design",
    subtitle="Mission overview, LangGraph multi-agent topology, agentic AI design patterns, technology stack, and intelligence sources.",
    icon="ℹ️"
)

# ============================================
# Project Overview
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-bottom:1rem;'>🎯 Our Mission</h4>", unsafe_allow_html=True)

st.markdown("""
<div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:16px; padding:1.5rem; box-shadow:0 4px 12px rgba(0,0,0,0.03); margin-bottom:2rem;">
    <p style="font-size:1.02rem; color:#334155; line-height:1.65; margin:0;">
        <b>CyberQuill</b> is an autonomous multi-agent intelligence platform engineered to continuously aggregate, deduplicate, categorize, enrich, write, review, and publish cybersecurity threat magazines.
        Our goal is to make cybersecurity intelligence accessible, readable, and actionable for security professionals, researchers, and technology enthusiasts.
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# Architecture Topology
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-bottom:1rem;'>🏗️ LangGraph Orchestration Topology</h4>", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f172a; border-radius:16px; padding:1.5rem; color:#38bdf8; font-family:'Courier New', monospace; font-size:0.88rem; overflow-x:auto; border:1px solid #1e293b; box-shadow:0 10px 25px rgba(0,0,0,0.2); margin-bottom:2rem;">
                    ┌────────────────────────────────────────────────────────┐
                    │            LangGraph StateGraph Pipeline               │
                    │                                                        │
  RSS Feeds ──────▶ │  1. Collector ──▶ 2. Duplicate ──▶ 3. Classifier      │
                    │                                           │            │
                    │                                           ▼            │
                    │                                     4. RAG Agent       │
                    │                                           │            │
                    │                                           ▼            │
                    │                      ┌────────── 5. Writer Agent ◄───┐ │
                    │                      │                           │   │
                    │                      ▼                           │   │
                    │              6. Reviewer Agent ─── revise? ──────┘   │
                    │                      │                               │
                    │            approved  ▼                               │
                    │              7. PDF Generator                        │
                    └────────────────────────────────────────────────────────┘
                                           │
                                           ▼
                                📄 CyberQuill Magazine.pdf
</div>
""", unsafe_allow_html=True)

# ============================================
# Agentic AI Design Patterns
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-bottom:1rem;'>🤖 Implemented Agentic AI Design Patterns</h4>", unsafe_allow_html=True)

patterns = {
    "🔧 Tool Use Pattern": {
        "description": "Agents dynamically leverage external tools for live data retrieval and vector store indexing.",
        "where": "Collector (feedparser RSS engine), RAG Agent (ChromaDB vector retriever), Writer Agent (Groq LLM).",
    },
    "🔀 Router Pattern": {
        "description": "Conditional routing in the orchestrator pipeline based on execution output and quality thresholds.",
        "where": "LangGraph StateGraph conditional edges determining revision loops or approval branches.",
    },
    "📋 Task Decomposition": {
        "description": "Decomposes end-to-end publishing into decoupled, specialized micro-agent tasks.",
        "where": "7 distinct agents with single responsibilities and validated Pydantic contract schemas.",
    },
    "🔄 Reflection / Self-Critique Pattern": {
        "description": "Output is evaluated by a reviewer agent that triggers automated feedback-driven revision cycles.",
        "where": "Reviewer → Writer reflection loop running up to 2 revision iterations.",
    },
    "👔 Orchestrator-Worker Architecture": {
        "description": "Central coordinator manages state transitions while worker agents perform core tasks.",
        "where": "LangGraph StateGraph serving as state coordinator across 6 workers and PDF generator.",
    },
}

for pattern_name, info in patterns.items():
    with st.expander(pattern_name):
        st.markdown(f"**Description:** {info['description']}")
        st.markdown(f"**Implementation Site:** `{info['where']}`")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# Technology Stack
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-bottom:1rem;'>🛠️ Technology Stack</h4>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ##### Core Orchestration & UI
    | Framework | Role |
    |-----------|------|
    | **LangGraph** | Multi-agent state machine & cyclic flow |
    | **LangChain** | LLM chain integration |
    | **Streamlit** | Multi-page web dashboard |
    | **Pydantic** | Schema validation & type safety |

    ##### AI & Inference Providers
    | Provider | Model | Purpose |
    |----------|-------|---------|
    | **Groq** | Llama 3.3 70B | High-speed classification, writing & review |
    | **OpenRouter** | Llama 4 Maverick | Complex reasoning fallback |
    """)

with col2:
    st.markdown("""
    ##### Vector Search & PDF Engine
    | Tool | Purpose |
    |------|---------|
    | **ChromaDB** | Local persistent vector database |
    | **Sentence-Transformers** | Text embedding model (`all-MiniLM-L6-v2`) |
    | **feedparser** | RSS feed parsing & normalization |
    | **ReportLab** | PDF document & cover page generation |

    ##### Quality & Testing
    | Component | Purpose |
    |-----------|---------|
    | **pytest** | Unit, integration & pipeline test suites |
    | **Python logging** | File-based structured logger |
    """)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# Monitored RSS Feeds
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-bottom:1rem;'>📡 Monitored Threat Intelligence Feeds</h4>", unsafe_allow_html=True)

sources = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Bleeping Computer", "https://www.bleepingcomputer.com/feed/"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("SecurityWeek", "https://www.securityweek.com/feed/"),
    ("Dark Reading", "https://www.darkreading.com/rss.xml"),
    ("CISA Bulletins", "https://www.cisa.gov/news.xml"),
]

s_cols = st.columns(2)
for i, (name, url) in enumerate(sources):
    with s_cols[i % 2]:
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:0.9rem 1.1rem; margin-bottom:0.75rem;">
            <div style="font-weight:700; color:#0f172a;">📡 {name}</div>
            <a href="{url}" target="_blank" style="font-size:0.82rem; color:#4f46e5; text-decoration:none;">{url} ↗</a>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# Statistics
# ============================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-bottom:1rem;'>📊 System Metrics</h4>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Autonomous Agents", "6")
col2.metric("Test Coverage", "170+ Tests")
col3.metric("Monitored Feeds", "6 Sources")
col4.metric("Knowledge Base", "3 Frameworks")

st.divider()
st.markdown(
    "<div style='text-align:center; color:#94a3b8; font-size:0.85rem; font-weight:500;'>"
    "Generated by CyberQuill"
    "</div>",
    unsafe_allow_html=True,
)
