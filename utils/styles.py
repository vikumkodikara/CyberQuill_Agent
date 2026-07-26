"""
CyberQuill — Dark Cybersecurity Terminal Theme
================================================

Centralized CSS injection for the dark, high-tech threat intelligence
terminal aesthetic. Imported by every page via inject_dark_theme().

Design language:
    - Military threat intelligence terminal meets premium digital magazine
    - Dark backgrounds with electric cyan and deep purple accents
    - JetBrains Mono for data/code, Inter for prose
    - Card surfaces with subtle borders and gradient top accents
"""

import streamlit as st


def inject_dark_theme():
    """
    Injects the complete dark cybersecurity terminal CSS into the page.
    Call this once at the top of every Streamlit page.
    """
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>
        /* =============================================
           GLOBAL RESET & TYPOGRAPHY
           ============================================= */

        /* Hide Streamlit default branding */
        #MainMenu, footer, header {visibility: hidden;}

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #E2E8F0;
        }

        /* App background */
        .stApp {
            background-color: #0A0E1A !important;
        }

        .main .block-container {
            background: #0A0E1A;
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1300px;
        }

        /* =============================================
           SIDEBAR
           ============================================= */

        [data-testid="stSidebar"] {
            background: #0D1117 !important;
            border-right: 1px solid #00D4FF22;
        }

        [data-testid="stSidebar"] * {
            color: #64748B !important;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #00D4FF !important;
            font-family: 'JetBrains Mono', monospace !important;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
            border-radius: 0;
            padding: 8px 16px;
            border-left: 2px solid transparent;
            transition: all 0.2s;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
            color: #00D4FF !important;
            border-left-color: #00D4FF;
            background: #00D4FF0A !important;
        }

        /* =============================================
           PAGE HEADERS
           ============================================= */

        .page-header {
            border-bottom: 1px solid #1F2937;
            padding-bottom: 20px;
            margin-bottom: 32px;
        }

        .page-header .page-tag {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #00D4FF;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            margin-bottom: 8px;
        }

        .page-header h1 {
            font-family: 'Inter', sans-serif;
            font-size: 28px;
            font-weight: 700;
            color: #F1F5F9;
            margin: 0 0 8px;
        }

        .page-header p {
            color: #64748B;
            font-size: 14px;
            margin: 0;
        }

        /* =============================================
           METRIC CARDS (Streamlit widgets)
           ============================================= */

        [data-testid="stMetric"] {
            background: #111827;
            border: 1px solid #1F2937;
            border-radius: 8px;
            padding: 16px !important;
            position: relative;
            overflow: hidden;
        }

        [data-testid="stMetric"]::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, #00D4FF, #7C3AED);
        }

        [data-testid="stMetricLabel"] {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 11px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            color: #64748B !important;
        }

        [data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace !important;
            color: #00D4FF !important;
            font-size: 28px !important;
            font-weight: 700 !important;
        }

        /* =============================================
           ARTICLE CARDS
           ============================================= */

        .article-card {
            background: #111827;
            border: 1px solid #1F2937;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 12px;
            transition: border-color 0.2s;
        }

        .article-card:hover {
            border-color: #00D4FF44;
        }

        /* =============================================
           CATEGORY BADGES
           ============================================= */

        .category-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .cat-malware     { background: #FF33660F; color: #FF3366; border: 1px solid #FF336633; }
        .cat-databreach   { background: #EF44440F; color: #F87171; border: 1px solid #EF444433; }
        .cat-phishing     { background: #7C3AED0F; color: #A78BFA; border: 1px solid #7C3AED33; }
        .cat-aisecurity   { background: #7C3AED0F; color: #A78BFA; border: 1px solid #7C3AED33; }
        .cat-vulnerability{ background: #F59E0B0F; color: #FCD34D; border: 1px solid #F59E0B33; }
        .cat-zeroday      { background: #FF6B000F; color: #FF6B00; border: 1px solid #FF6B0033; }
        .cat-cloud        { background: #10B9810F; color: #34D399; border: 1px solid #10B98133; }
        .cat-intel        { background: #00D4FF0F; color: #00D4FF; border: 1px solid #00D4FF33; }
        .cat-general      { background: #64748B0F; color: #94A3B8; border: 1px solid #64748B33; }

        /* =============================================
           NAVIGATION CARDS (Home Page)
           ============================================= */

        .nav-card {
            background: #111827;
            border: 1px solid #1F2937;
            border-radius: 8px;
            padding: 1.5rem;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            overflow: hidden;
        }

        .nav-card:hover {
            transform: translateY(-4px);
            border-color: #00D4FF44;
            box-shadow: 0 12px 24px rgba(0, 212, 255, 0.08);
        }

        .nav-card-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }

        .nav-card-icon {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
        }

        .nav-card-tag {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            padding: 3px 8px;
            border-radius: 4px;
        }

        .nav-card-title {
            font-family: 'Inter', sans-serif;
            font-size: 1.15rem;
            font-weight: 700;
            color: #F1F5F9;
            margin: 0 0 0.5rem 0;
            line-height: 1.3;
        }

        .nav-card-desc {
            font-size: 0.85rem;
            color: #64748B;
            line-height: 1.55;
            margin-bottom: 1rem;
            flex-grow: 1;
        }

        /* =============================================
           FEATURED ARTICLE BANNER
           ============================================= */

        .featured-article {
            background: linear-gradient(135deg, #0D1117 0%, #111827 50%, #1a1040 100%);
            border: 1px solid #7C3AED33;
            border-radius: 12px;
            padding: 2rem 2.5rem;
            color: #ffffff;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }

        .featured-article::before {
            content: '';
            position: absolute;
            top: -40%;
            right: -15%;
            width: 50%;
            height: 200%;
            background: radial-gradient(circle, rgba(0, 212, 255, 0.08) 0%, transparent 60%);
            pointer-events: none;
        }

        .featured-article .featured-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #00D4FF;
            margin-bottom: 0.75rem;
        }

        .featured-article .featured-title {
            font-size: 1.6rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.75rem;
            color: #F1F5F9;
        }

        .featured-article .featured-excerpt {
            font-size: 0.95rem;
            color: #94A3B8;
            line-height: 1.6;
            margin-bottom: 1rem;
            max-width: 700px;
        }

        .featured-article .featured-meta {
            display: flex;
            gap: 16px;
            font-size: 0.82rem;
            color: #64748B;
        }

        /* =============================================
           MAGAZINE PREVIEW CARDS
           ============================================= */

        .magazine-preview-card {
            background: #111827;
            border: 1px solid #1F2937;
            border-radius: 8px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
        }

        .magazine-preview-card:hover {
            border-color: #00D4FF44;
        }

        .magazine-preview-card .card-category {
            display: inline-block;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 3px 10px;
            border-radius: 4px;
            margin-bottom: 0.75rem;
        }

        .magazine-preview-card .card-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #F1F5F9;
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }

        .magazine-preview-card .card-excerpt {
            font-size: 0.88rem;
            color: #94A3B8;
            line-height: 1.55;
            margin-bottom: 0.75rem;
        }

        .magazine-preview-card .card-meta {
            display: flex;
            gap: 12px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #64748B;
        }

        /* =============================================
           ISSUE BANNER
           ============================================= */

        .issue-banner {
            background: linear-gradient(135deg, #0D1117 0%, #1a1040 100%);
            border: 1px solid #7C3AED33;
            border-radius: 12px;
            padding: 1.5rem 2rem;
            color: #ffffff;
            text-align: center;
            margin-bottom: 2rem;
        }

        .issue-banner .issue-number {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1rem;
            font-weight: 700;
            color: #00D4FF;
            letter-spacing: 0.08em;
        }

        .issue-banner .issue-title {
            font-size: 1.4rem;
            font-weight: 700;
            margin: 0.25rem 0;
            color: #F1F5F9;
        }

        .issue-banner .issue-meta {
            font-size: 0.85rem;
            color: #64748B;
        }

        /* =============================================
           PIPELINE STEP CARDS
           ============================================= */

        .pipeline-step {
            background: #111827;
            border: 1px solid #1F2937;
            border-radius: 8px;
            padding: 16px 8px;
            text-align: center;
            height: 100%;
            transition: border-color 0.2s;
        }

        .pipeline-step:hover {
            border-color: #00D4FF44;
        }

        .pipeline-step .step-number {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: #00D4FF;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 6px;
        }

        .pipeline-step .step-icon {
            font-size: 1.6rem;
            margin-bottom: 4px;
        }

        .pipeline-step .step-name {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 600;
            color: #F1F5F9;
        }

        .pipeline-step .step-sub {
            font-size: 11px;
            color: #64748B;
            margin-top: 2px;
        }

        /* =============================================
           BUTTONS
           ============================================= */

        .stButton > button {
            background: #111827 !important;
            border: 1px solid #1F2937 !important;
            color: #E2E8F0 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12px !important;
            letter-spacing: 0.05em !important;
            border-radius: 6px !important;
            transition: all 0.15s !important;
        }

        .stButton > button:hover {
            border-color: #00D4FF44 !important;
            color: #00D4FF !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #00D4FF20, #7C3AED20) !important;
            border-color: #00D4FF66 !important;
            color: #00D4FF !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #00D4FF30, #7C3AED30) !important;
            border-color: #00D4FF !important;
        }

        /* =============================================
           INPUTS & SELECTS (BaseWeb Dark Cybersecurity Theme)
           ============================================= */

        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea,
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"],
        div[data-baseweb="input"] {
            background-color: #111827 !important;
            background: #111827 !important;
            border-color: #1F2937 !important;
            color: #E2E8F0 !important;
            font-family: 'JetBrains Mono', monospace !important;
            border-radius: 6px !important;
        }

        /* Focus & Hover states for BaseWeb controls */
        div[data-baseweb="select"]:hover > div,
        div[data-baseweb="base-input"]:hover,
        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border-color: #00D4FF66 !important;
            box-shadow: 0 0 0 1px #00D4FF44 !important;
        }

        /* Multiselect / Selectbox inner input text */
        div[data-baseweb="select"] input {
            color: #E2E8F0 !important;
            font-family: 'JetBrains Mono', monospace !important;
            background: transparent !important;
        }

        /* Dropdown icons (arrow down, clear x) */
        div[data-baseweb="select"] svg,
        [data-baseweb="icon"] {
            fill: #64748B !important;
            color: #64748B !important;
        }

        div[data-baseweb="select"] svg:hover,
        [data-baseweb="icon"]:hover {
            fill: #00D4FF !important;
            color: #00D4FF !important;
        }

        /* Multiselect Tags / Badges (Selected Items) */
        [data-baseweb="tag"] {
            background: #00D4FF1A !important;
            border: 1px solid #00D4FF44 !important;
            border-radius: 4px !important;
            padding: 2px 8px !important;
            margin: 2px !important;
        }

        [data-baseweb="tag"] span,
        [data-baseweb="tag"] div {
            color: #00D4FF !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12px !important;
            font-weight: 600 !important;
        }

        [data-baseweb="tag"] [data-baseweb="icon"],
        [data-baseweb="tag"] svg {
            fill: #00D4FF !important;
            color: #00D4FF !important;
            cursor: pointer !important;
        }

        [data-baseweb="tag"] [data-baseweb="icon"]:hover,
        [data-baseweb="tag"] svg:hover {
            fill: #FF3366 !important;
            color: #FF3366 !important;
        }

        /* Dropdown Popover & Menu Options */
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        div[role="listbox"],
        ul[role="listbox"] {
            background-color: #111827 !important;
            background: #111827 !important;
            border: 1px solid #1F2937 !important;
            border-radius: 8px !important;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6) !important;
        }

        [data-baseweb="option"],
        li[role="option"],
        div[role="option"] {
            background-color: #111827 !important;
            color: #CBD5E1 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 13px !important;
            padding: 8px 12px !important;
        }

        [data-baseweb="option"]:hover,
        li[role="option"]:hover,
        div[role="option"]:hover,
        [aria-selected="true"][data-baseweb="option"] {
            background-color: #1F2937 !important;
            color: #00D4FF !important;
        }

        .stSlider > div > div > div {
            color: #00D4FF !important;
        }

        /* =============================================
           EXPANDERS
           ============================================= */

        .streamlit-expanderHeader {
            background: #111827 !important;
            border: 1px solid #1F2937 !important;
            border-radius: 6px !important;
            color: #E2E8F0 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 13px !important;
        }

        details {
            background: #111827 !important;
            border: 1px solid #1F2937 !important;
            border-radius: 8px !important;
        }

        details summary {
            color: #E2E8F0 !important;
        }

        details[open] > div {
            background: #0D1117 !important;
            color: #CBD5E1 !important;
        }

        /* =============================================
           PROGRESS BAR
           ============================================= */

        .stProgress > div > div > div {
            background: linear-gradient(90deg, #00D4FF, #7C3AED) !important;
        }

        /* =============================================
           TABS
           ============================================= */

        .stTabs [data-baseweb="tab-list"] {
            background: #111827;
            border-radius: 8px;
            padding: 4px;
        }

        .stTabs [data-baseweb="tab"] {
            color: #64748B !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12px !important;
        }

        .stTabs [aria-selected="true"] {
            color: #00D4FF !important;
            border-bottom-color: #00D4FF !important;
        }

        /* =============================================
           ALERTS & INFO BOXES
           ============================================= */

        .stAlert, [data-testid="stNotification"] {
            background: #111827 !important;
            border: 1px solid #1F2937 !important;
            color: #E2E8F0 !important;
        }

        /* =============================================
           SCROLLBAR
           ============================================= */

        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #0A0E1A; }
        ::-webkit-scrollbar-thumb { background: #1F2937; border-radius: 2px; }
        ::-webkit-scrollbar-thumb:hover { background: #374151; }

        /* =============================================
           DIVIDERS
           ============================================= */

        hr, .stDivider {
            border-color: #1F2937 !important;
        }

        /* =============================================
           ANIMATIONS
           ============================================= */

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }

        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 4px #00FF88; }
            50% { box-shadow: 0 0 12px #00FF88, 0 0 20px #00FF8844; }
        }

        .cursor-blink {
            animation: blink 1s step-end infinite;
            color: #00D4FF;
        }

        .pulse-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00FF88;
            animation: pulse 2s ease-in-out infinite;
            margin-right: 8px;
        }

        .live-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 700;
            color: #00FF88;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            background: #00FF8812;
            border: 1px solid #00FF8833;
            padding: 3px 10px;
            border-radius: 4px;
        }

        /* =============================================
           CHART STYLING (Dark Theme Containers)
           ============================================= */

        .js-plotly-plot .plotly,
        .js-plotly-plot .plotly .main-svg,
        .js-plotly-plot .plotly .bg {
            background: #111827 !important;
            background-color: #111827 !important;
        }

        /* Streamlit Vega-Lite / bar chart dark container */
        [data-testid="stVegaLiteChart"] {
            background-color: #111827 !important;
            border: 1px solid #1F2937 !important;
            border-radius: 8px !important;
            padding: 16px !important;
        }

        .vega-embed {
            background-color: transparent !important;
            background: transparent !important;
        }

        /* SVG text elements inside charts */
        [data-testid="stVegaLiteChart"] text,
        .vega-embed text {
            fill: #94A3B8 !important;
            font-family: 'JetBrains Mono', monospace !important;
        }

        [data-testid="stVegaLiteChart"] line,
        [data-testid="stVegaLiteChart"] path.domain {
            stroke: #1F2937 !important;
        }

        /* Vega action menu items */
        .vega-embed .vega-actions {
            background-color: #111827 !important;
            border: 1px solid #1F2937 !important;
            border-radius: 6px !important;
        }

        .vega-embed .vega-actions a {
            color: #00D4FF !important;
        }

        /* =============================================
           DOWNLOAD BUTTON
           ============================================= */

        .stDownloadButton > button {
            background: linear-gradient(135deg, #00D4FF20, #7C3AED20) !important;
            border: 1px solid #00D4FF66 !important;
            color: #00D4FF !important;
            font-family: 'JetBrains Mono', monospace !important;
        }

        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #00D4FF30, #7C3AED30) !important;
            border-color: #00D4FF !important;
        }

        /* =============================================
           MARKDOWN TEXT OVERRIDES
           ============================================= */

        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: #F1F5F9 !important;
        }

        .stMarkdown p, .stMarkdown li {
            color: #CBD5E1;
        }

        .stMarkdown a {
            color: #00D4FF;
        }

        .stMarkdown code {
            background: #1F2937;
            color: #00D4FF;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
        }

        /* =============================================
           TABLE OVERRIDES
           ============================================= */

        .stMarkdown table {
            border-collapse: collapse;
            width: 100%;
        }

        .stMarkdown table th {
            background: #1F2937;
            color: #00D4FF;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 10px 14px;
            border: 1px solid #374151;
        }

        .stMarkdown table td {
            background: #111827;
            color: #CBD5E1;
            padding: 10px 14px;
            border: 1px solid #1F2937;
            font-size: 13px;
        }

        /* =============================================
           SPINNER
           ============================================= */

        .stSpinner > div {
            border-top-color: #00D4FF !important;
        }

        /* =============================================
           CAPTION / SMALL TEXT
           ============================================= */

        .stCaption, [data-testid="stCaptionContainer"] {
            color: #64748B !important;
        }
    </style>
    """, unsafe_allow_html=True)
