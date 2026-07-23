"""
CyberQuill — RAG Testing Page
===================================================

Interactive interface to test the Retrieval-Augmented Generation system.
Users can query the knowledge base and see retrieved context chunks.
"""

import streamlit as st
from utils.theme import render_page_header, render_sidebar_controls

st.set_page_config(page_title="RAG Testing — CyberQuill", page_icon="📚", layout="wide")

render_sidebar_controls()

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
        <div style="background: #111827; border: 1px solid #1F2937; border-left: 3px solid #00FF88; border-radius: 0 8px 8px 0; padding: 14px 18px; display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;">
            <span class="pulse-dot"></span>
            <div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; color: #00FF88; text-transform: uppercase; letter-spacing: 0.08em;">KNOWLEDGE BASE ACTIVE</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748B; margin-top: 2px;">{doc_count} security framework chunks indexed</div>
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

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">
    // EXECUTE RAG SEARCH
</div>
""", unsafe_allow_html=True)

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
        placeholder="e.g. What is SQL injection? How does ransomware work?",
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
        from utils.content_sanitizer import sanitize_rag_context_chunks, strip_source_filenames

        clean_chunks = sanitize_rag_context_chunks(context)
        if clean_chunks:
            st.markdown("""
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin: 1.5rem 0 1rem;">
                // RETRIEVED INTELLIGENCE CONTEXT
            </div>
            """, unsafe_allow_html=True)

            for idx, chunk in enumerate(clean_chunks, 1):
                chunk_escaped = chunk.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                st.markdown(f"""
                <div class="rag-chunk" style="background: #111827; border-left: 3px solid #00D4FF; border-radius: 0 8px 8px 0; padding: 16px 20px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #1F2937;">
                        <span>MATCH #{idx}</span>
                        <span style="background: #00D4FF15; color: #00D4FF; padding: 2px 8px; border-radius: 4px; font-size: 10px;">VERIFIED</span>
                    </div>
                    <div style="font-size: 14px; color: #CBD5E1; line-height: 1.7;">
                        {chunk_escaped}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if sources:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #7C3AED; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
                // CITED FRAMEWORK SOURCES
            </div>
            """, unsafe_allow_html=True)
            clean_sources = [strip_source_filenames(s) for s in sources]
            s_html = "".join([f'<span style="background: #7C3AED15; color: #A78BFA; border: 1px solid #7C3AED33; padding: 4px 12px; border-radius: 4px; font-family: JetBrains Mono, monospace; font-weight: 600; font-size: 11px; display: inline-block; margin-right: 8px; margin-bottom: 8px;">📘 {s}</span>' for s in set(clean_sources) if s])
            st.markdown(f"<div>{s_html}</div>", unsafe_allow_html=True)
    else:
        st.info("No relevant context found for this query.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="border-top: 1px solid #1F2937; margin: 0.5rem 0 1.5rem;"></div>', unsafe_allow_html=True)

# ============================================
# Sample Queries
# ============================================

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">
    // SAMPLE QUERIES
</div>
""", unsafe_allow_html=True)

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
