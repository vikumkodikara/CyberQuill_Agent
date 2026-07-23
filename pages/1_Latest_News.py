"""
CyberQuill — Latest News Page
================================

Displays the latest cybersecurity articles collected from RSS feeds.
Users can view raw articles, filter by source, and trigger a fresh collection.
"""

import streamlit as st

st.set_page_config(page_title="Latest News — CyberQuill", page_icon="📰", layout="wide")

st.title("📰 Latest News")
st.markdown("Browse the latest cybersecurity articles collected from RSS feeds.")
st.divider()


# ============================================
# Collect Articles
# ============================================

@st.cache_data(ttl=300, show_spinner=False)
def _fetch_articles():
    """Fetches articles from RSS feeds with caching (5 min TTL)."""
    from agents.collector import collect_all_feeds
    return collect_all_feeds()


col_btn, col_info = st.columns([1, 3])

with col_btn:
    if st.button("🔄 Refresh Feeds", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col_info:
    st.caption("Articles are cached for 5 minutes. Click Refresh to fetch the latest.")


# Fetch
with st.spinner("Fetching articles from RSS feeds..."):
    try:
        articles = _fetch_articles()
    except Exception as e:
        st.error(f"Failed to fetch articles: {e}")
        articles = []


if not articles:
    st.warning("No articles collected. RSS feeds may be unavailable.")
    st.stop()


# ============================================
# Summary Metrics
# ============================================

sources = list({a.source for a in articles})

m1, m2, m3 = st.columns(3)
m1.metric("Total Articles", len(articles))
m2.metric("Sources", len(sources))
m3.metric("Latest", articles[0].published[:10] if articles[0].published else "N/A")


# ============================================
# Filters
# ============================================

st.subheader("🔎 Filter")

selected_sources = st.multiselect(
    "Filter by source",
    options=sorted(sources),
    default=sorted(sources),
)

search_query = st.text_input("Search titles", placeholder="e.g. ransomware, zero-day, CVE...")

filtered = [
    a for a in articles
    if a.source in selected_sources
    and (not search_query or search_query.lower() in a.title.lower())
]

st.caption(f"Showing {len(filtered)} of {len(articles)} articles")


# ============================================
# Article List
# ============================================

for article in filtered:
    with st.container(border=True):
        st.markdown(f"### [{article.title}]({article.link})")
        tag_col, date_col = st.columns([2, 1])
        with tag_col:
            st.caption(f"📡 {article.source}")
        with date_col:
            st.caption(f"🗓️ {article.published or 'Unknown date'}")
        if article.summary:
            st.markdown(article.summary[:300] + ("..." if len(article.summary) > 300 else ""))
