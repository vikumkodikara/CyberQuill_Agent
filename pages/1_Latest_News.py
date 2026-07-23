"""
CyberQuill — Latest News Page
================================

Displays the latest cybersecurity articles collected from RSS feeds.
Users can view raw articles, filter by source, and trigger a fresh collection.
"""

import streamlit as st
from utils.theme import render_page_header, render_sidebar_controls, get_category_left_border
from utils.helpers import format_date_magazine

st.set_page_config(page_title="News Feed — CyberQuill", page_icon="📰", layout="wide")

render_sidebar_controls()

render_page_header(
    title="News Feed",
    subtitle="Real-time cybersecurity news collected from curated security publications and intelligence sources.",
    icon="📰"
)

# LIVE badge
st.markdown("""
<div style="margin-top: -20px; margin-bottom: 20px;">
    <span class="live-badge"><span class="pulse-dot"></span> LIVE</span>
</div>
""", unsafe_allow_html=True)

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
    st.markdown('<div style="padding-top:6px; color:#64748B; font-size:0.85rem; font-family: JetBrains Mono, monospace;">⚡ Articles cached for 5 min. Click <b style="color:#00D4FF">Refresh Feeds</b> to force a fresh fetch.</div>', unsafe_allow_html=True)


# Fetch
with st.spinner("Fetching live articles..."):
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
m2.metric("Sources Active", len(sources))
m3.metric("Latest Article", format_date_magazine(articles[0].published) if articles[0].published else "Today")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# Filters
# ============================================

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">
    // FILTER & SEARCH
</div>
""", unsafe_allow_html=True)

f_col1, f_col2 = st.columns([1, 1])

with f_col1:
    selected_sources = st.multiselect(
        "Filter by Source",
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

# Assign a left-border color per source for visual grouping
source_colors = {}
color_palette = ["#00D4FF", "#7C3AED", "#FF3366", "#34D399", "#FCD34D", "#FF6B00", "#A78BFA", "#F87171"]
for i, src in enumerate(sorted(sources)):
    source_colors[src] = color_palette[i % len(color_palette)]

for article in filtered:
    with st.container():
        pub_date = format_date_magazine(article.published) if article.published else "Recent"
        summary_text = article.summary[:320] + ("..." if len(article.summary) > 320 else "") if article.summary else "No preview summary available."
        border_color = source_colors.get(article.source, "#1F2937")

        st.markdown(f"""
        <div style="background: #111827; border: 1px solid #1F2937; border-left: 3px solid {border_color}; border-radius: 0 8px 8px 0; padding: 18px 20px; margin-bottom: 10px; transition: border-color 0.2s;">
            <div style="margin-bottom: 8px;">
                <a href="{article.link}" target="_blank" style="font-size: 15px; font-weight: 600; color: #F1F5F9; text-decoration: none; line-height: 1.4;">
                    {article.title} ↗
                </a>
            </div>
            <div style="display: flex; gap: 16px; margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px;">
                <span style="color: {border_color};">📡 {article.source}</span>
                <span style="color: #64748B;">🗓️ {pub_date}</span>
            </div>
            <div style="font-size: 13px; color: #94A3B8; line-height: 1.6;">
                {summary_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
