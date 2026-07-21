# CyberQuill — Project Review & Implementation Plan

> **Last Updated:** 2026-07-21  
> **Current Phase:** Phase 1 — Repository Setup (NOT YET STARTED — awaiting approval)  
> **Status:** Planning complete. Awaiting user approval to begin Phase 1.

---

## 1. Project Review Summary

CyberQuill is a **multi-agent cybersecurity intelligence platform** that:
1. Collects news from RSS feeds
2. Removes duplicates
3. Classifies articles by threat category
4. Enriches content via RAG (Retrieval-Augmented Generation)
5. Generates magazine-style articles
6. Reviews content with a reflection agent
7. Exports a downloadable PDF magazine

The architecture follows a **sequential pipeline** of 6 agents communicating via structured JSON.

---

## 2. Proposed Improvements Over the Original Specification

### 2.1 Architecture Improvements

| Area | Original Spec | Proposed Improvement | Reason |
|------|--------------|---------------------|--------|
| **Config Management** | Hardcoded values | Centralized `config/settings.py` using `pydantic-settings` | API keys, model names, and URLs should never be hardcoded. Makes deployment easier and keeps secrets safe. |
| **Logging** | "Agent Logs" page only | Structured logging with Python `logging` module + log file rotation | Proper logging is essential for debugging in production. The Streamlit page will *read* these logs. |
| **Error Handling** | Not specified | Per-agent error handling with retry logic and graceful degradation | RSS feeds go down. APIs rate-limit. The system must not crash. |
| **State Management** | Not specified | LangGraph `StateGraph` with typed state dict | LangGraph is the preferred framework — state management is its core strength. |
| **Caching** | Not specified | Cache RSS fetches and LLM responses to reduce API costs | During development you'll call the same feeds/prompts repeatedly. Caching saves money and time. |
| **Data Validation** | "Return JSON" | Pydantic models for all data schemas | Catches malformed data early. Makes the code self-documenting. Viva-friendly. |

### 2.2 Structural Improvements

| Area | Original Spec | Proposed Improvement | Reason |
|------|--------------|---------------------|--------|
| **Project Name in Structure** | `CyberIntel-Agent/` | `CyberQuill/` (match your actual project name) | Consistency. |
| **Config directory** | Not present | Add `config/` with `settings.py` and `prompts.py` | Separates configuration from logic. |
| **Orchestrator** | Not present | Add `orchestrator/pipeline.py` | The LangGraph pipeline definition deserves its own module. |
| **Models/Schemas** | Not present | Add `models/schemas.py` | Pydantic data models used across all agents. |
| **Utils** | Not present | Add `utils/logger.py` and `utils/helpers.py` | Shared utilities reduce code duplication. |
| **UI structure** | Single `ui/pages.py` | Streamlit multi-page app with `pages/` directory | Streamlit's native multi-page app pattern is cleaner and more maintainable. |

### 2.3 Agent-Level Improvements

| Agent | Improvement | Reason |
|-------|------------|--------|
| **Collector** | Add `published` date parsing with `dateutil`, add timeout handling, add source health checks | RSS feeds have inconsistent date formats. Feeds can hang. |
| **Duplicate** | Use fuzzy matching (cosine similarity on titles) in addition to exact URL matching | "Same story, different headline" is common across sources. |
| **Classifier** | Return confidence scores alongside categories, support multi-label classification | An article about a zero-day malware data breach spans multiple categories. |
| **RAG** | Add metadata filtering, implement a retrieval quality scorer | Not all retrieved chunks are relevant. Quality scoring improves output. |
| **Writer** | Add structured output parsing with Pydantic | Ensures the LLM returns all required sections (Title, Summary, Analysis, etc.). |
| **Reviewer** | Implement iterative feedback loop (max 2 revision cycles) | A single pass may miss issues. But infinite loops waste API credits. |

---

## 3. Proposed Repository Structure

```
CyberQuill/
│
├── config/
│   ├── __init__.py
│   ├── settings.py          # Environment variables, API keys, model configs
│   └── prompts.py           # All LLM prompt templates (centralized)
│
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic data models (Article, ClassifiedArticle, etc.)
│
├── agents/
│   ├── __init__.py
│   ├── collector.py          # RSS feed collection
│   ├── duplicate.py          # Duplicate detection & removal
│   ├── classifier.py         # Article classification
│   ├── rag.py                # RAG retrieval & enrichment
│   ├── writer.py             # Magazine article generation
│   └── reviewer.py           # Content review & reflection
│
├── orchestrator/
│   ├── __init__.py
│   └── pipeline.py           # LangGraph StateGraph pipeline definition
│
├── pdf/
│   ├── __init__.py
│   └── generator.py          # ReportLab PDF generation
│
├── data/
│   ├── documents/            # RAG knowledge base documents
│   └── output/               # Generated news.json, PDFs
│
├── utils/
│   ├── __init__.py
│   ├── logger.py             # Structured logging setup
│   └── helpers.py            # Shared utility functions
│
├── pages/                    # Streamlit multi-page app
│   ├── 1_Latest_News.py
│   ├── 2_Categories.py
│   ├── 3_RAG_Testing.py
│   ├── 4_Generate_Magazine.py
│   ├── 5_Agent_Logs.py
│   └── 6_About.py
│
├── tests/
│   ├── __init__.py
│   ├── test_collector.py
│   ├── test_duplicate.py
│   ├── test_classifier.py
│   ├── test_rag.py
│   ├── test_writer.py
│   ├── test_reviewer.py
│   └── test_pdf.py
│
├── streamlit_app.py          # Streamlit entry point (Home page)
├── requirements.txt          # Python dependencies
├── .env.example              # Template for environment variables
├── .gitignore                # Git ignore rules
└── README.md                 # Project documentation
```

### Why this structure?

- **`config/`** — Centralizes all configuration. During your viva, you can point to one place and say "all settings live here."
- **`models/`** — Pydantic schemas are shared across agents. Placing them in their own module avoids circular imports.
- **`orchestrator/`** — The LangGraph pipeline is the "brain" of the system. It deserves its own module separate from the agents it orchestrates.
- **`pages/`** — Streamlit's native multi-page app pattern. Each file in `pages/` automatically becomes a sidebar navigation item.
- **`utils/`** — Shared code (logging, helpers) lives here. Avoids duplication across agents.
- **`tests/`** — One test file per agent. Easy to run individually or all at once.

---

## 4. Development Phases

### Phase 1: Repository Setup
- `.gitignore`, `requirements.txt`, `.env.example`
- `config/settings.py` — Load environment variables using `pydantic-settings`
- `config/prompts.py` — Empty template for future LLM prompts
- `models/schemas.py` — Core Pydantic data models (`Article`, `ClassifiedArticle`, `MagazineArticle`)
- `utils/logger.py` — Structured logging configuration
- `README.md` — Project overview and setup instructions
- All `__init__.py` files and empty placeholder files

### Phase 2: Collector Agent
- Fetch RSS feeds using `feedparser`
- Normalize article format
- Return standardized JSON (`Article` schema)

### Phase 3: Duplicate Agent
- Remove duplicate articles
- Compare titles (fuzzy) and URLs (exact)

### Phase 4: Classification Agent
- Classify articles into categories using LLM
- Categories: Malware, Data Breach, AI Security, Cloud Security, Zero-Day, Threat Intelligence, Vulnerability Management

### Phase 5: RAG Agent
- Set up ChromaDB vector store
- Chunk and embed knowledge base documents
- Retrieve relevant context for article enrichment

### Phase 6: Writer Agent
- Generate magazine-style articles using LLM
- Sections: Title, Executive Summary, Background, Technical Analysis, Impact, Recommendations, References

### Phase 7: Reviewer Agent
- Grammar and consistency review
- Reflection/self-critique pattern
- Publication approval with iterative feedback

### Phase 8: PDF Generator
- ReportLab PDF generation
- Magazine layout with cover, articles, references

### Phase 9: LangGraph Orchestrator
- Wire all agents into a LangGraph StateGraph pipeline

### Phase 10: Streamlit UI
- Multi-page Streamlit app with all 7 pages

### Phase 11: Deployment
- Streamlit Community Cloud deployment

### Phase 12: Documentation
- Final README, architecture diagrams, viva preparation notes

---

## 5. Agentic AI Design Patterns to Implement

| Pattern | Where Implemented | Description |
|---------|-------------------|-------------|
| **Tool Use** | Collector (feedparser), RAG (ChromaDB) | Agents use external tools to fetch data or query databases |
| **Router Pattern** | Orchestrator | Routes articles to appropriate agents based on pipeline stage |
| **Planning/Task Decomposition** | Orchestrator | Breaks the magazine generation task into sub-tasks for each agent |
| **Reflection/Self-Critique** | Reviewer Agent | Agent reviews its own output and iterates to improve quality |
| **Orchestrator-Worker** | Pipeline | Central orchestrator delegates work to specialized worker agents |

---

## 6. Model Strategy

| Model | Provider | Used For | Why |
|-------|----------|----------|-----|
| Fast model (e.g., Llama 3) | Groq | Classification, Routing | Low latency, free tier, good for simple tasks |
| Strong model (e.g., Claude/GPT) | OpenRouter | Writing, Review | Better reasoning, longer context, higher quality output |

---

## 7. RSS Sources

```
https://feeds.feedburner.com/TheHackersNews
https://www.bleepingcomputer.com/feed/
https://krebsonsecurity.com/feed/
https://www.securityweek.com/feed/
https://www.darkreading.com/rss.xml
https://www.cisa.gov/news.xml
```

---

## 8. Open Questions

1. **Python environment manager** — Are you using `venv`, `conda`, or `poetry`?
2. **API keys** — Do you already have API keys for OpenRouter and Groq?
3. **Colab notebook** — Can you share the Google Colab prototype for reference?
4. **LangGraph version** — Are you using `langgraph>=0.2`?
5. **Deployment** — Streamlit Community Cloud has no persistent filesystem. ChromaDB vectors will reset. Need a strategy for this.
