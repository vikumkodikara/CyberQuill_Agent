"""
CyberQuill — Theme Utilities & Reusable Components
=====================================================

Provides dark cybersecurity terminal styling helpers:
    - apply_custom_theme() — injects the global dark CSS
    - render_page_header() — terminal-style page header
    - get_category_badge_html() — dark-themed category badges
    - get_category_pill_style() — category color tuples
    - render_sidebar_controls() — session state defaults
"""

import streamlit as st
from utils.styles import inject_dark_theme


def apply_custom_theme():
    """Injects global dark cybersecurity terminal CSS."""
    inject_dark_theme()


def render_page_header(title: str, subtitle: str, icon: str = ""):
    """
    Renders a terminal-style page header with a monospace tag line,
    bold title, and muted subtitle.
    """
    apply_custom_theme()
    # Build a tag from the title (e.g. "News Feed" -> "// NEWS FEED")
    tag = f"// {title.upper()}"
    st.markdown(f"""
    <div class="page-header">
        <div class="page-tag">{tag}</div>
        <h1>{icon} {title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def get_category_badge_html(category: str) -> str:
    """Returns HTML for a dark-themed threat category badge."""
    cat_lower = category.lower()
    if "malware" in cat_lower or "ransomware" in cat_lower:
        cls = "cat-malware"
    elif "breach" in cat_lower or "leak" in cat_lower:
        cls = "cat-databreach"
    elif "phish" in cat_lower or "social" in cat_lower:
        cls = "cat-phishing"
    elif "ai" in cat_lower or "llm" in cat_lower:
        cls = "cat-aisecurity"
    elif "vuln" in cat_lower or "cve" in cat_lower:
        cls = "cat-vulnerability"
    elif "zero-day" in cat_lower or "zero day" in cat_lower:
        cls = "cat-zeroday"
    elif "cloud" in cat_lower:
        cls = "cat-cloud"
    elif "intel" in cat_lower or "threat" in cat_lower:
        cls = "cat-intel"
    else:
        cls = "cat-general"

    return f'<span class="category-badge {cls}">{category}</span>'


def get_category_pill_style(category: str) -> tuple[str, str, str]:
    """Returns (bg_color, text_color, border_color) for a category — dark theme."""
    cat_lower = category.lower()
    if "malware" in cat_lower or "ransomware" in cat_lower:
        return "#FF33660F", "#FF3366", "#FF336633"
    elif "breach" in cat_lower or "leak" in cat_lower:
        return "#EF44440F", "#F87171", "#EF444433"
    elif "phish" in cat_lower or "social" in cat_lower:
        return "#7C3AED0F", "#A78BFA", "#7C3AED33"
    elif "ai" in cat_lower or "llm" in cat_lower:
        return "#7C3AED0F", "#A78BFA", "#7C3AED33"
    elif "vuln" in cat_lower or "cve" in cat_lower:
        return "#F59E0B0F", "#FCD34D", "#F59E0B33"
    elif "zero-day" in cat_lower or "zero day" in cat_lower:
        return "#FF6B000F", "#FF6B00", "#FF6B0033"
    elif "cloud" in cat_lower:
        return "#10B9810F", "#34D399", "#10B98133"
    elif "intel" in cat_lower or "threat" in cat_lower:
        return "#00D4FF0F", "#00D4FF", "#00D4FF33"
    else:
        return "#64748B0F", "#94A3B8", "#64748B33"


def get_category_left_border(category: str) -> str:
    """Returns a left-border CSS color for a category."""
    cat_lower = category.lower()
    if "malware" in cat_lower or "ransomware" in cat_lower:
        return "#FF3366"
    elif "breach" in cat_lower or "leak" in cat_lower:
        return "#F87171"
    elif "phish" in cat_lower or "social" in cat_lower:
        return "#A78BFA"
    elif "ai" in cat_lower or "llm" in cat_lower:
        return "#A78BFA"
    elif "vuln" in cat_lower or "cve" in cat_lower:
        return "#FCD34D"
    elif "zero-day" in cat_lower or "zero day" in cat_lower:
        return "#FF6B00"
    elif "cloud" in cat_lower:
        return "#34D399"
    elif "intel" in cat_lower or "threat" in cat_lower:
        return "#00D4FF"
    else:
        return "#64748B"


def render_sidebar_controls():
    """
    Ensures default session state values.
    Dark mode is always enabled for the cybersecurity terminal aesthetic.
    """
    if "ui_mode" not in st.session_state:
        st.session_state["ui_mode"] = "magazine"
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = True
