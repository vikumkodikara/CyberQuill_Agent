# 🛡️ CyberQuill

**CyberQuill** is a multi-agent cybersecurity intelligence platform that collects cybersecurity news from multiple RSS feeds, removes duplicates, classifies articles, enriches content using Retrieval-Augmented Generation (RAG), generates magazine-style cybersecurity articles, reviews generated content using a reflection agent, and exports the final output as downloadable PDF magazines.

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
