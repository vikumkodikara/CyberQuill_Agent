"""
CyberQuill — About Page
==========================

Project information, architecture overview, design patterns used,
and technology stack documentation.
"""

import streamlit as st

st.set_page_config(page_title="About — CyberQuill", page_icon="ℹ️", layout="wide")

st.title("ℹ️ About CyberQuill")
st.divider()


# ============================================
# Project Overview
# ============================================

st.subheader("🎯 What is CyberQuill?")
st.markdown("""
**CyberQuill** is a multi-agent cybersecurity intelligence platform that:

1. **Collects** news from 6+ RSS feeds (The Hacker News, Bleeping Computer, Krebs on Security, etc.)
2. **Removes duplicates** using URL matching and fuzzy title comparison
3. **Classifies** articles by threat category (Malware, Data Breach, AI Security, etc.)
4. **Enriches** content with RAG context from OWASP, NIST CSF, and MITRE ATT&CK
5. **Generates** professional magazine-style articles using LLM
6. **Reviews** content quality with a reflection/self-critique pattern
7. **Exports** a downloadable PDF magazine — "CyberQuill Weekly"
""")


# ============================================
# Architecture
# ============================================

st.subheader("🏗️ Architecture")

st.markdown("""
```
                    ┌──────────────────────────────────────────┐
                    │        LangGraph StateGraph Pipeline     │
                    │                                          │
  RSS Feeds ──────▶ │  Collector → Duplicate → Classifier      │
                    │                              │            │
                    │                              ▼            │
                    │                             RAG           │
                    │                              │            │
                    │                              ▼            │
                    │                 ┌──── Writer ◀────┐       │
                    │                 │                  │       │
                    │                 ▼                  │       │
                    │              Reviewer ─── revise? ─┘       │
                    │                 │                          │
                    │           approved ▼                      │
                    │            PDF Generator                  │
                    └──────────────────────────────────────────┘
                                      │
                                      ▼
                              CyberQuill Weekly.pdf
```
""")


# ============================================
# Agentic AI Design Patterns
# ============================================

st.subheader("🤖 Agentic AI Design Patterns")

patterns = {
    "🔧 Tool Use": {
        "description": "Agents use external tools to fetch data or query databases",
        "where": "Collector (feedparser), RAG (ChromaDB), Writer (LLM API)",
    },
    "🔀 Router Pattern": {
        "description": "Routes articles through appropriate processing based on conditions",
        "where": "Orchestrator — conditional edges in LangGraph StateGraph",
    },
    "📋 Planning & Decomposition": {
        "description": "Breaks magazine generation into sequential sub-tasks",
        "where": "Pipeline decomposes into 7 agents with clear responsibilities",
    },
    "🔄 Reflection / Self-Critique": {
        "description": "Agent reviews its output and iterates to improve quality",
        "where": "Reviewer → Writer loop (max 2 cycles) based on quality scores",
    },
    "👔 Orchestrator-Worker": {
        "description": "Central orchestrator delegates work to specialized agents",
        "where": "LangGraph StateGraph coordinates all 6 agents + PDF generator",
    },
}

for pattern_name, info in patterns.items():
    with st.expander(pattern_name):
        st.markdown(f"**What it is:** {info['description']}")
        st.markdown(f"**Where implemented:** {info['where']}")


# ============================================
# Technology Stack
# ============================================

st.subheader("🛠️ Technology Stack")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Core Framework
    | Technology | Purpose |
    |-----------|---------|
    | **LangGraph** | Agent orchestration pipeline |
    | **LangChain** | LLM integration layer |
    | **Streamlit** | Web UI framework |
    | **Pydantic** | Data validation & schemas |

    #### LLM Providers
    | Provider | Used For |
    |----------|----------|
    | **Groq** (Llama 3.3) | Classification, Writing, Review |
    | **OpenRouter** (Llama 4) | Complex reasoning tasks |
    """)

with col2:
    st.markdown("""
    #### Data & Storage
    | Technology | Purpose |
    |-----------|---------|
    | **ChromaDB** | Vector database for RAG |
    | **sentence-transformers** | Text embeddings |
    | **feedparser** | RSS feed parsing |
    | **ReportLab** | PDF generation |

    #### Quality
    | Technology | Purpose |
    |-----------|---------|
    | **pytest** | Unit & integration testing |
    | **pydantic-settings** | Configuration management |
    | **Python logging** | Structured logging |
    """)


# ============================================
# Model Strategy
# ============================================

st.subheader("🧠 Model Strategy")

st.markdown("""
CyberQuill uses a **dual-model architecture** to balance speed and quality:

| Model | Provider | Used For | Why |
|-------|----------|----------|-----|
| Llama 3.3 70B | Groq | Classification, Writing, Review | Ultra-fast inference, generous free tier |
| Llama 4 Maverick | OpenRouter | Complex reasoning (future) | Superior reasoning for hard tasks |

Both models have **graceful fallback modes**:
- **Classification**: Falls back to keyword matching
- **Writing**: Falls back to template-based article generation
- **Review**: Falls back to rule-based quality checks
""")


# ============================================
# RSS Sources
# ============================================

st.subheader("📡 RSS Sources")

sources = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Bleeping Computer", "https://www.bleepingcomputer.com/feed/"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("SecurityWeek", "https://www.securityweek.com/feed/"),
    ("Dark Reading", "https://www.darkreading.com/rss.xml"),
    ("CISA", "https://www.cisa.gov/news.xml"),
]

for name, url in sources:
    st.markdown(f"- **{name}** — [{url}]({url})")


# ============================================
# Project Statistics
# ============================================

st.subheader("📊 Project Statistics")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Agents", "6")
col2.metric("Test Cases", "170+")
col3.metric("Phases", "12")
col4.metric("RSS Sources", "6")


# ============================================
# Footer
# ============================================

st.divider()
st.markdown(
    "<div style='text-align:center; color:#999; font-size:0.85rem;'>"
    "CyberQuill — A Multi-Agent Cybersecurity Intelligence Platform<br>"
    "Built with LangGraph • Streamlit • ChromaDB • ReportLab"
    "</div>",
    unsafe_allow_html=True,
)
