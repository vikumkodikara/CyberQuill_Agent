"""
CyberQuill — Latest News Page
================================

Displays the latest cybersecurity articles collected from RSS feeds.
Users can view raw articles, filter by source, and trigger a fresh collection.
"""

import streamlit as st
from utils.theme import render_page_header

st.set_page_config(page_title="Latest News — CyberQuill", page_icon="📰", layout="wide")

render_page_header(
    title="Latest Threat Feeds",
    subtitle="Real-time cybersecurity news collected from curated security RSS feeds.",
    icon="📰"
)

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
    st.markdown("<div style='padding-top:6px; color:#64748b; font-size:0.9rem;'>⚡ Articles are cached for 5 minutes. Click <b>Refresh Feeds</b> to force a fresh fetch.</div>", unsafe_allow_html=True)


# Fetch
with st.spinner("Fetching live articles from RSS feeds..."):
    try:
        articles = _fetch_articles()
    except Exception as e:
        st.error(f"Failed to fetch articles: {e}")
        articles = []


if not articles:
    st.warning("No articles collected. RSS feeds may be temporarily unavailable.")
    st.stop()


# ============================================
# Summary Metrics
# ============================================

sources = list({a.source for a in articles})

m1, m2, m3 = st.columns(3)
m1.metric("Total Collected", len(articles))
m2.metric("Feed Sources", len(sources))
m3.metric("Latest Article", articles[0].published[:10] if articles[0].published else "Today")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# Filters
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; color:#0f172a; margin-bottom:1rem;'>🔎 Filter & Search</h4>", unsafe_allow_html=True)

f_col1, f_col2 = st.columns([1, 1])

with f_col1:
    selected_sources = st.multiselect(
        "Filter by Source Provider",
        options=sorted(sources),
        default=sorted(sources),
    )

with f_col2:
    search_query = st.text_input(
        "Search Keyword",
        placeholder="e.g. ransomware, zero-day, vulnerability, CVE...",
    )

filtered = [
    a for a in articles
    if a.source in selected_sources
    and (not search_query or search_query.lower() in a.title.lower() or (a.summary and search_query.lower() in a.summary.lower()))
]

st.caption(f"Showing **{len(filtered)}** of **{len(articles)}** articles")
st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# Article List
# ============================================

for article in filtered:
    with st.container():
        st.markdown(f"""
        <div class="article-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 0.5rem;">
                <a href="{article.link}" target="_blank" style="font-family:'Space Grotesk', sans-serif; font-size:1.2rem; font-weight:700; color:#0f172a; text-decoration:none;">
                    {article.title} ↗
                </a>
            </div>
            <div style="display:flex; gap:12px; margin-bottom:0.75rem; font-size:0.82rem; color:#64748b; align-items:center;">
                <span style="background:#f1f5f9; color:#334155; padding:2px 10px; border-radius:12px; font-weight:600;">📡 {article.source}</span>
                <span>🗓️ {article.published or 'Recent'}</span>
            </div>
            <div style="font-size:0.92rem; color:#475569; line-height:1.55;">
                {article.summary[:320] + ("..." if len(article.summary) > 320 else "") if article.summary else "No preview summary available."}
            </div>
        </div>
        """, unsafe_allow_html=True)
