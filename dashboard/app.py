import sys
from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


# ============================================================
# PATH SETUP
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.feature_engineering import create_features
from src.kpi_calculations import calculate_all_kpis
from src.bottleneck_analysis import prepare_bottleneck_analysis


DATA_PATH = ROOT_DIR / "data" / "processed" / "uac_cleaned.csv"
STYLES_PATH = Path(__file__).resolve().parent / "styles.css"

from components import (
    kpi_card,
    section_header,
    insight_card,
    status_badge,
    chart_container,
    footer,
    render_html,
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="UAC Care Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# THEME
# ============================================================
# All colors live in CSS variables. styles.css is the single
# source of truth for every component's look; the only thing
# that changes between Dark/Light is the variable values below.

THEMES = {
    "Dark": {
        "--bg-app": "#0b1120",
        "--bg-sidebar": "#111827",
        "--bg-card": "#111827",
        "--border-color": "#263244",
        "--text-primary": "#f8fafc",
        "--text-secondary": "#94a3b8",
        "--text-muted": "#64748b",
        "--accent": "#42a5f5",
        "--header-gradient-start": "#0c3a6b",
        "--header-gradient-mid": "#1565c0",
        "--header-gradient-end": "#0b1120",
        "--header-text": "#ffffff",
        "--header-subtext": "#dbeafe",
    },
    "Light": {
        "--bg-app": "#f4f6fb",
        "--bg-sidebar": "#ffffff",
        "--bg-card": "#ffffff",
        "--border-color": "#e2e8f0",
        "--text-primary": "#0f172a",
        "--text-secondary": "#475569",
        "--text-muted": "#94a3b8",
        "--accent": "#1d4ed8",
        "--header-gradient-start": "#bfdbfe",
        "--header-gradient-mid": "#60a5fa",
        "--header-gradient-end": "#f4f6fb",
        "--header-text": "#0b1120",
        "--header-subtext": "#1e3a5f",
    },
}


def build_theme_css(theme_name):
    """Build the full <style> block: theme variables + static stylesheet."""

    variables = THEMES.get(theme_name, THEMES["Dark"])
    root_block = ":root {\n" + "\n".join(
        f"    {key}: {value};" for key, value in variables.items()
    ) + "\n}\n"

    stylesheet = STYLES_PATH.read_text()

    return f"<style>\n{root_block}\n{stylesheet}\n</style>"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(DATA_PATH)

    df["date"] = pd.to_datetime(df["date"])

    numeric_columns = [
        "apprehended",
        "cbp_custody",
        "transferred",
        "hhs_care",
        "discharged"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = create_features(df)
    df = prepare_bottleneck_analysis(df)

    return df


try:
    df = load_data()

except Exception as e:

    st.error(
        f"Unable to load project data.\n\n"
        f"Expected file:\n`{DATA_PATH}`\n\n"
        f"Error: {e}"
    )

    st.stop()


min_date = df["date"].min().date()
max_date = df["date"].max().date()

METRIC_OPTIONS = [
    "Transfer Efficiency",
    "Discharge Effectiveness",
    "CBP Net Pressure",
    "HHS Net Pressure"
]


# ============================================================
# SESSION STATE DEFAULTS + RESET HANDLING
# ============================================================
# Widgets below are bound via `key=`. To reset them we must set
# st.session_state BEFORE the widgets are instantiated, then rerun.

if "theme_choice" not in st.session_state:
    st.session_state.theme_choice = "Dark"

if "date_range_filter" not in st.session_state:
    st.session_state.date_range_filter = (min_date, max_date)

if "chart_metric_filter" not in st.session_state:
    st.session_state.chart_metric_filter = METRIC_OPTIONS[0]

if st.session_state.get("_do_reset", False):
    st.session_state.date_range_filter = (min_date, max_date)
    st.session_state.chart_metric_filter = METRIC_OPTIONS[0]
    st.session_state.theme_choice = "Dark"
    st.session_state._do_reset = False


# Inject theme CSS (must happen after we know the current theme choice)
render_html(build_theme_css(st.session_state.theme_choice))


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html("""
        <div class="sidebar-brand-title">🏥 CareFlow</div>
        <div class="sidebar-brand-subtitle">UAC Program Analytics</div>
        """)

    st.markdown("### Dashboard Controls")

    date_range = st.date_input(
        "Analysis Period",
        min_value=min_date,
        max_value=max_date,
        key="date_range_filter"
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:

        start_date, end_date = date_range

        filtered_df = df[
            (df["date"].dt.date >= start_date)
            &
            (df["date"].dt.date <= end_date)
        ].copy()

    else:

        filtered_df = df.copy()

    if st.button("↺ Reset Filters", use_container_width=True):
        st.session_state._do_reset = True
        st.rerun()

    st.markdown("---")

    st.markdown("### Display")

    chart_metric = st.selectbox(
        "Trend Metric",
        METRIC_OPTIONS,
        key="chart_metric_filter"
    )

    st.markdown("---")

    st.markdown("### Theme")

    theme_choice = st.radio(
        "Appearance",
        list(THEMES.keys()),
        key="theme_choice",
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("---")

    render_html("""
        <div class="sidebar-footnote">
            Data source: UAC Program dataset<br>
            Analysis: Care Transition Efficiency<br>
            Reporting period: 2023-2025
        </div>
        """)


# ============================================================
# HEADER
# ============================================================

render_html("""
    <div class="dashboard-header">
        <h1>UAC Care Transition Efficiency & Placement Analytics</h1>
        <p>
            CBP &rarr; HHS Transfer Monitoring
            &nbsp; &bull; &nbsp;
            Care Pipeline
            &nbsp; &bull; &nbsp;
            Discharge Outcomes
            &nbsp; &bull; &nbsp;
            Operational Pressure
        </p>
    </div>
    """)


# ============================================================
# FILTER INFO
# ============================================================

st.caption(
    f"Showing {len(filtered_df):,} reporting observations "
    f"from {filtered_df['date'].min().strftime('%d %b %Y')} "
    f"to {filtered_df['date'].max().strftime('%d %b %Y')}."
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

kpis = calculate_all_kpis(filtered_df)


def format_number(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:,.0f}"


def format_percent(value):

    if pd.isna(value):
        return "N/A"

    return f"{value * 100:.1f}%"


# ============================================================
# KPI CARDS
# ============================================================

section_header(
    "Executive Performance Snapshot",
    "Key indicators for the selected reporting period"
)


kpi_cols = st.columns(6)

with kpi_cols[0]:
    kpi_card(
        "Total Apprehended",
        f"{kpis['total_apprehended']:,}",
        "Children entering CBP custody"
    )

with kpi_cols[1]:
    kpi_card(
        "Total Transferred",
        f"{kpis['total_transferred']:,}",
        "CBP → HHS transfers"
    )

with kpi_cols[2]:
    kpi_card(
        "Total Discharged",
        f"{kpis['total_discharged']:,}",
        "Children discharged from HHS"
    )

with kpi_cols[3]:
    kpi_card(
        "Transfer Efficiency",
        f"{kpis['transfer_efficiency']:.1%}",
        "Transfers / CBP custody"
    )

with kpi_cols[4]:
    kpi_card(
        "Discharge Effectiveness",
        f"{kpis['discharge_effectiveness']:.1%}",
        "Discharges / HHS care"
    )

with kpi_cols[5]:
    kpi_card(
        "Pipeline Throughput",
        f"{kpis['pipeline_throughput']:.1%}",
        "Discharges / apprehensions"
    )


# ============================================================
# TABS
# ============================================================

tabs = st.tabs(
    [
        "📊 Overview",
        "🔄 Transfers",
        "🏠 Discharges",
        "⚠️ Bottlenecks",
        "📅 Temporal",
        "💡 Insights"
    ]
)


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================

with tabs[0]:

    section_header(
        "Care Pipeline Overview",
        "Aggregate activity across the UAC care transition process"
    )

    col1, col2 = st.columns([1, 1.4])

    # ---------- PIPELINE ----------

    with col1:

        pipeline_values = [
            filtered_df["apprehended"].sum(),
            filtered_df["transferred"].sum(),
            filtered_df["discharged"].sum()
        ]

        pipeline_labels = [
            "Apprehended",
            "Transferred",
            "Discharged"
        ]

        fig = go.Figure(
            go.Funnel(
                y=pipeline_labels,
                x=pipeline_values,
                textinfo="value+percent initial"
            )
        )

        fig.update_layout(
            title="Aggregate Care Pipeline",
            template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
            height=420,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    # ---------- ACTIVITY ----------

    with col2:

        monthly = (
            filtered_df
            .set_index("date")
            .resample("ME")[
                ["apprehended", "transferred", "discharged"]
            ]
            .sum()
            .reset_index()
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=monthly["date"],
                y=monthly["apprehended"],
                mode="lines+markers",
                name="Apprehended"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=monthly["date"],
                y=monthly["transferred"],
                mode="lines+markers",
                name="Transferred"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=monthly["date"],
                y=monthly["discharged"],
                mode="lines+markers",
                name="Discharged"
            )
        )

        fig.update_layout(
            title="Monthly Care Activity",
            template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
            height=420,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    # ---------- PRESSURE ----------

    chart_container("Operational Pressure")

    pressure_monthly = (
        filtered_df
        .set_index("date")
        .resample("ME")[
            ["cbp_net_pressure", "hhs_net_pressure"]
        ]
        .mean()
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=pressure_monthly["date"],
            y=pressure_monthly["cbp_net_pressure"],
            name="CBP Net Pressure"
        )
    )

    fig.add_trace(
        go.Bar(
            x=pressure_monthly["date"],
            y=pressure_monthly["hhs_net_pressure"],
            name="HHS Net Pressure"
        )
    )

    fig.add_hline(y=0, line_width=1)

    fig.update_layout(
        template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
        height=360,
        barmode="group",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------- FILTERED DATASET (lives only on Overview) ----------

    chart_container(
        "Filtered Dataset",
        "The raw reporting rows behind the charts above, for the selected date range"
    )

    display_columns = [
        "date",
        "apprehended",
        "cbp_custody",
        "transferred",
        "hhs_care",
        "discharged",
        "transfer_efficiency",
        "discharge_effectiveness",
        "cbp_net_pressure",
        "hhs_net_pressure"
    ]

    with st.expander("🔎 View Filtered Dataset", expanded=False):

        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

        csv = filtered_df[display_columns].to_csv(index=False)

        st.download_button(
            label="⬇️ Download Filtered CSV",
            data=csv,
            file_name="uac_filtered_analysis.csv",
            mime="text/csv"
        )


# ============================================================
# TAB 2 — TRANSFERS
# ============================================================

with tabs[1]:

    section_header(
        "CBP → HHS Transfer Analysis",
        "Monitoring transfer activity and transfer efficiency"
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=filtered_df["date"],
                y=filtered_df["cbp_custody"],
                mode="lines",
                name="CBP Custody"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=filtered_df["date"],
                y=filtered_df["transferred"],
                mode="lines",
                name="Transferred"
            )
        )

        fig.update_layout(
            title="CBP Custody vs Transfers",
            template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
            height=400,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=filtered_df["date"],
                y=filtered_df["transfer_efficiency"] * 100,
                mode="lines",
                name="Transfer Efficiency"
            )
        )

        fig.update_layout(
            title="Transfer Efficiency Trend",
            yaxis_title="Efficiency (%)",
            template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
            height=400,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

    chart_container("CBP Operational Pressure")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtered_df["date"],
            y=filtered_df["cbp_net_pressure"],
            mode="lines",
            name="CBP Net Pressure"
        )
    )

    fig.add_hline(y=0)

    fig.update_layout(
        template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
        height=350,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 3 — DISCHARGES
# ============================================================

with tabs[2]:

    section_header(
        "HHS Discharge Analysis",
        "Monitoring HHS care population and discharge activity"
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=filtered_df["date"],
                y=filtered_df["hhs_care"],
                mode="lines",
                name="Children in HHS Care"
            )
        )

        fig.update_layout(
            title="Children in HHS Care",
            template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
            height=400,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=filtered_df["date"],
                y=filtered_df["discharged"],
                mode="lines+markers",
                name="Discharged"
            )
        )

        fig.update_layout(
            title="Discharge Activity",
            template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
            height=400,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtered_df["date"],
            y=filtered_df["discharge_effectiveness"] * 100,
            mode="lines",
            name="Discharge Effectiveness"
        )
    )

    fig.update_layout(
        title="Discharge Effectiveness Trend",
        yaxis_title="Effectiveness (%)",
        template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
        height=350,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 4 — BOTTLENECKS
# ============================================================

with tabs[3]:

    section_header(
        "Bottleneck & Pressure Analysis",
        "Identifying periods of elevated operational pressure"
    )

    cbp_threshold = filtered_df["cbp_net_pressure"].quantile(0.75)
    hhs_threshold = filtered_df["hhs_net_pressure"].quantile(0.75)

    col1, col2 = st.columns(2)

    with col1:

        st.metric("CBP High-Pressure Threshold", f"{cbp_threshold:.1f}")

        cbp_high = filtered_df[
            filtered_df["cbp_net_pressure"] >= cbp_threshold
        ]

        st.metric("High-Pressure CBP Observations", f"{len(cbp_high):,}")

    with col2:

        st.metric("HHS High-Pressure Threshold", f"{hhs_threshold:.1f}")

        hhs_high = filtered_df[
            filtered_df["hhs_net_pressure"] >= hhs_threshold
        ]

        st.metric("High-Pressure HHS Observations", f"{len(hhs_high):,}")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtered_df["date"],
            y=filtered_df["cbp_net_pressure"],
            mode="lines",
            name="CBP Pressure"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=filtered_df["date"],
            y=filtered_df["hhs_net_pressure"],
            mode="lines",
            name="HHS Pressure"
        )
    )

    fig.add_hline(y=0)

    fig.update_layout(
        title="CBP and HHS Operational Pressure",
        template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
        height=430,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    chart_container("Highest Pressure Reporting Periods")

    pressure_table = filtered_df[
        [
            "date",
            "cbp_net_pressure",
            "hhs_net_pressure"
        ]
    ].copy()

    pressure_table["combined_pressure"] = (
        pressure_table["cbp_net_pressure"]
        + pressure_table["hhs_net_pressure"]
    )

    pressure_table = (
        pressure_table
        .sort_values("combined_pressure", ascending=False)
        .head(10)
    )

    pressure_table = pressure_table.rename(
        columns={
            "date": "Date",
            "cbp_net_pressure": "CBP Pressure",
            "hhs_net_pressure": "HHS Pressure",
            "combined_pressure": "Combined Pressure"
        }
    )

    st.dataframe(pressure_table, use_container_width=True, hide_index=True)


# ============================================================
# TAB 5 — TEMPORAL
# ============================================================

with tabs[4]:

    section_header(
        "Temporal Analysis",
        "Monthly, yearly and reporting-day patterns"
    )

    monthly = (
        filtered_df
        .set_index("date")
        .resample("ME")[
            ["transferred", "discharged"]
        ]
        .sum()
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["date"],
            y=monthly["transferred"],
            mode="lines+markers",
            name="Transferred"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["date"],
            y=monthly["discharged"],
            mode="lines+markers",
            name="Discharged"
        )
    )

    fig.update_layout(
        title="Monthly Transfers vs Discharges",
        template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
        height=400,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    yearly = (
        filtered_df
        .groupby("year")[
            ["apprehended", "transferred", "discharged"]
        ]
        .sum()
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(x=yearly["year"], y=yearly["apprehended"], name="Apprehended"))
    fig.add_trace(go.Bar(x=yearly["year"], y=yearly["transferred"], name="Transferred"))
    fig.add_trace(go.Bar(x=yearly["year"], y=yearly["discharged"], name="Discharged"))

    fig.update_layout(
        title="Year-over-Year Activity",
        template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
        height=400,
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)

    weekday_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]

    weekday = (
        filtered_df
        .groupby("day_of_week")[
            ["transferred", "discharged"]
        ]
        .mean()
        .reindex(weekday_order)
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(x=weekday["day_of_week"], y=weekday["transferred"], name="Average Transfers"))
    fig.add_trace(go.Bar(x=weekday["day_of_week"], y=weekday["discharged"], name="Average Discharges"))

    fig.update_layout(
        title="Average Activity by Reporting Day",
        template="plotly_dark" if theme_choice == "Dark" else "plotly_white",
        height=400,
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 6 — INSIGHTS
# ============================================================

with tabs[5]:

    section_header(
        "Executive Insights",
        "Data-driven observations from the selected reporting period"
    )

    transfer_eff = kpis["transfer_efficiency"]
    discharge_eff = kpis["discharge_effectiveness"]
    avg_cbp = kpis["average_cbp_pressure"]
    avg_hhs = kpis["average_hhs_pressure"]

    # ---------- Insight 1 — Transfer ----------

    transfer_level = "success" if transfer_eff >= 0.75 else "warning" if transfer_eff >= 0.5 else "danger"

    insight_card(
        "Transfer Performance",
        f"The aggregate transfer efficiency for the selected period is "
        f"<b>{transfer_eff * 100:.1f}%</b>. This indicator compares total "
        f"transfers with total reported CBP custody observations.",
        icon="🔄",
        level=transfer_level
    )

    # ---------- Insight 2 — Discharge ----------

    discharge_level = "success" if discharge_eff >= 0.75 else "warning" if discharge_eff >= 0.5 else "danger"

    insight_card(
        "Discharge Activity",
        f"Aggregate discharge effectiveness is <b>{discharge_eff * 100:.1f}%</b>. "
        f"This measures discharge activity relative to reported children in HHS care.",
        icon="🏠",
        level=discharge_level
    )

    # ---------- Insight 3 — CBP Pressure ----------

    if avg_cbp > 0:
        cbp_message = (
            "CBP shows positive average net pressure, indicating that reported "
            "apprehension activity exceeded reported transfers during the "
            "selected observations."
        )
        cbp_level = "warning"
    else:
        cbp_message = (
            "CBP shows non-positive average net pressure, meaning reported "
            "transfers were at or above apprehension activity on average."
        )
        cbp_level = "success"

    insight_card(
        "CBP Operational Pressure",
        f"Average CBP net pressure is <b>{avg_cbp:.1f}</b> children. {cbp_message}",
        icon="⚠️",
        level=cbp_level
    )

    # ---------- Insight 4 — HHS Pressure ----------

    if avg_hhs > 0:
        hhs_message = (
            "Positive HHS pressure indicates that reported transfers exceeded "
            "reported discharges during the selected observations."
        )
        hhs_level = "warning"
    else:
        hhs_message = (
            "HHS pressure is non-positive on average, indicating reported "
            "discharge activity was at or above transfers."
        )
        hhs_level = "success"

    insight_card(
        "HHS Operational Pressure",
        f"Average HHS net pressure is <b>{avg_hhs:.1f}</b> children. {hhs_message}",
        icon="🏥",
        level=hhs_level
    )

    # ---------- Methodology ----------

    section_header("Interpretation & Limitations")

    render_html("""
        <div class="info-card">

        <b>Transfer Efficiency</b><br>
        Calculated as reported transfers divided by reported CBP
        custody observations. It is an operational activity ratio,
        not a direct measurement of transfer processing time.

        <br><br>

        <b>Discharge Effectiveness</b><br>
        Calculated as reported discharges divided by reported
        children in HHS care. It describes aggregate discharge
        activity and should not be interpreted as individual
        reunification success.

        <br><br>

        <b>Operational Pressure</b><br>
        CBP pressure is calculated as apprehensions minus transfers.
        HHS pressure is calculated as transfers minus discharges.
        These measures indicate directional operational pressure,
        not necessarily literal physical backlog.

        <br><br>

        <b>Reporting Frequency</b><br>
        The dataset contains uneven reporting intervals. Missing
        dates should therefore not be interpreted as zero activity.

        </div>
        """)


# ============================================================
# FOOTER
# ============================================================

footer(name="Mahi Ahalawat")