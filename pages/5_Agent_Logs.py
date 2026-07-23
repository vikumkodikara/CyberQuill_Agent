"""
CyberQuill — Agent Logs Page (Debug Mode Only)
=================================================

Displays the structured log file from the CyberQuill pipeline.
Allows filtering by log level and agent name with auto-refresh.

This page is only visible in Debug Mode.
"""

import streamlit as st
from pathlib import Path
from utils.theme import render_page_header, render_sidebar_controls
from utils.helpers import is_magazine_mode

st.set_page_config(page_title="Agent Logs — CyberQuill", page_icon="📋", layout="wide")

render_sidebar_controls()

# Gate: Debug Mode only
if is_magazine_mode():
    st.info("🔒 This page is available in **Debug Mode** only. Enable Debug Mode from the sidebar toggle.")
    st.stop()

render_page_header(
    title="Agent Observability & Logs",
    subtitle="Monitor real-time pipeline execution, agent state transitions, and structured debug telemetry.",
    icon="📋"
)

# ============================================
# Log File Path
# ============================================

LOG_FILE = Path("logs/cyberquill.log")

# ============================================
# Controls Header
# ============================================

col_refresh, col_clear, col_lines = st.columns([1, 1, 2])

with col_refresh:
    if st.button("🔄 Refresh Logs", use_container_width=True):
        st.rerun()

with col_clear:
    if st.button("🗑️ Clear Logs", use_container_width=True):
        try:
            LOG_FILE.write_text("")
            st.success("Logs cleared successfully.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to clear log file: {e}")

with col_lines:
    max_lines = st.slider("Max Log Lines", 50, 500, 200, step=50)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# Filters
# ============================================

st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-bottom:1rem;'>🔎 Filter Telemetry</h4>", unsafe_allow_html=True)

col_level, col_agent = st.columns(2)

with col_level:
    level_filter = st.multiselect(
        "Filter by Log Level",
        options=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=["INFO", "WARNING", "ERROR"],
    )

with col_agent:
    agent_filter = st.text_input(
        "Filter by Agent or Module",
        placeholder="e.g. collector, duplicate, classifier, rag, writer, reviewer",
    )

# ============================================
# Log Display
# ============================================

if not LOG_FILE.exists():
    st.info(
        "📭 No log stream detected. Run the pipeline from **Publish Issue** page to generate real-time logs.\n\n"
        f"Target log path: `{LOG_FILE.resolve()}`"
    )
    st.stop()

try:
    lines = LOG_FILE.read_text(encoding="utf-8").strip().split("\n")
except Exception as e:
    st.error(f"Failed to read log file: {e}")
    st.stop()

if not lines or (len(lines) == 1 and not lines[0].strip()):
    st.info("Log stream is currently empty. Execute the pipeline to capture telemetry.")
    st.stop()

# Apply filters
filtered_lines = []
for line in lines:
    if level_filter:
        if not any(f"| {level}" in line for level in level_filter):
            continue

    if agent_filter:
        if agent_filter.lower() not in line.lower():
            continue

    filtered_lines.append(line)

display_lines = filtered_lines[-max_lines:]

st.caption(f"Displaying **{len(display_lines)}** of **{len(filtered_lines)}** filtered events ({len(lines)} total in log file)")

# Terminal container
log_html = []
for line in display_lines:
    if "| ERROR" in line:
        color = "#f87171"
        bg = "rgba(239, 68, 68, 0.1)"
    elif "| WARNING" in line:
        color = "#fbbf24"
        bg = "rgba(245, 158, 11, 0.08)"
    elif "| DEBUG" in line:
        color = "#94a3b8"
        bg = "transparent"
    else:
        color = "#38bdf8"
        bg = "transparent"

    escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    log_html.append(f'<div style="color:{color}; background:{bg}; font-family:\'Courier New\', monospace; font-size:0.83rem; padding:4px 8px; border-radius:4px; margin-bottom:2px; border-bottom:1px solid rgba(255,255,255,0.03);">{escaped}</div>')

st.markdown(
    f'<div style="background:#090d16; padding:1.25rem; border-radius:14px; max-height:550px; overflow-y:auto; border:1px solid #1e293b; box-shadow:0 10px 30px rgba(0,0,0,0.3);">{"".join(log_html)}</div>',
    unsafe_allow_html=True,
)

# ============================================
# Log Statistics
# ============================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h4 style='font-family:\"Space Grotesk\", sans-serif; font-weight:700; margin-bottom:1rem;'>📊 Telemetry Statistics</h4>", unsafe_allow_html=True)

level_counts = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0}
for line in lines:
    for level in level_counts:
        if f"| {level}" in line:
            level_counts[level] += 1
            break

c1, c2, c3, c4 = st.columns(4)
c1.metric("ℹ️ Info", level_counts["INFO"])
c2.metric("⚠️ Warning", level_counts["WARNING"])
c3.metric("❌ Error", level_counts["ERROR"])
c4.metric("🐛 Debug", level_counts["DEBUG"])
