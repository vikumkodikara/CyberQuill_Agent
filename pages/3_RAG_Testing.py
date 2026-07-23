"""
CyberQuill — RAG Testing Page
================================

Interactive interface to test the Retrieval-Augmented Generation system.
Users can query the knowledge base and see retrieved context chunks.
"""

import streamlit as st

st.set_page_config(page_title="RAG Testing — CyberQuill", page_icon="📚", layout="wide")

st.title("📚 RAG Testing")
st.markdown(
    "Test the Retrieval-Augmented Generation knowledge base interactively. "
    "Enter a query to see what context the RAG system retrieves from the "
    "cybersecurity knowledge base (OWASP, NIST CSF, MITRE ATT&CK)."
)
st.divider()


# ============================================
# Knowledge Base Status
# ============================================

st.subheader("📦 Knowledge Base Status")

kb_built = False
try:
    from agents.rag import _get_collection, build_knowledge_base
    try:
        collection = _get_collection()
        doc_count = collection.count()
        kb_built = True
        st.success(f"Knowledge base loaded — **{doc_count} chunks** indexed.")
    except Exception:
        st.warning("Knowledge base not built yet.")
except ImportError as e:
    st.error(f"RAG module unavailable: {e}")
    st.stop()

if not kb_built:
    if st.button("🔨 Build Knowledge Base", type="primary"):
        with st.spinner("Building knowledge base (chunking + embedding)..."):
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

st.subheader("🔎 Query the Knowledge Base")

query = st.text_input(
    "Enter your query",
    placeholder="e.g. What is SQL injection? How does phishing work? MITRE ATT&CK lateral movement",
)

num_results = st.slider("Number of results", min_value=1, max_value=10, value=3)

if query:
    with st.spinner("Searching knowledge base..."):
        try:
            from agents.rag import retrieve_context
            context, sources = retrieve_context(query, n_results=num_results)
        except Exception as e:
            st.error(f"Retrieval failed: {e}")
            context, sources = "", []

    if context:
        st.subheader("📄 Retrieved Context")
        st.markdown(context)

        if sources:
            st.subheader("📎 Sources")
            for source in set(sources):
                st.markdown(f"- 📘 {source}")
    else:
        st.info("No relevant context found for this query.")


# ============================================
# Sample Queries
# ============================================

st.divider()
st.subheader("💡 Sample Queries")

sample_queries = [
    "What are the OWASP Top 10 vulnerabilities?",
    "Explain the NIST Cybersecurity Framework core functions",
    "What is MITRE ATT&CK technique for credential dumping?",
    "How does ransomware encryption work?",
    "What are the best practices for cloud security?",
    "Explain SQL injection attack vectors",
]

cols = st.columns(2)
for i, sq in enumerate(sample_queries):
    with cols[i % 2]:
        st.code(sq, language=None)
