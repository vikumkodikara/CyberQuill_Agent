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

# Custom High-Tech Dark Cybersecurity Distribution Graph (HTML/CSS)
total_articles = sum(categories.values()) or 1

bar_rows_html = []
for cat, count in sorted_cats:
    color = get_category_left_border(cat)
    pct = round((count / total_articles) * 100, 1)
    bar_width = max(pct, 4)  # min 4% width for visibility

    # Category icon mapping
    cat_lower = cat.lower()
    if "malware" in cat_lower or "ransomware" in cat_lower:
        icon = "🐛"
    elif "breach" in cat_lower or "leak" in cat_lower:
        icon = "🔓"
    elif "phish" in cat_lower or "social" in cat_lower:
        icon = "🎣"
    elif "ai" in cat_lower or "llm" in cat_lower:
        icon = "🤖"
    elif "vuln" in cat_lower or "cve" in cat_lower:
        icon = "⚠️"
    elif "zero-day" in cat_lower or "zero day" in cat_lower:
        icon = "⚡"
    elif "cloud" in cat_lower:
        icon = "☁️"
    elif "intel" in cat_lower or "threat" in cat_lower:
        icon = "🔍"
    else:
        icon = "🏷️"

    pct_label = f"{int(pct)}%" if pct >= 7 else ""

    bar_rows_html.append(f"""
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 14px;">
        <div style="width: 200px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #E2E8F0; font-weight: 600; display: flex; align-items: center; gap: 8px; flex-shrink: 0;">
            <span style="font-size: 14px;">{icon}</span>
            <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{cat}</span>
        </div>
        <div style="flex-grow: 1; background: #0A0E1A; border: 1px solid #1F2937; border-radius: 6px; height: 28px; padding: 2px; position: relative; overflow: hidden;">
            <div style="width: {bar_width}%; background: linear-gradient(90deg, {color}99, {color}); height: 100%; border-radius: 4px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; box-shadow: 0 0 10px {color}33;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #0A0E1A;">{pct_label}</span>
            </div>
        </div>
        <div style="width: 110px; text-align: right; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; color: {color}; flex-shrink: 0;">
            {count} <span style="font-size: 11px; color: #64748B; font-weight: 400;">({pct}%)</span>
        </div>
    </div>
    """)

st.markdown(f"""
<div style="background: #111827; border: 1px solid #1F2937; border-radius: 10px; padding: 22px 24px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #1F2937; padding-bottom: 12px;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; color: #00D4FF; letter-spacing: 0.1em; text-transform: uppercase; display: flex; align-items: center; gap: 8px;">
            <span>📊</span> THREAT CATEGORY DISTRIBUTION GRAPH
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748B;">
            {len(categories)} CATEGORIES &bull; {total_articles} ARTICLES
        </div>
    </div>
    {"".join(bar_rows_html)}
</div>
""", unsafe_allow_html=True)

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
