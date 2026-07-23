"""
CyberQuill — Streamlit Modern UI Theme & Helper Components
===========================================================

Provides consistent, high-aesthetic CSS styling, modern typography,
glassmorphism cards, glowing badges, micro-animations, and reusable layout elements.
"""

import streamlit as st

def apply_custom_theme():
    """Injects global custom CSS for a modern, sleek, high-aesthetic UI."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&display=swap');

        /* Global Typography & Font Family */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #1e293b;
        }

        /* Container Padding */
        .main .block-container {
            padding-top: 1.8rem;
            padding-bottom: 3.5rem;
            max-width: 1280px;
        }

        /* Sidebar Customization */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        [data-testid="stSidebar"] * {
            color: #94a3b8 !important;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #f8fafc !important;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
            border-radius: 10px;
            padding: 8px 12px;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
            background-color: rgba(56, 189, 248, 0.1) !important;
            color: #38bdf8 !important;
        }

        /* Page Headers */
        .page-header-container {
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e2e8f0;
        }
        .page-header-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.25rem;
            font-weight: 800;
            color: #0f172a;
            margin: 0 0 0.5rem 0;
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: -0.02em;
        }
        .page-header-subtitle {
            font-size: 1.05rem;
            color: #64748b;
            margin: 0;
            line-height: 1.5;
        }

        /* Quick Navigation Cards styling */
        .nav-card {
            position: relative;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            overflow: hidden;
        }
        .nav-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 20px 30px -10px rgba(99, 102, 241, 0.15), 0 10px 15px -5px rgba(0, 0, 0, 0.04);
            border-color: rgba(99, 102, 241, 0.4);
        }
        .nav-card-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
        }
        .nav-card-icon {
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
        }
        .nav-card-tag {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 4px 10px;
            border-radius: 20px;
            background: #f1f5f9;
            color: #475569;
            border: 1px solid #e2e8f0;
        }
        .nav-card-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: #0f172a;
            margin: 0 0 0.5rem 0;
            line-height: 1.3;
        }
        .nav-card-desc {
            font-size: 0.9rem;
            color: #64748b;
            line-height: 1.55;
            margin-bottom: 1.25rem;
            flex-grow: 1;
        }
        .nav-card-footer {
            margin-top: auto;
            padding-top: 0.75rem;
        }

        /* Metric Cards */
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1rem 1.25rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        [data-testid="stMetric"]:hover {
            border-color: #38bdf8;
            transform: translateY(-2px);
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            color: #64748b !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        [data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.85rem !important;
            font-weight: 800 !important;
            color: #0f172a !important;
        }

        /* Category Badges */
        .category-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }
        .cat-malware { background: #fef2f2; color: #dc2626; border: 1px solid #fca5a5; }
        .cat-databreach { background: #fff7ed; color: #c2410c; border: 1px solid #fdba74; }
        .cat-phishing { background: #faf5ff; color: #7e22ce; border: 1px solid #d8b4fe; }
        .cat-aisecurity { background: #f0fdf4; color: #15803d; border: 1px solid #86efac; }
        .cat-vulnerability { background: #f0f9ff; color: #0369a1; border: 1px solid #7dd3fc; }
        .cat-cloud { background: #fefce8; color: #a16207; border: 1px solid #fde047; }
        .cat-general { background: #f8fafc; color: #475569; border: 1px solid #cbd5e1; }

        /* Article Glass Cards */
        .article-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
        }
        .article-card:hover {
            border-color: #94a3b8;
            box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.08);
            transform: translateY(-2px);
        }

        /* Custom Buttons */
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
            border: none;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
        }
        .stButton>button[kind="primary"]:hover {
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
            transform: translateY(-1px);
        }

        /* Custom Scrollbar for code blocks & logs */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
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
