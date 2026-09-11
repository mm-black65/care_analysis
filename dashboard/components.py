import textwrap

import streamlit as st


def render_html(html):
    """
    Render HTML safely inside Streamlit.

    Removes all leading indentation from HTML lines so Streamlit
    does not interpret nested HTML as a Markdown code block.
    """
    html = textwrap.dedent(html).strip()

    # Remove remaining indentation from nested/interpolated HTML
    html = "\n".join(line.lstrip() for line in html.splitlines())

    st.markdown(html, unsafe_allow_html=True)

def kpi_card(title, value, subtitle="", status=None):
    """Display a dashboard KPI card."""

    status_html = ""

    if status:
        status_html = f'<div class="kpi-status">{status}</div>'

    render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtitle">{subtitle}</div>
            {status_html}
        </div>
        """)


def section_header(title, subtitle=None):
    """Display a section heading."""

    subtitle_html = ""

    if subtitle:
        subtitle_html = f'<div class="section-subtitle">{subtitle}</div>'

    render_html(f"""
        <div class="section-header">
            <div class="section-title">{title}</div>
            {subtitle_html}
        </div>
        """)


def insight_card(title, message, icon="💡", level="info", recommendation=None):
    """Display an analytical insight card.

    level: one of "info", "success", "warning", "danger" - controls the
    accent color of the left border.
    recommendation: optional action-oriented follow-up shown beneath the
    observation, visually separated so it reads as "what to do about it".
    """

    recommendation_html = ""

    if recommendation:
        recommendation_html = (
            f'<div class="insight-recommendation">'
            f'<span class="insight-recommendation-label">Recommendation:</span> '
            f'{recommendation}</div>'
        )

    render_html(f"""
        <div class="insight-card {level}">
            <div class="insight-icon">{icon}</div>
            <div>
                <div class="insight-title">{title}</div>
                <div class="insight-message">{message}</div>
                {recommendation_html}
            </div>
        </div>
        """)


def status_badge(text, status="normal"):
    """Display a small status badge."""

    render_html(f'<span class="status-badge {status}">{text}</span>')


def chart_container(title, subtitle=None):
    """Start a styled chart section."""

    subtitle_html = ""

    if subtitle:
        subtitle_html = f'<div class="chart-subtitle">{subtitle}</div>'

    render_html(f"""
        <div class="chart-header">
            <div class="chart-title">{title}</div>
            {subtitle_html}
        </div>
        """)


def footer(name="Mahi Ahalawat"):
    """Dashboard footer."""

    render_html(f"""
        <div class="dashboard-footer">
            <div><strong>UAC Care Transition Analytics</strong></div>
            <div>
                Data-driven monitoring of care transitions,
                operational pressure and discharge activity
            </div>
            <div style="margin-top:8px;">
                Built by <strong>{name}</strong>
            </div>
        </div>
        """)