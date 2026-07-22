"""
CyberQuill — Agent Logs Page
===============================

Displays the structured log file from the CyberQuill pipeline.
Allows filtering by log level and agent name with auto-refresh.
"""

import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Agent Logs — CyberQuill", page_icon="📋", layout="wide")

st.title("📋 Agent Logs")
st.markdown("Monitor pipeline execution and debug agent behaviour.")
st.divider()


# ============================================
# Log File Path
# ============================================

LOG_FILE = Path("logs/cyberquill.log")


# ============================================
# Controls
# ============================================

col_refresh, col_clear, col_lines = st.columns([1, 1, 2])

with col_refresh:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

with col_clear:
    if st.button("🗑️ Clear Logs", use_container_width=True):
        try:
            LOG_FILE.write_text("")
            st.success("Logs cleared.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to clear logs: {e}")

with col_lines:
    max_lines = st.slider("Lines to show", 50, 500, 200, step=50)


# ============================================
# Filters
# ============================================

col_level, col_agent = st.columns(2)

with col_level:
    level_filter = st.multiselect(
        "Filter by log level",
        options=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=["INFO", "WARNING", "ERROR"],
    )

with col_agent:
    agent_filter = st.text_input(
        "Filter by agent/module",
        placeholder="e.g. collector, classifier, rag",
    )


# ============================================
# Log Display
# ============================================

if not LOG_FILE.exists():
    st.info(
        "📭 No log file found. Run the pipeline to generate logs.\n\n"
        f"Expected path: `{LOG_FILE.resolve()}`"
    )
    st.stop()

try:
    lines = LOG_FILE.read_text(encoding="utf-8").strip().split("\n")
except Exception as e:
    st.error(f"Failed to read log file: {e}")
    st.stop()

if not lines or (len(lines) == 1 and not lines[0].strip()):
    st.info("Log file is empty. Run the pipeline to generate logs.")
    st.stop()

# Apply filters
filtered_lines = []
for line in lines:
    # Level filter
    if level_filter:
        if not any(f"| {level}" in line for level in level_filter):
            continue

    # Agent filter
    if agent_filter:
        if agent_filter.lower() not in line.lower():
            continue

    filtered_lines.append(line)

# Show latest lines (tail)
display_lines = filtered_lines[-max_lines:]

st.caption(
    f"Showing {len(display_lines)} of {len(filtered_lines)} filtered lines "
    f"({len(lines)} total)"
)

# Colour-coded log display
log_html = []
for line in display_lines:
    if "| ERROR" in line:
        color = "#e53935"
    elif "| WARNING" in line:
        color = "#f57c00"
    elif "| DEBUG" in line:
        color = "#9e9e9e"
    else:
        color = "#333"

    escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    log_html.append(f'<div style="color:{color};font-family:monospace;font-size:0.82rem;'
                    f'padding:2px 0;border-bottom:1px solid #f0f0f0">{escaped}</div>')

st.markdown(
    f'<div style="background:#fafafa;padding:1rem;border-radius:8px;'
    f'max-height:600px;overflow-y:auto">{"".join(log_html)}</div>',
    unsafe_allow_html=True,
)


# ============================================
# Log Statistics
# ============================================

st.divider()
st.subheader("📊 Log Statistics")

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
