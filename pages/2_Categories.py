"""
CyberQuill — Categories Page
===============================

Displays articles grouped by threat category after classification.
Shows classification confidence and category distribution.
Supports Magazine/Debug modes with softer language in Magazine mode.
"""

import streamlit as st
import pandas as pd
from utils.theme import render_page_header, get_category_badge_html, render_sidebar_controls
from utils.helpers import is_magazine_mode

st.set_page_config(page_title="Topics — CyberQuill", page_icon="🏷️", layout="wide")

render_sidebar_controls()

render_page_header(
    title="Topics & Categories",
    subtitle="Articles organized by cybersecurity topic — browse malware analysis, data breaches, AI security, cloud threats, and more.",
    icon="🏷️"
)

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


with st.spinner("Analyzing and categorizing articles..."):
    try:
        classified = _get_classified_articles()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        classified = []

col_act, col_spacer = st.columns([1, 4])
with col_act:
    if st.button("🔄 Re-classify", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if not classified:
    st.warning("No classified articles available.")
    st.stop()


# ============================================
# Category Distribution
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-top:1.5rem; margin-bottom:1rem;'>📊 Category Breakdown</h4>", unsafe_allow_html=True)

categories: dict[str, int] = {}
for article in classified:
    categories[article.category] = categories.get(article.category, 0) + 1

# Metrics grid
cols = st.columns(min(len(categories), 4))
for i, (cat, count) in enumerate(sorted(categories.items(), key=lambda x: x[1], reverse=True)):
    with cols[i % len(cols)]:
        st.metric(cat, f"{count} Articles")

st.markdown("<br>", unsafe_allow_html=True)

# Bar chart
df = pd.DataFrame(
    sorted(categories.items(), key=lambda x: x[1], reverse=True),
    columns=["Category", "Article Count"],
)
st.bar_chart(df, x="Category", y="Article Count", color="#6366f1")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# Category Filter & Articles
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-bottom:1rem;'>📰 Articles by Category</h4>", unsafe_allow_html=True)

selected_cat = st.selectbox(
    "Filter by Category",
    options=["All Categories"] + sorted(categories.keys()),
)

if selected_cat == "All Categories":
    display_articles = classified
else:
    display_articles = [a for a in classified if a.category == selected_cat]

st.caption(f"Displaying **{len(display_articles)}** articles")
st.markdown("<br>", unsafe_allow_html=True)

for article in display_articles:
    badge_html = get_category_badge_html(article.category)

    if magazine_mode:
        # Softer language: "Relevance" instead of "AI Confidence"
        conf_pct = int(article.confidence * 100)
        confidence_label = f"Relevance: {conf_pct}%"
    else:
        conf_pct = int(article.confidence * 100)
        confidence_label = f"AI Confidence: {conf_pct}%"

    st.markdown(f"""
    <div class="article-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 0.6rem;">
            <a href="{article.link}" target="_blank" style="font-family:'Space Grotesk', sans-serif; font-size:1.2rem; font-weight:700; color:#0f172a; text-decoration:none;">
                {article.title} ↗
            </a>
            {badge_html}
        </div>
        <div style="display:flex; gap:16px; margin-bottom:0.75rem; font-size:0.82rem; color:#64748b; align-items:center;">
            <span>📡 <b>Source:</b> {article.source}</span>
            <span>🗓️ <b>Published:</b> {article.published or 'Recent'}</span>
            <span style="color:#4f46e5; font-weight:700;">🎯 <b>{confidence_label}</b></span>
        </div>
        <div style="font-size:0.92rem; color:#475569; line-height:1.55;">
            {article.summary[:300] + ("..." if len(article.summary) > 300 else "") if article.summary else "No preview summary available."}
        </div>
    </div>
    """, unsafe_allow_html=True)
