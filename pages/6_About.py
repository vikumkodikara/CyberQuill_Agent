"""
CyberQuill — About Page
==========================

Project information, architecture overview, design patterns used,
and technology stack documentation.
"""

import streamlit as st
from utils.theme import render_page_header, render_sidebar_controls

st.set_page_config(page_title="About — CyberQuill", page_icon="ℹ️", layout="wide")

render_sidebar_controls()

render_page_header(
    title="About CyberQuill — Architecture & Design",
    subtitle="Mission overview, LangGraph multi-agent topology, agentic AI design patterns, technology stack, and intelligence sources.",
    icon="ℹ️"
)

# ============================================
# Project Overview
# ============================================

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">
    // OUR MISSION
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: #111827; border: 1px solid #1F2937; border-left: 3px solid #00D4FF; border-radius: 0 8px 8px 0; padding: 1.5rem 1.75rem; margin-bottom: 2rem;">
    <p style="font-size: 0.95rem; color: #CBD5E1; line-height: 1.65; margin: 0;">
        <b style="color: #00D4FF;">CyberQuill</b> is an autonomous multi-agent intelligence platform engineered to continuously aggregate, deduplicate, categorize, enrich, write, review, and publish cybersecurity threat magazines.
        Our goal is to make cybersecurity intelligence accessible, readable, and actionable for security professionals, researchers, and technology enthusiasts.
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# Architecture Topology
# ============================================

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">
    // LANGGRAPH ORCHESTRATION TOPOLOGY
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: #030712; border-radius: 8px; padding: 1.5rem; color: #00D4FF; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; overflow-x: auto; border: 1px solid #1F2937; margin-bottom: 2rem; line-height: 1.6;">
<pre style="margin: 0; color: #00D4FF;">
                    ┌────────────────────────────────────────────────────────┐
                    │            <span style="color: #F1F5F9;">LangGraph StateGraph Pipeline</span>               │
                    │                                                        │
  <span style="color: #34D399;">RSS Feeds</span> ──────▶ │  <span style="color: #FCD34D;">1. Collector</span> ──▶ <span style="color: #A78BFA;">2. Duplicate</span> ──▶ <span style="color: #FF3366;">3. Classifier</span>      │
                    │                                           │            │
                    │                                           ▼            │
                    │                                     <span style="color: #34D399;">4. RAG Agent</span>       │
                    │                                           │            │
                    │                                           ▼            │
                    │                      ┌────────── <span style="color: #FCD34D;">5. Writer Agent</span> ◄───┐ │
                    │                      │                           │   │
                    │                      ▼                           │   │
                    │              <span style="color: #FF6B00;">6. Reviewer Agent</span> ─── <span style="color: #64748B;">revise?</span> ──────┘   │
                    │                      │                               │
                    │            <span style="color: #34D399;">approved</span>  ▼                               │
                    │              <span style="color: #00D4FF;">7. PDF Generator</span>                        │
                    └────────────────────────────────────────────────────────┘
                                           │
                                           ▼
                                📄 <span style="color: #F1F5F9;">CyberQuill Magazine.pdf</span>
</pre>
</div>
""", unsafe_allow_html=True)

# ============================================
# Agentic AI Design Patterns
# ============================================

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #7C3AED; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">
    // AGENTIC AI DESIGN PATTERNS
</div>
""", unsafe_allow_html=True)

patterns = {
    "🔧 Tool Use Pattern": {
        "description": "Agents dynamically leverage external tools for live data retrieval and vector store indexing.",
        "where": "Collector (feedparser RSS engine), RAG Agent (ChromaDB vector retriever), Writer Agent (Groq LLM).",
        "color": "#00D4FF",
    },
    "🔀 Router Pattern": {
        "description": "Conditional routing in the orchestrator pipeline based on execution output and quality thresholds.",
        "where": "LangGraph StateGraph conditional edges determining revision loops or approval branches.",
        "color": "#A78BFA",
    },
    "📋 Task Decomposition": {
        "description": "Decomposes end-to-end publishing into decoupled, specialized micro-agent tasks.",
        "where": "7 distinct agents with single responsibilities and validated Pydantic contract schemas.",
        "color": "#FF3366",
    },
    "🔄 Reflection / Self-Critique Pattern": {
        "description": "Output is evaluated by a reviewer agent that triggers automated feedback-driven revision cycles.",
        "where": "Reviewer → Writer reflection loop running up to 2 revision iterations.",
        "color": "#FCD34D",
    },
    "👔 Orchestrator-Worker Architecture": {
        "description": "Central coordinator manages state transitions while worker agents perform core tasks.",
        "where": "LangGraph StateGraph serving as state coordinator across 6 workers and PDF generator.",
        "color": "#34D399",
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

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">
    // TECHNOLOGY STACK
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #34D399; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">
    // MONITORED THREAT INTELLIGENCE FEEDS
</div>
""", unsafe_allow_html=True)

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
        <div style="background: #111827; border: 1px solid #1F2937; border-left: 3px solid #34D399; border-radius: 0 8px 8px 0; padding: 12px 16px; margin-bottom: 8px;">
            <div style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #F1F5F9; font-size: 13px;">📡 {name}</div>
            <a href="{url}" target="_blank" style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-decoration: none;">{url} ↗</a>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# Statistics
# ============================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">
    // SYSTEM METRICS
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Autonomous Agents", "6")
col2.metric("Test Coverage", "170+ Tests")
col3.metric("Monitored Feeds", "6 Sources")
col4.metric("Knowledge Base", "3 Frameworks")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top: 1px solid #1F2937; padding-top: 1rem; text-align: center;">
    <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #374151; letter-spacing: 0.1em;">GENERATED BY CYBERQUILL</span>
</div>
""", unsafe_allow_html=True)
