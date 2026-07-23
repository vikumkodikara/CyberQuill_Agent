"""
CyberQuill — Categories Page
===============================

Displays articles grouped by threat category after classification.
Shows classification confidence and category distribution.
"""

import streamlit as st

st.set_page_config(page_title="Categories — CyberQuill", page_icon="🏷️", layout="wide")

st.title("🏷️ Categories")
st.markdown("Articles classified by threat category using LLM and keyword analysis.")
st.divider()


# ============================================
# Pipeline: Collect → Deduplicate → Classify
# ============================================

@st.cache_data(ttl=300, show_spinner=False)
def _get_classified_articles():
    """Runs collection, deduplication, and classification."""
    from agents.collector import collect_all_feeds
    from agents.duplicate import remove_duplicates
    from agents.classifier import classify_articles

    articles = collect_all_feeds()
    unique = remove_duplicates(articles)
    classified = classify_articles(unique)
    return classified


with st.spinner("Collecting, deduplicating, and classifying articles..."):
    try:
        classified = _get_classified_articles()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        classified = []

if st.button("🔄 Re-classify", use_container_width=False):
    st.cache_data.clear()
    st.rerun()

if not classified:
    st.warning("No classified articles available.")
    st.stop()


# ============================================
# Category Distribution
# ============================================

st.subheader("📊 Category Distribution")

categories: dict[str, int] = {}
for article in classified:
    categories[article.category] = categories.get(article.category, 0) + 1

# Bar chart
import pandas as pd
df = pd.DataFrame(
    sorted(categories.items(), key=lambda x: x[1], reverse=True),
    columns=["Category", "Count"],
)
st.bar_chart(df, x="Category", y="Count", color="#42a5f5")

# Metrics row
cols = st.columns(min(len(categories), 4))
for i, (cat, count) in enumerate(sorted(categories.items(), key=lambda x: x[1], reverse=True)):
    with cols[i % len(cols)]:
        st.metric(cat, count)


# ============================================
# Category Filter & Articles
# ============================================

st.subheader("📰 Articles by Category")

selected_cat = st.selectbox(
    "Select category",
    options=["All"] + sorted(categories.keys()),
)

if selected_cat == "All":
    display_articles = classified
else:
    display_articles = [a for a in classified if a.category == selected_cat]

st.caption(f"Showing {len(display_articles)} articles")

for article in display_articles:
    with st.container(border=True):
        col_title, col_badge = st.columns([4, 1])
        with col_title:
            st.markdown(f"### [{article.title}]({article.link})")
        with col_badge:
            st.markdown(
                f"<span style='background:#e3f2fd;color:#1565c0;padding:4px 12px;"
                f"border-radius:20px;font-size:0.8rem;font-weight:600'>"
                f"{article.category}</span>",
                unsafe_allow_html=True,
            )

        meta_col, conf_col = st.columns([3, 1])
        with meta_col:
            st.caption(f"📡 {article.source}  •  🗓️ {article.published or 'Unknown'}")
        with conf_col:
            confidence_pct = int(article.confidence * 100)
            st.caption(f"🎯 Confidence: {confidence_pct}%")

        if article.summary:
            st.markdown(article.summary[:250] + ("..." if len(article.summary) > 250 else ""))
