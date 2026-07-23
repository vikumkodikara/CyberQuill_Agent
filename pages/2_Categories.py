"""
CyberQuill — Categories Page
===============================

Displays articles grouped by threat category after classification.
Shows classification confidence and category distribution.
"""

import streamlit as st
import pandas as pd
from utils.theme import render_page_header, get_category_badge_html, render_sidebar_controls, get_category_left_border

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

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin: 1.5rem 0 1rem;">
    // CATEGORY BREAKDOWN
</div>
""", unsafe_allow_html=True)

categories: dict[str, int] = {}
for article in classified:
    categories[article.category] = categories.get(article.category, 0) + 1

# Category stat cards with colored left-border
sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
cols = st.columns(min(len(categories), 4))
for i, (cat, count) in enumerate(sorted_cats):
    border_color = get_category_left_border(cat)
    with cols[i % len(cols)]:
        st.markdown(f"""
        <div style="background: #111827; border: 1px solid #1F2937; border-left: 3px solid {border_color}; border-radius: 0 8px 8px 0; padding: 16px 18px; margin-bottom: 8px;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px;">{cat}</div>
            <div style="font-size: 24px; font-weight: 700; color: {border_color}; font-family: 'JetBrains Mono', monospace;">{count} <span style="font-size: 13px; color: #64748B; font-weight: 400;">articles</span></div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Bar chart
df = pd.DataFrame(
    sorted_cats,
    columns=["Category", "Article Count"],
)
st.bar_chart(df, x="Category", y="Article Count", color="#00D4FF")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# Category Filter & Articles
# ============================================

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">
    // ARTICLES BY CATEGORY
</div>
""", unsafe_allow_html=True)

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
    border_color = get_category_left_border(article.category)

    conf_pct = int(article.confidence * 100)
    confidence_label = f"Relevance: {conf_pct}%"

    st.markdown(f"""
    <div style="background: #111827; border: 1px solid #1F2937; border-left: 3px solid {border_color}; border-radius: 0 8px 8px 0; padding: 18px 20px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <a href="{article.link}" target="_blank" style="font-size: 15px; font-weight: 600; color: #F1F5F9; text-decoration: none; line-height: 1.4;">
                {article.title} ↗
            </a>
            {badge_html}
        </div>
        <div style="display: flex; gap: 16px; margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px;">
            <span style="color: #00D4FF;">📡 {article.source}</span>
            <span style="color: #64748B;">🗓️ {article.published or 'Recent'}</span>
            <span style="color: {border_color};">🎯 {confidence_label}</span>
        </div>
        <div style="font-size: 13px; color: #94A3B8; line-height: 1.6;">
            {article.summary[:300] + ("..." if len(article.summary) > 300 else "") if article.summary else "No preview summary available."}
        </div>
    </div>
    """, unsafe_allow_html=True)
