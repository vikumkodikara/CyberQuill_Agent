# 🛡️ CyberQuill

**CyberQuill** is a multi-agent cybersecurity intelligence platform that collects cybersecurity news from multiple RSS feeds, removes duplicates, classifies articles, enriches content using Retrieval-Augmented Generation (RAG), generates magazine-style cybersecurity articles, reviews generated content using a reflection agent, and exports the final output as downloadable PDF magazines.

**Live Streamlit Demo:** [CyberQuill Live Demo (Local Deployment)](#) *(Note: Replace `#` with your actual deployment URL if hosted online)*

## 🏗️ Architecture

```
Collector → Duplicate → Classifier → RAG → Writer → Reviewer → PDF
```

CyberQuill uses a **sequential pipeline** of 6 AI agents orchestrated by [LangGraph](https://github.com/langchain-ai/langgraph):

| Agent | Role |
|-------|------|
| **Collector** | Fetches cybersecurity news from RSS feeds |
| **Duplicate** | Removes duplicate articles using URL and title matching |
| **Classifier** | Categorizes articles (Malware, Data Breach, Zero-Day, etc.) |
| **RAG** | Enriches articles with context from a cybersecurity knowledge base |
| **Writer** | Generates magazine-style articles with full analysis |
| **Reviewer** | Reviews, critiques, and approves articles for publication |

## Quick Start

### Prerequisites

- Python 3.13+
- [Groq API Key](https://console.groq.com/keys)
- [OpenRouter API Key](https://openrouter.ai/keys)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/vikumkodikara/CyberQuill_Agent.git
cd CyberQuill_Agent

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env
# Edit .env with your API keys

# 5. Run the Streamlit app
streamlit run streamlit_app.py
```

## 📁 Project Structure

```
CyberQuill/
├── config/          # Configuration and prompt templates
├── models/          # Pydantic data models
├── agents/          # AI agent implementations
├── orchestrator/    # LangGraph pipeline
├── pdf/             # PDF generation
├── data/            # Knowledge base & output
├── utils/           # Logging and helpers
├── pages/           # Streamlit pages
├── tests/           # Unit tests
├── streamlit_app.py # App entry point
└── requirements.txt # Dependencies
```

## 🤖 AI Design Patterns

| Pattern | Implementation |
|---------|---------------|
| **Tool Use** | Collector (feedparser), RAG (ChromaDB) |
| **Router** | Orchestrator routes data between agents |
| **Planning** | Pipeline decomposes magazine generation into stages |
| **Reflection** | Reviewer self-critiques its own review |
| **Orchestrator-Worker** | LangGraph coordinates all agents |

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📰 RSS Sources

- The Hacker News
- Bleeping Computer
- Krebs on Security
- SecurityWeek
- Dark Reading
- CISA

## 🛠️ Technology Stack

### Model-Choice Comparison

| Provider | Model | Role | Rationale |
|----------|-------|------|-----------|
| **Groq** | `llama-3.3-70b-versatile` | Classifier, Writer, Reviewer | Blazing-fast inference speeds necessary for processing multiple articles per issue without timeouts. High instruction-following capability for structured JSON output and drafting. |
| **OpenRouter** | `meta-llama/llama-4-maverick` | Fallback / Complex Reasoning | Specialized model configured for tackling complex reasoning tasks and deeply nuanced cybersecurity topics when standard fast models fall short. |

### Technologies

- **Framework**: Streamlit, LangGraph
- **LLM Providers**: Groq, OpenRouter
- **Vector Store**: ChromaDB
- **Embeddings**: Sentence Transformers
- **PDF**: ReportLab
- **Language**: Python 3.13+

## 📄 License

This project is for academic purposes.

## 👤 Author

Vikum Kodikara

## ⚠️ Known Limitations

- **Processing Time**: The pipeline can take several minutes to run entirely depending on the number of articles collected and API rate limits.
- **Dependency on RSS Feeds**: If the source feeds go down or change their XML structure, the collector may fail to parse new articles.
- **API Rate Limits**: Aggressive fetching and writing can hit rate limits on free tiers of Groq or OpenRouter.
- **RAG Context Size**: The context window limits how much of the framework PDF content can be injected at once, occasionally resulting in truncated references.
