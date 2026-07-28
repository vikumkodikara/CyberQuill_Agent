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

CLASSIFICATION_CACHE_VERSION = 3


@st.cache_data(ttl=300, show_spinner=False)
def _get_classified_articles(_cache_version: int = CLASSIFICATION_CACHE_VERSION):
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

if not classified:
    st.warning("No classified articles available.")
    st.stop()

# ============================================
# Uncategorized Warning
# ============================================

uncategorized_count = sum(1 for a in classified if a.category == "Uncategorized")
uncategorized_rate = (uncategorized_count / len(classified)) * 100 if classified else 0

if uncategorized_count > 0 and uncategorized_rate > 5:
    st.warning(
        f"**{uncategorized_count} articles ({uncategorized_rate:.1f}%)** remain uncategorized after auto-classification."
    )
elif uncategorized_count > 0:
    st.info(
        f"{uncategorized_count} article(s) ({uncategorized_rate:.1f}%) remain Uncategorized — within acceptable range."
    )


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
        card_html = (
            f'<div style="background: #111827; border: 1px solid #1F2937; border-left: 3px solid {border_color}; border-radius: 0 8px 8px 0; padding: 16px 18px; margin-bottom: 8px;">'
            f'<div style="font-family: \'JetBrains Mono\', monospace; font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px;">{cat}</div>'
            f'<div style="font-size: 24px; font-weight: 700; color: {border_color}; font-family: \'JetBrains Mono\', monospace;">{count} <span style="font-size: 13px; color: #64748B; font-weight: 400;">articles</span></div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

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

    row_html = (
        f'<div style="display: flex; align-items: center; gap: 16px; margin-bottom: 14px;">'
        f'<div style="width: 200px; font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: #E2E8F0; font-weight: 600; display: flex; align-items: center; gap: 8px; flex-shrink: 0;">'
        f'<span style="font-size: 14px;">{icon}</span>'
        f'<span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{cat}</span>'
        f'</div>'
        f'<div style="flex-grow: 1; background: #0A0E1A; border: 1px solid #1F2937; border-radius: 6px; height: 28px; padding: 2px; position: relative; overflow: hidden;">'
        f'<div style="width: {bar_width}%; background: linear-gradient(90deg, {color}99, {color}); height: 100%; border-radius: 4px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; box-shadow: 0 0 10px {color}33;">'
        f'<span style="font-family: \'JetBrains Mono\', monospace; font-size: 11px; font-weight: 700; color: #0A0E1A;">{pct_label}</span>'
        f'</div>'
        f'</div>'
        f'<div style="width: 110px; text-align: right; font-family: \'JetBrains Mono\', monospace; font-size: 13px; font-weight: 700; color: {color}; flex-shrink: 0;">'
        f'{count} <span style="font-size: 11px; color: #64748B; font-weight: 400;">({pct}%)</span>'
        f'</div>'
        f'</div>'
    )
    bar_rows_html.append(row_html)

graph_container_html = (
    f'<div style="background: #111827; border: 1px solid #1F2937; border-radius: 10px; padding: 22px 24px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">'
    f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #1F2937; padding-bottom: 12px;">'
    f'<div style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; font-weight: 700; color: #00D4FF; letter-spacing: 0.1em; text-transform: uppercase; display: flex; align-items: center; gap: 8px;">'
    f'<span>📊</span> THREAT CATEGORY DISTRIBUTION GRAPH'
    f'</div>'
    f'<div style="font-family: \'JetBrains Mono\', monospace; font-size: 11px; color: #64748B;">'
    f'{len(categories)} CATEGORIES &bull; {total_articles} ARTICLES'
    f'</div>'
    f'</div>'
    f'{"".join(bar_rows_html)}'
    f'</div>'
)

st.markdown(graph_container_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# Category Filter & Articles
# ============================================

st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00D4FF; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">
    // ARTICLES BY CATEGORY
</div>
""", unsafe_allow_html=True)

category_options = ["All Categories"] + sorted(categories.keys())
default_filter = st.session_state.get("category_filter", "All Categories")
if default_filter not in category_options:
    default_filter = "All Categories"

selected_cat = st.selectbox(
    "Filter by Category",
    options=category_options,
    index=category_options.index(default_filter),
)

if selected_cat == "All Categories":
    display_articles = sorted(
        classified,
        key=lambda a: (a.category == "Uncategorized", a.title),
    )
else:
    display_articles = [a for a in classified if a.category == selected_cat]

st.caption(f"Displaying **{len(display_articles)}** articles")
st.markdown("<br>", unsafe_allow_html=True)

for article in display_articles:
    badge_html = get_category_badge_html(article.category)
    border_color = get_category_left_border(article.category)

    conf_pct = int(article.confidence * 100)
    confidence_label = f"Relevance: {conf_pct}%"
    method = getattr(article, "classification_method", "") or "unknown"
    method_labels = {
        "llm": "LLM",
        "keyword": "Keywords",
        "forced_llm": "Forced LLM",
        "best_guess": "Best guess",
        "mandatory": "Auto-assigned",
        "uncategorized": "Unclassified",
    }
    method_label = method_labels.get(method, method)

    article_html = (
        f'<div style="background: #111827; border: 1px solid #1F2937; border-left: 3px solid {border_color}; border-radius: 0 8px 8px 0; padding: 18px 20px; margin-bottom: 10px;">'
        f'<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">'
        f'<a href="{article.link}" target="_blank" style="font-size: 15px; font-weight: 600; color: #F1F5F9; text-decoration: none; line-height: 1.4;">'
        f'{article.title} ↗'
        f'</a>'
        f'{badge_html}'
        f'</div>'
        f'<div style="display: flex; gap: 16px; margin-bottom: 10px; font-family: \'JetBrains Mono\', monospace; font-size: 12px;">'
        f'<span style="color: #00D4FF;">📡 {article.source}</span>'
        f'<span style="color: #64748B;">🗓️ {article.published or "Recent"}</span>'
        f'<span style="color: {border_color};">🎯 {confidence_label}</span>'
        f'<span style="color: #A78BFA;">⚙️ {method_label}</span>'
        f'</div>'
        f'<div style="font-size: 13px; color: #94A3B8; line-height: 1.6;">'
        f'{article.summary[:300] + ("..." if len(article.summary) > 300 else "") if article.summary else "No preview summary available."}'
        f'</div>'
        f'</div>'
    )
    st.markdown(article_html, unsafe_allow_html=True)
