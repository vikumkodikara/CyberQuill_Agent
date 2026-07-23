"""
CyberQuill — RAG Testing Page
================================

Interactive interface to test the Retrieval-Augmented Generation system.
Users can query the knowledge base and see retrieved context chunks.
"""

import streamlit as st
from utils.theme import render_page_header

st.set_page_config(page_title="RAG Testing — CyberQuill", page_icon="📚", layout="wide")

render_page_header(
    title="RAG Vector Search Playground",
    subtitle="Query the ChromaDB vector database index containing OWASP Top 10, NIST CSF 2.0, and MITRE ATT&CK security frameworks.",
    icon="📚"
)

# ============================================
# Knowledge Base Status
# ============================================

kb_built = False
try:
    from agents.rag import _get_collection, build_knowledge_base
    try:
        collection = _get_collection()
        doc_count = collection.count()
        kb_built = True
        st.markdown(f"""
        <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:12px; padding:1rem 1.25rem; display:flex; align-items:center; gap:12px; margin-bottom:1.5rem;">
            <div style="font-size:1.5rem;">✅</div>
            <div>
                <div style="font-weight:700; color:#15803d; font-size:1rem;">Knowledge Base Active</div>
                <div style="color:#166534; font-size:0.88rem;">ChromaDB collection loaded with <b>{doc_count} security framework chunks</b> indexed.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.warning("Knowledge base not initialized yet.")
except ImportError as e:
    st.error(f"RAG module unavailable: {e}")
    st.stop()

if not kb_built:
    if st.button("🔨 Build Knowledge Base Now", type="primary"):
        with st.spinner("Building vector knowledge base (chunking + embedding)..."):
            try:
                build_knowledge_base()
                st.success("Knowledge base built successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to build knowledge base: {e}")
    st.stop()

# ============================================
# Query Interface
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; color:#0f172a; margin-bottom:1rem;'>🔎 Execute RAG Search</h4>", unsafe_allow_html=True)

# Sample query handler
if "selected_sample" in st.session_state:
    default_query = st.session_state["selected_sample"]
else:
    default_query = ""

col_q, col_k = st.columns([3, 1])

with col_q:
    query = st.text_input(
        "Enter natural language query",
        value=default_query,
        placeholder="e.g. What is SQL injection? How does ransomware work? MITRE ATT&CK credential dumping...",
    )

with col_k:
    num_results = st.slider("Top Chunks (k)", min_value=1, max_value=8, value=3)

if query:
    with st.spinner("Searching vector embeddings..."):
        try:
            from agents.rag import retrieve_context
            context, sources = retrieve_context(query, top_k=num_results)
        except Exception as e:
            st.error(f"Retrieval failed: {e}")
            context, sources = "", []

    if context:
        st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; color:#0f172a; margin-top:1.5rem; margin-bottom:1rem;'>📄 Retrieved Context Chunks</h4>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background:#0f172a; color:#e2e8f0; border-radius:14px; padding:1.5rem; font-family:'Plus Jakarta Sans', monospace; line-height:1.65; border:1px solid #334155; box-shadow:0 10px 25px -5px rgba(15,23,42,0.3);">
            <div style="font-size:0.75rem; font-weight:700; color:#38bdf8; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:1rem; border-bottom:1px solid #1e293b; padding-bottom:0.5rem;">
                RETRIEVED VECTOR EMBEDDING CONTEXT ({num_results} MATCHES)
            </div>
            {context.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

        if sources:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h5 style='font-weight:700; color:#0f172a;'>📎 Cited Framework Sources</h5>", unsafe_allow_html=True)
            s_html = "".join([f'<span style="background:#e0f2fe; color:#0369a1; border:1px solid #7dd3fc; padding:6px 14px; border-radius:20px; font-weight:600; font-size:0.85rem; display:inline-block; margin-right:8px; margin-bottom:8px;">📘 {s}</span>' for s in set(sources)])
            st.markdown(f"<div>{s_html}</div>", unsafe_allow_html=True)
    else:
        st.info("No relevant context found for this query.")

st.markdown("<br><hr>", unsafe_allow_html=True)

# ============================================
# Sample Queries
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; color:#0f172a; margin-bottom:1rem;'>💡 Click Sample Queries to Test</h4>", unsafe_allow_html=True)

sample_queries = [
    "What are the OWASP Top 10 vulnerabilities?",
    "Explain the NIST Cybersecurity Framework core functions",
    "What is MITRE ATT&CK technique for credential dumping?",
    "How does ransomware encryption work?",
    "What are the best practices for cloud security?",
    "Explain SQL injection attack vectors",
]

sq_cols = st.columns(2)
for i, sq in enumerate(sample_queries):
    with sq_cols[i % 2]:
        if st.button(f"🔍 {sq}", key=f"sq_{i}", use_container_width=True):
            st.session_state["selected_sample"] = sq
            st.rerun()
