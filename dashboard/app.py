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
        "--input-bg": "#0f172a",
        "--input-text": "#f8fafc",
        "--input-border": "#334155",
    },
    "Cosmic": {
        "--bg-app": "#0a0a1f",
        "--bg-sidebar": "#12102b",
        "--bg-card": "#181435",
        "--border-color": "#3a2f6e",
        "--text-primary": "#f3f0ff",
        "--text-secondary": "#c4b5fd",
        "--text-muted": "#8b7ec9",
        "--accent": "#c084fc",
        "--header-gradient-start": "#1e1147",
        "--header-gradient-mid": "#8b5cf6",
        "--header-gradient-end": "#0a0a1f",
        "--header-text": "#ffffff",
        "--header-subtext": "#e9d5ff",
        "--input-bg": "#1a1640",
        "--input-text": "#f3f0ff",
        "--input-border": "#4c3a8c",
        "--bg-pattern": (
            "radial-gradient(1.5px 1.5px at 20px 30px, #ffffff77, transparent), "
            "radial-gradient(2px 2px at 140px 80px, #ffffff55, transparent), "
            "radial-gradient(1.2px 1.2px at 90px 160px, #ffffff44, transparent), "
            "radial-gradient(1.8px 1.8px at 200px 220px, #ffffff66, transparent), "
            "radial-gradient(1.2px 1.2px at 50px 200px, #ffffff44, transparent), "
            "radial-gradient(1.5px 1.5px at 230px 40px, #ffffff55, transparent)"
        ),
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

    st.markdown("### Theme")

    theme_choice = st.radio(
        "Appearance",
        list(THEMES.keys()),
        key="theme_choice",
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("---")

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
            template="plotly_dark",
            height=420,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "📌 Each stage narrows compared to the one before it — a bigger drop "
            "between two stages means more attrition happens there."
        )

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
            template="plotly_dark",
            height=420,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "📌 Lines moving together mean the pipeline is keeping pace; "
            "lines pulling apart signal a bottleneck forming at that stage."
        )

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
        template="plotly_dark",
        height=360,
        barmode="group",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "📌 Bars above zero mean intake is outpacing outflow at that stage; "
        "bars below zero mean the pipeline is clearing faster than it fills."
    )

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
                name="CBP Custody",
                line=dict(color="#38bdf8")
            )
        )

        fig.add_trace(
            go.Scatter(
                x=filtered_df["date"],
                y=filtered_df["transferred"],
                mode="lines",
                name="Transferred",
                line=dict(color="#f59e0b")
            )
        )

        fig.update_layout(
            title="CBP Custody vs Transfers",
            template="plotly_dark",
            height=400,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "📌 A widening gap between the two lines means children are "
            "entering custody faster than they're being transferred out."
        )

    with col2:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=filtered_df["date"],
                y=filtered_df["transfer_efficiency"] * 100,
                mode="lines",
                name="Transfer Efficiency",
                line=dict(color="#34d399")
            )
        )

        fig.update_layout(
            title="Transfer Efficiency Trend",
            yaxis_title="Efficiency (%)",
            template="plotly_dark",
            height=400,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "📌 Higher and steadier is better — dips point to periods where "
            "transfers out of CBP custody slowed down."
        )

    # ---------- TRANSFER EFFICIENCY DISTRIBUTION ----------

    chart_container(
        "Transfer Efficiency Distribution",
        "Distribution of reporting-period transfer efficiency values"
    )

    efficiency_data = filtered_df["transfer_efficiency"].dropna() * 100

    if len(efficiency_data) > 0:

        fig = go.Figure()

        fig.add_trace(
            go.Histogram(
                x=efficiency_data,
                nbinsx=25,
                name="Transfer Efficiency",
                marker=dict(color="#a78bfa")
            )
        )

        fig.update_layout(
            title="Distribution of Transfer Efficiency",
            xaxis_title="Transfer Efficiency (%)",
            yaxis_title="Number of Reporting Periods",
            template="plotly_dark",
            height=360,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="transfer_efficiency_distribution"
        )

        st.caption(
            "📌 A cluster toward the right means most periods performed well; "
            "a cluster toward the left signals a persistent efficiency problem."
        )

    else:
        st.warning("No transfer efficiency data available for the selected period.")

    # ---------- CBP OPERATIONAL PRESSURE ----------

    chart_container("CBP Operational Pressure")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtered_df["date"],
            y=filtered_df["cbp_net_pressure"],
            mode="lines",
            name="CBP Net Pressure",
            line=dict(color="#14b8a6")
        )
    )

    fig.add_hline(y=0)

    fig.update_layout(
        template="plotly_dark",
        height=350,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True, key="cbp_operational_pressure")

    st.caption(
        "📌 Positive values mean apprehensions are outpacing transfers, building "
        "custody backlog; negative values mean CBP is clearing custody faster than it fills."
    )


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
                name="Children in HHS Care",
                line=dict(color="#8b5cf6")
            )
        )

        fig.update_layout(
            title="Children in HHS Care",
            template="plotly_dark",
            height=400,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "📌 Sustained growth here signals rising placement demand on HHS."
        )

    with col2:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=filtered_df["date"],
                y=filtered_df["discharged"],
                mode="lines+markers",
                name="Discharged",
                line=dict(color="#f59e0b")
            )
        )

        fig.update_layout(
            title="Discharge Activity",
            template="plotly_dark",
            height=400,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "📌 Should rise and fall in step with the HHS care population on the left."
        )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtered_df["date"],
            y=filtered_df["discharge_effectiveness"] * 100,
            mode="lines",
            name="Discharge Effectiveness",
            line=dict(color="#22c55e")
        )
    )

    fig.update_layout(
        title="Discharge Effectiveness Trend",
        yaxis_title="Effectiveness (%)",
        template="plotly_dark",
        height=350,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "📌 A declining trend here suggests placement or sponsor-vetting delays "
        "are slowing discharges relative to the care population."
    )


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
            name="CBP Pressure",
            line=dict(color="#38bdf8")
        )
    )

    fig.add_trace(
        go.Scatter(
            x=filtered_df["date"],
            y=filtered_df["hhs_net_pressure"],
            mode="lines",
            name="HHS Pressure",
            line=dict(color="#f59e0b")
        )
    )

    fig.add_hline(y=0)

    fig.update_layout(
        title="CBP and HHS Operational Pressure",
        template="plotly_dark",
        height=430,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True, key="bottleneck_pressure_chart")

    st.caption(
        "📌 Whichever line sits further from zero for longer is the bigger "
        "current bottleneck — CBP intake or HHS discharge."
    )

    # ---------- MONTHLY TRANSFER-DISCHARGE GAP ----------

    chart_container(
        "Monthly Transfer–Discharge Gap",
        "Positive values indicate more transfers than discharges"
    )

    gap_monthly = (
        filtered_df
        .set_index("date")
        .resample("ME")[["transferred", "discharged"]]
        .sum()
        .reset_index()
    )

    gap_monthly["net_gap"] = (
        gap_monthly["transferred"]
        - gap_monthly["discharged"]
    )

    if len(gap_monthly) > 0:

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=gap_monthly["date"],
                y=gap_monthly["net_gap"],
                name="Net Gap",
                marker=dict(color="#a78bfa")
            )
        )

        fig.add_hline(
            y=0,
            line_width=1
        )

        fig.update_layout(
            title="Monthly Transfer–Discharge Gap",
            xaxis_title="Month",
            yaxis_title="Transfers − Discharges",
            template="plotly_dark",
            height=380,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="bottleneck_monthly_gap"
        )

        st.caption(
            "📌 Positive bars mean more children were transferred into HHS care "
            "than discharged that month, adding to backlog; negative bars mean "
            "HHS discharged faster than it received."
        )

    else:
        st.warning("No monthly data available for the selected period.")

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

    st.caption(
        "📌 Ranked by combined CBP + HHS pressure — these periods would "
        "benefit most from a root-cause review."
    )


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
            name="Transferred",
            line=dict(color="#f59e0b")
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["date"],
            y=monthly["discharged"],
            mode="lines+markers",
            name="Discharged",
            line=dict(color="#34d399")
        )
    )

    fig.update_layout(
        title="Monthly Transfers vs Discharges",
        template="plotly_dark",
        height=400,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True, key="temporal_monthly_transfers_discharges")

    st.caption(
        "📌 Recurring gaps between the two lines point to seasonal or cyclical "
        "capacity mismatches worth planning around."
    )

    # ---------- MONTHLY TRANSFER-DISCHARGE GAP ----------

    chart_container(
        "Monthly Transfer–Discharge Gap",
        "Positive values indicate more transfers than discharges"
    )

    gap_monthly = (
        filtered_df
        .set_index("date")
        .resample("ME")[["transferred", "discharged"]]
        .sum()
        .reset_index()
    )

    gap_monthly["net_gap"] = (
        gap_monthly["transferred"]
        - gap_monthly["discharged"]
    )

    if len(gap_monthly) > 0:

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=gap_monthly["date"],
                y=gap_monthly["net_gap"],
                name="Net Gap",
                marker=dict(color="#818cf8")
            )
        )

        fig.add_hline(
            y=0,
            line_width=1
        )

        fig.update_layout(
            title="Monthly Transfer–Discharge Gap",
            xaxis_title="Month",
            yaxis_title="Transfers − Discharges",
            template="plotly_dark",
            height=380,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="temporal_monthly_gap"
        )

        st.caption(
            "📌 Use this to spot whether backlog is building, shrinking, or "
            "holding steady over time."
        )

    else:
        st.warning("No monthly data available for the selected period.")

    yearly = (
        filtered_df
        .groupby("year")[
            ["apprehended", "transferred", "discharged"]
        ]
        .sum()
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(x=yearly["year"], y=yearly["apprehended"], name="Apprehended", marker_color="#38bdf8"))
    fig.add_trace(go.Bar(x=yearly["year"], y=yearly["transferred"], name="Transferred", marker_color="#f59e0b"))
    fig.add_trace(go.Bar(x=yearly["year"], y=yearly["discharged"], name="Discharged", marker_color="#34d399"))

    fig.update_layout(
        title="Year-over-Year Activity",
        template="plotly_dark",
        height=400,
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True, key="temporal_yearly_activity")

    st.caption(
        "📌 A shrinking gap between Apprehended and Discharged year over year "
        "signals improving overall throughput."
    )

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

    fig.add_trace(go.Bar(x=weekday["day_of_week"], y=weekday["transferred"], name="Average Transfers", marker_color="#a78bfa"))
    fig.add_trace(go.Bar(x=weekday["day_of_week"], y=weekday["discharged"], name="Average Discharges", marker_color="#22d3ee"))

    fig.update_layout(
        title="Average Activity by Reporting Day",
        template="plotly_dark",
        height=400,
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True, key="temporal_weekday_activity")

    st.caption(
        "📌 Highlights which reporting days see the most transfer and "
        "discharge activity — useful for staffing decisions."
    )


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

    if transfer_level == "success":
        transfer_recommendation = (
            "Performance is healthy - maintain current staffing levels and "
            "transfer protocols, and continue routine monitoring."
        )
    elif transfer_level == "warning":
        transfer_recommendation = (
            "Efficiency is below target. Review hand-off procedures and staffing "
            "at CBP custody points to close the gap toward the 75% benchmark."
        )
    else:
        transfer_recommendation = (
            "Efficiency is significantly below target. Prioritize an operational "
            "review of transfer capacity and coordination between CBP and HHS."
        )

    insight_card(
        "Transfer Performance",
        f"The aggregate transfer efficiency for the selected period is "
        f"<b>{transfer_eff * 100:.1f}%</b>. This indicator compares total "
        f"transfers with total reported CBP custody observations.",
        icon="🔄",
        level=transfer_level,
        recommendation=transfer_recommendation
    )

    # ---------- Insight 2 — Discharge ----------

    discharge_level = "success" if discharge_eff >= 0.75 else "warning" if discharge_eff >= 0.5 else "danger"

    if discharge_level == "success":
        discharge_recommendation = (
            "Discharge activity is keeping pace with HHS care volume - continue "
            "current sponsor-placement and case-processing workflows."
        )
    elif discharge_level == "warning":
        discharge_recommendation = (
            "Discharge pace is trailing HHS care volume. Consider accelerating "
            "sponsor vetting and placement reviews to reduce time in care."
        )
    else:
        discharge_recommendation = (
            "Discharge activity is well below intake volume. Recommend an urgent "
            "review of placement bottlenecks and available bed capacity."
        )

    insight_card(
        "Discharge Activity",
        f"Aggregate discharge effectiveness is <b>{discharge_eff * 100:.1f}%</b>. "
        f"This measures discharge activity relative to reported children in HHS care.",
        icon="🏠",
        level=discharge_level,
        recommendation=discharge_recommendation
    )

    # ---------- Insight 3 — CBP Pressure ----------

    if avg_cbp > 0:
        cbp_message = (
            "CBP shows positive average net pressure, indicating that reported "
            "apprehension activity exceeded reported transfers during the "
            "selected observations."
        )
        cbp_level = "warning"
        cbp_recommendation = (
            "Backlog is building at the CBP stage. Recommend evaluating transfer "
            "throughput capacity and arranging temporary surge support to relieve "
            "custody pressure."
        )
    else:
        cbp_message = (
            "CBP shows non-positive average net pressure, meaning reported "
            "transfers were at or above apprehension activity on average."
        )
        cbp_level = "success"
        cbp_recommendation = (
            "Pipeline capacity at the CBP stage is adequate - continue routine "
            "monitoring, no immediate action needed."
        )

    insight_card(
        "CBP Operational Pressure",
        f"Average CBP net pressure is <b>{avg_cbp:.1f}</b> children. {cbp_message}",
        icon="⚠️",
        level=cbp_level,
        recommendation=cbp_recommendation
    )

    # ---------- Insight 4 — HHS Pressure ----------

    if avg_hhs > 0:
        hhs_message = (
            "Positive HHS pressure indicates that reported transfers exceeded "
            "reported discharges during the selected observations."
        )
        hhs_level = "warning"
        hhs_recommendation = (
            "Care population is growing faster than discharges. Recommend "
            "expanding HHS bed capacity or accelerating sponsor placement to "
            "relieve downstream pressure."
        )
    else:
        hhs_message = (
            "HHS pressure is non-positive on average, indicating reported "
            "discharge activity was at or above transfers."
        )
        hhs_level = "success"
        hhs_recommendation = (
            "Discharge pace is keeping up with inflow - maintain current "
            "staffing and placement operations."
        )

    insight_card(
        "HHS Operational Pressure",
        f"Average HHS net pressure is <b>{avg_hhs:.1f}</b> children. {hhs_message}",
        icon="🏥",
        level=hhs_level,
        recommendation=hhs_recommendation
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