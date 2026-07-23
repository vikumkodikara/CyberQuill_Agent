"""
CyberQuill — Streamlit Modern UI Theme & Helper Components
===========================================================

Provides consistent, high-aesthetic CSS styling, modern typography,
glassmorphism cards, glowing badges, micro-animations, and reusable layout elements.
Supports Magazine Mode (reader-facing) and Debug Mode (developer-facing),
as well as an optional dark mode toggle.
"""

import streamlit as st


def apply_custom_theme():
    """Injects global custom CSS for a modern, sleek, high-aesthetic UI."""

    dark = st.session_state.get("dark_mode", False)

    # Base colour tokens
    if dark:
        bg_primary = "#0b0f19"
        bg_card = "#111827"
        bg_sidebar = "#070b14"
        border_card = "#1e293b"
        text_primary = "#f1f5f9"
        text_secondary = "#94a3b8"
        text_muted = "#64748b"
        accent = "#38bdf8"
        accent2 = "#6366f1"
        hover_border = "#6366f1"
        hover_shadow = "rgba(99, 102, 241, 0.25)"
        metric_bg = "#111827"
        scrollbar_track = "#1e293b"
        scrollbar_thumb = "#334155"
    else:
        bg_primary = "#ffffff"
        bg_card = "#ffffff"
        bg_sidebar = "#0f172a"
        border_card = "#e2e8f0"
        text_primary = "#0f172a"
        text_secondary = "#64748b"
        text_muted = "#94a3b8"
        accent = "#38bdf8"
        accent2 = "#6366f1"
        hover_border = "#818cf8"
        hover_shadow = "rgba(99, 102, 241, 0.15)"
        metric_bg = "#ffffff"
        scrollbar_track = "#f1f5f9"
        scrollbar_thumb = "#cbd5e1"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&display=swap');

        /* Global Typography & Font Family */
        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: {text_primary};
        }}

        /* Dark mode body background */
        {"" if not dark else f'''
        .stApp {{
            background-color: {bg_primary} !important;
        }}
        .main .block-container {{
            background-color: {bg_primary} !important;
        }}
        '''}

        /* Container Padding */
        .main .block-container {{
            padding-top: 1.8rem;
            padding-bottom: 3.5rem;
            max-width: 1280px;
        }}

        /* Sidebar Customization */
        [data-testid="stSidebar"] {{
            background-color: {bg_sidebar};
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}
        [data-testid="stSidebar"] * {{
            color: #94a3b8 !important;
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: #f8fafc !important;
        }}
        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {{
            border-radius: 10px;
            padding: 8px 12px;
            transition: all 0.2s ease;
        }}
        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {{
            background-color: rgba(56, 189, 248, 0.1) !important;
            color: #38bdf8 !important;
        }}

        /* Page Headers */
        .page-header-container {{
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid {border_card};
        }}
        .page-header-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.25rem;
            font-weight: 800;
            color: {text_primary};
            margin: 0 0 0.5rem 0;
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: -0.02em;
        }}
        .page-header-subtitle {{
            font-size: 1.05rem;
            color: {text_secondary};
            margin: 0;
            line-height: 1.5;
        }}

        /* Quick Navigation Cards styling */
        .nav-card {{
            position: relative;
            background: {bg_card};
            border: 1px solid {border_card};
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            overflow: hidden;
        }}
        .nav-card:hover {{
            transform: translateY(-6px);
            box-shadow: 0 20px 30px -10px {hover_shadow}, 0 10px 15px -5px rgba(0, 0, 0, 0.04);
            border-color: {hover_border};
        }}
        .nav-card-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
        }}
        .nav-card-icon {{
            width: 48px;
            height: 48px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            border: 1px solid #cbd5e1;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
        }}
        .nav-card-tag {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 4px 10px;
            border-radius: 20px;
            background: #f1f5f9;
            color: #475569;
            border: 1px solid #e2e8f0;
        }}
        .nav-card-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: {text_primary};
            margin: 0 0 0.5rem 0;
            line-height: 1.3;
        }}
        .nav-card-desc {{
            font-size: 0.9rem;
            color: {text_secondary};
            line-height: 1.55;
            margin-bottom: 1.25rem;
            flex-grow: 1;
        }}
        .nav-card-footer {{
            margin-top: auto;
            padding-top: 0.75rem;
        }}

        /* Metric Cards */
        [data-testid="stMetric"] {{
            background: {metric_bg};
            border: 1px solid {border_card};
            border-radius: 14px;
            padding: 1rem 1.25rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        [data-testid="stMetric"]:hover {{
            border-color: {accent};
            transform: translateY(-2px);
        }}
        [data-testid="stMetricLabel"] {{
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            color: {text_secondary} !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        [data-testid="stMetricValue"] {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.85rem !important;
            font-weight: 800 !important;
            color: {text_primary} !important;
        }}

        /* Category Badges */
        .category-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }}
        .cat-malware {{ background: #fef2f2; color: #dc2626; border: 1px solid #fca5a5; }}
        .cat-databreach {{ background: #fff7ed; color: #c2410c; border: 1px solid #fdba74; }}
        .cat-phishing {{ background: #faf5ff; color: #7e22ce; border: 1px solid #d8b4fe; }}
        .cat-aisecurity {{ background: #f0fdf4; color: #15803d; border: 1px solid #86efac; }}
        .cat-vulnerability {{ background: #f0f9ff; color: #0369a1; border: 1px solid #7dd3fc; }}
        .cat-cloud {{ background: #fefce8; color: #a16207; border: 1px solid #fde047; }}
        .cat-general {{ background: #f8fafc; color: #475569; border: 1px solid #cbd5e1; }}

        /* Article Glass Cards */
        .article-card {{
            background: {bg_card};
            border: 1px solid {border_card};
            border-radius: 14px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
        }}
        .article-card:hover {{
            border-color: #94a3b8;
            box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.08);
            transform: translateY(-2px);
        }}

        /* ============================================
           Magazine-Specific Cards
           ============================================ */

        /* Featured Article Banner */
        .featured-article {{
            background: linear-gradient(135deg, #0b0f19 0%, #1e1b4b 100%);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 20px;
            padding: 2rem 2.5rem;
            color: #ffffff;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px -10px rgba(15, 23, 42, 0.4);
            position: relative;
            overflow: hidden;
        }}
        .featured-article::before {{
            content: '';
            position: absolute;
            top: -40%;
            right: -15%;
            width: 50%;
            height: 200%;
            background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, transparent 60%);
            pointer-events: none;
        }}
        .featured-article .featured-label {{
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #38bdf8;
            margin-bottom: 0.75rem;
        }}
        .featured-article .featured-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.8rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.75rem;
            color: #ffffff;
        }}
        .featured-article .featured-excerpt {{
            font-size: 1rem;
            color: #94a3b8;
            line-height: 1.6;
            margin-bottom: 1rem;
            max-width: 700px;
        }}
        .featured-article .featured-meta {{
            display: flex;
            gap: 16px;
            font-size: 0.82rem;
            color: #64748b;
        }}

        /* Magazine Article Preview Card */
        .magazine-preview-card {{
            background: {bg_card};
            border: 1px solid {border_card};
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.25rem;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
        }}
        .magazine-preview-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 16px 32px -8px rgba(15, 23, 42, 0.1);
            border-color: {hover_border};
        }}
        .magazine-preview-card .card-category {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 3px 10px;
            border-radius: 12px;
            margin-bottom: 0.75rem;
        }}
        .magazine-preview-card .card-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.15rem;
            font-weight: 700;
            color: {text_primary};
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }}
        .magazine-preview-card .card-excerpt {{
            font-size: 0.9rem;
            color: {text_secondary};
            line-height: 1.55;
            margin-bottom: 0.75rem;
        }}
        .magazine-preview-card .card-meta {{
            display: flex;
            gap: 12px;
            font-size: 0.78rem;
            color: {text_muted};
        }}

        /* Reading Time Badge */
        .reading-time {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 0.78rem;
            color: {text_muted};
            font-weight: 600;
        }}

        /* Issue Banner */
        .issue-banner {{
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: 18px;
            padding: 1.5rem 2rem;
            color: #ffffff;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 12px 30px -8px rgba(15, 23, 42, 0.35);
        }}
        .issue-banner .issue-number {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            color: #38bdf8;
            letter-spacing: 0.04em;
        }}
        .issue-banner .issue-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.5rem;
            font-weight: 800;
            margin: 0.25rem 0;
        }}
        .issue-banner .issue-meta {{
            font-size: 0.88rem;
            color: #94a3b8;
        }}

        /* Section Divider */
        .section-divider {{
            border: none;
            border-top: 1px solid {border_card};
            margin: 2rem 0;
        }}

        /* Custom Buttons */
        .stButton>button {{
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .stButton>button[kind="primary"] {{
            background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
            border: none;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
        }}
        .stButton>button[kind="primary"]:hover {{
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
            transform: translateY(-1px);
        }}

        /* Custom Scrollbar for code blocks & logs */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: {scrollbar_track};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb {{
            background: {scrollbar_thumb};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #94a3b8;
        }}
    </style>
    """, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str, icon: str = ""):
    """Renders a sleek, modern header for pages."""
    apply_custom_theme()
    st.markdown(f"""
    <div class="page-header-container">
        <div class="page-header-title">
            <span>{icon}</span> {title}
        </div>
        <div class="page-header-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def get_category_badge_html(category: str) -> str:
    """Returns HTML for a color-coded threat category badge."""
    cat_lower = category.lower()
    if "malware" in cat_lower or "ransomware" in cat_lower:
        cls = "cat-malware"
    elif "breach" in cat_lower or "leak" in cat_lower:
        cls = "cat-databreach"
    elif "phish" in cat_lower or "social" in cat_lower:
        cls = "cat-phishing"
    elif "ai" in cat_lower or "llm" in cat_lower:
        cls = "cat-aisecurity"
    elif "vuln" in cat_lower or "cve" in cat_lower or "zero-day" in cat_lower:
        cls = "cat-vulnerability"
    elif "cloud" in cat_lower:
        cls = "cat-cloud"
    else:
        cls = "cat-general"
    
    return f'<span class="category-badge {cls}">🏷️ {category}</span>'


def get_category_pill_style(category: str) -> tuple[str, str, str]:
    """Returns (bg_color, text_color, border_color) for a category."""
    cat_lower = category.lower()
    if "malware" in cat_lower or "ransomware" in cat_lower:
        return "#fef2f2", "#dc2626", "#fca5a5"
    elif "breach" in cat_lower or "leak" in cat_lower:
        return "#fff7ed", "#c2410c", "#fdba74"
    elif "phish" in cat_lower or "social" in cat_lower:
        return "#faf5ff", "#7e22ce", "#d8b4fe"
    elif "ai" in cat_lower or "llm" in cat_lower:
        return "#f0fdf4", "#15803d", "#86efac"
    elif "vuln" in cat_lower or "cve" in cat_lower or "zero-day" in cat_lower:
        return "#f0f9ff", "#0369a1", "#7dd3fc"
    elif "cloud" in cat_lower:
        return "#fefce8", "#a16207", "#fde047"
    else:
        return "#f8fafc", "#475569", "#cbd5e1"


def render_sidebar_controls():
    """
    Ensures default session state values without displaying extra sidebar settings.
    """
    if "ui_mode" not in st.session_state:
        st.session_state["ui_mode"] = "magazine"
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False
