"""
app.py
------
Employee Attrition & Workforce Analytics — Interactive HR Analytics Platform
Author : Mayur Pandey
Dataset: IBM HR Analytics Employee Attrition & Performance (Kaggle)

Run with:
    streamlit run app.py
"""

import sys
import os

# Ensure src/ is importable when running from project root
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── Internal modules ──────────────────────────────────────────────
from src.data_loader    import get_descriptive_stats, get_data_quality_report
from src.data_cleaning  import get_clean_data, get_summary_kpis
from src.analysis       import (
    attrition_by_column, attrition_by_two_columns, attrition_pivot,
    segment_analysis, income_stats_by_group, income_by_attrition,
    tenure_vs_attrition, generate_key_insights,
)
from src.statistics     import run_all_statistical_tests, get_significant_vars
from src.visualizations import (
    attrition_donut, attrition_rate_bar, attrition_heatmap,
    age_histogram, income_box, income_by_role_box,
    satisfaction_bar, gender_donut, marital_bar, education_bar,
    travel_bar, correlation_heatmap, scatter_income_age,
    tenure_attrition_line, overtime_wlb_heatmap, segment_heatmap,
)
from src.utils import (
    inject_css, render_kpi_row, section_header, insight_card,
    download_button, apply_sidebar_filters,
)

# ─────────────────────────────────────────────────────────────────
# Page config  (MUST be first Streamlit call)
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Analytics | Employee Attrition",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


# ─────────────────────────────────────────────────────────────────
# Load data with friendly error handling
# ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load():
    return get_clean_data()


try:
    df_full = load()
except FileNotFoundError as e:
    st.error(f"📂 **Dataset not found.**\n\n{e}")
    st.stop()
except ValueError as e:
    st.error(f"⚠️ **Data error:** {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ **Unexpected error while loading data:** {e}")
    st.stop()


# ─────────────────────────────────────────────────────────────────
# Sidebar — navigation + global filters
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='color:#f1f5f9; font-size:1.15rem; margin-bottom:0;'>"
        "📊 HR Analytics</h2>"
        "<p style='color:#94a3b8; font-size:0.78rem; margin-top:0.2rem;'>"
        "Employee Attrition Platform</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    PAGE = st.radio(
        "Navigation",
        options=[
            "🏠 Executive Overview",
            "👥 Workforce Demographics",
            "📉 Attrition Analysis",
            "💰 Compensation & Career",
            "🌟 Employee Experience",
            "🔬 Segment Analysis",
            "📐 Statistical Analysis",
            "🗃 Data Explorer",
            "💡 Key Insights",
            "ℹ️ About Project",
        ],
        label_visibility="collapsed",
    )

df = apply_sidebar_filters(df_full)
kpis = get_summary_kpis(df)


# ─────────────────────────────────────────────────────────────────
# Helper: standard plotly chart wrapper
# ─────────────────────────────────────────────────────────────────
def _chart(fig, height: int = 400, key: str = ""):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# =================================================================
# PAGE 1 — EXECUTIVE OVERVIEW
# =================================================================
if PAGE == "🏠 Executive Overview":
    st.markdown(
        "<h1 style='font-size:1.9rem;color:#1e293b;'>🏠 Executive Overview</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#6b7280; font-size:0.95rem;'>"
        "High-level workforce metrics and attrition summary for the filtered dataset.</p>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    # ── KPI row ──
    render_kpi_row(kpis)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top charts ──
    c1, c2 = st.columns([1, 2])
    with c1:
        section_header("Attrition Split")
        _chart(attrition_donut(kpis["employees_left"], kpis["employees_stayed"]))

    with c2:
        section_header("Attrition by Department")
        grp_dept = attrition_by_column(df, "Department")
        _chart(attrition_rate_bar(grp_dept, "Department"))

    c3, c4 = st.columns(2)
    with c3:
        section_header("Attrition by Job Role")
        grp_role = attrition_by_column(df, "JobRole")
        _chart(attrition_rate_bar(grp_role, "JobRole", "Attrition by Job Role"))

    with c4:
        section_header("Attrition by Overtime")
        grp_ot = attrition_by_column(df, "OverTime")
        _chart(attrition_rate_bar(grp_ot, "OverTime", "Attrition by Overtime"))

    c5, c6 = st.columns(2)
    with c5:
        section_header("Attrition by Age Group")
        grp_ag = attrition_by_column(df, "AgeGroup")
        _chart(attrition_rate_bar(grp_ag, "AgeGroup", "Attrition by Age Group"))

    with c6:
        section_header("Age Distribution")
        _chart(age_histogram(df))

    # ── Key observations ──
    section_header("Key Observations")
    top_dept = attrition_by_column(df, "Department").iloc[0]
    top_role = attrition_by_column(df, "JobRole").iloc[0]
    ot_df    = attrition_by_column(df, "OverTime")
    ot_yes   = ot_df.loc[ot_df["OverTime"] == "Yes", "AttritionRate"]
    ot_no    = ot_df.loc[ot_df["OverTime"] == "No",  "AttritionRate"]

    obs = [
        f"• Overall attrition rate in this dataset: **{kpis['attrition_rate']:.1f}%** "
        f"({kpis['employees_left']:,} out of {kpis['total_employees']:,} employees).",
        f"• Highest attrition by department: **{top_dept['Department']}** at "
        f"**{top_dept['AttritionRate']:.1f}%**.",
        f"• Highest attrition by job role: **{top_role['JobRole']}** at "
        f"**{top_role['AttritionRate']:.1f}%**.",
    ]
    if len(ot_yes) and len(ot_no):
        obs.append(
            f"• Employees who work overtime show an observed attrition rate of "
            f"**{ot_yes.values[0]:.1f}%** vs **{ot_no.values[0]:.1f}%** for those who do not."
        )
    obs.append(
        f"• Average age: **{kpis['avg_age']:.1f} years** | "
        f"Average monthly income: **${kpis['avg_monthly_income']:,.0f}** | "
        f"Average tenure: **{kpis['avg_tenure']:.1f} years**."
    )
    with st.container():
        for o in obs:
            st.markdown(o)

    st.markdown("<br>", unsafe_allow_html=True)
    download_button(df, "Download Filtered Dataset", "hr_filtered.csv")


# =================================================================
# PAGE 2 — WORKFORCE DEMOGRAPHICS
# =================================================================
elif PAGE == "👥 Workforce Demographics":
    st.markdown(
        "<h1 style='font-size:1.9rem;color:#1e293b;'>👥 Workforce Demographics</h1>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        section_header("Age Distribution")
        _chart(age_histogram(df))
    with c2:
        section_header("Gender Distribution")
        _chart(gender_donut(df))

    c3, c4 = st.columns(2)
    with c3:
        section_header("Marital Status vs Attrition")
        _chart(marital_bar(df))
    with c4:
        section_header("Education Level")
        _chart(education_bar(df))

    c5, c6 = st.columns(2)
    with c5:
        section_header("Employees by Department")
        dept_cnt = df["Department"].value_counts().reset_index()
        dept_cnt.columns = ["Department", "Count"]
        fig = px.bar(dept_cnt, x="Department", y="Count",
                     color="Count", color_continuous_scale="Blues",
                     title="Employees by Department")
        _chart(fig)
    with c6:
        section_header("Employees by Job Level")
        jl_cnt = df["JobLevel"].value_counts().sort_index().reset_index()
        jl_cnt.columns = ["JobLevel", "Count"]
        fig = px.bar(jl_cnt, x="JobLevel", y="Count",
                     color="Count", color_continuous_scale="Purples",
                     title="Employees by Job Level")
        _chart(fig)

    section_header("Employees by Job Role")
    role_cnt = df["JobRole"].value_counts().reset_index()
    role_cnt.columns = ["JobRole", "Count"]
    fig = px.bar(role_cnt.sort_values("Count"),
                 x="Count", y="JobRole", orientation="h",
                 color="Count", color_continuous_scale="Teal",
                 title="Employees by Job Role")
    _chart(fig, height=450)

    c7, c8 = st.columns(2)
    with c7:
        section_header("Business Travel Frequency")
        bt_cnt = df["BusinessTravel"].value_counts().reset_index()
        bt_cnt.columns = ["BusinessTravel", "Count"]
        fig = px.pie(bt_cnt, names="BusinessTravel", values="Count",
                     hole=0.5, title="Business Travel Distribution",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        _chart(fig)
    with c8:
        section_header("Income Group Distribution")
        ig_cnt = df["IncomeGroup"].value_counts().reset_index()
        ig_cnt.columns = ["IncomeGroup", "Count"]
        fig = px.bar(ig_cnt, x="IncomeGroup", y="Count",
                     color="IncomeGroup", title="Income Group Distribution",
                     color_discrete_sequence=px.colors.qualitative.Safe)
        _chart(fig)

    section_header("Monthly Income Distribution by Job Level")
    fig = px.box(df, x="JobLevel", y="MonthlyIncome", color="Attrition",
                 color_discrete_map={"No": "#3b82f6", "Yes": "#ef4444"},
                 title="Monthly Income by Job Level",
                 labels={"MonthlyIncome": "Monthly Income ($)"})
    _chart(fig)

    download_button(df, "Download Demographics Data", "hr_demographics.csv")


# =================================================================
# PAGE 3 — ATTRITION ANALYSIS
# =================================================================
elif PAGE == "📉 Attrition Analysis":
    st.markdown(
        "<h1 style='font-size:1.9rem;color:#1e293b;'>📉 Attrition Analysis</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#6b7280;'>Each chart shows BOTH employee count and attrition rate "
        "to prevent size-driven misleading conclusions.</p>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    # Summary KPI strip
    render_kpi_row(kpis)
    st.markdown("<br>", unsafe_allow_html=True)

    # Core attrition breakdowns
    charts = [
        ("Department",      "Attrition by Department"),
        ("JobRole",         "Attrition by Job Role"),
        ("JobLevel",        "Attrition by Job Level"),
        ("OverTime",        "Attrition by Overtime"),
        ("AgeGroup",        "Attrition by Age Group"),
        ("IncomeGroup",     "Attrition by Income Group"),
        ("TenureGroup",     "Attrition by Tenure Group"),
        ("BusinessTravel",  "Attrition by Business Travel"),
        ("Gender",          "Attrition by Gender"),
        ("MaritalStatus",   "Attrition by Marital Status"),
    ]
    for i in range(0, len(charts), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(charts):
                var, title = charts[i + j]
                with col:
                    section_header(title)
                    grp = attrition_by_column(df, var)
                    _chart(attrition_rate_bar(grp, var, title))

    # Satisfaction dims
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    section_header("Attrition by Satisfaction Dimensions")
    sat_dims = [
        ("JobSatisfaction",         "JobSatisfactionLabel"),
        ("WorkLifeBalance",         "WorkLifeBalanceLabel"),
        ("EnvironmentSatisfaction", "EnvironmentSatisfactionLabel"),
        ("JobInvolvement",          "JobInvolvementLabel"),
    ]
    for i in range(0, len(sat_dims), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(sat_dims):
                num_col, lbl_col = sat_dims[i + j]
                with col:
                    _chart(satisfaction_bar(df, num_col, lbl_col))

    # Heatmap: Dept × Job Level
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    section_header("Attrition Heatmap: Department × Job Level")
    pivot = attrition_pivot(df, "Department", "JobLevel")
    _chart(attrition_heatmap(pivot, "Attrition Rate (%) by Department × Job Level"))

    # Heatmap: Job Role × Overtime
    section_header("Attrition Heatmap: Job Role × Overtime")
    pivot2 = attrition_pivot(df, "JobRole", "OverTime")
    _chart(attrition_heatmap(pivot2, "Attrition Rate (%) by Job Role × Overtime"))

    download_button(df, "Download Attrition Data", "hr_attrition.csv")


# =================================================================
# PAGE 4 — COMPENSATION & CAREER
# =================================================================
elif PAGE == "💰 Compensation & Career":
    st.markdown(
        "<h1 style='font-size:1.9rem;color:#1e293b;'>💰 Compensation & Career</h1>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        section_header("Monthly Income by Attrition")
        _chart(income_box(df))
    with c2:
        section_header("Salary Hike vs Attrition")
        fig = px.box(df, x="Attrition", y="PercentSalaryHike",
                     color="Attrition",
                     color_discrete_map={"No": "#3b82f6", "Yes": "#ef4444"},
                     title="Percent Salary Hike by Attrition",
                     labels={"PercentSalaryHike": "Salary Hike (%)"},
                     points="outliers")
        _chart(fig)

    section_header("Monthly Income by Job Role & Attrition")
    _chart(income_by_role_box(df))

    c3, c4 = st.columns(2)
    with c3:
        section_header("Stock Option Level vs Attrition")
        grp_so = attrition_by_column(df, "StockOptionLevel")
        _chart(attrition_rate_bar(grp_so, "StockOptionLevel",
                                  "Attrition by Stock Option Level"))
    with c4:
        section_header("Income vs Age (coloured by Attrition)")
        _chart(scatter_income_age(df))

    section_header("Income by Job Level")
    inc_by_jl = income_stats_by_group(df, "JobLevel")
    fig = px.bar(inc_by_jl, x="JobLevel", y="Median", error_y=None,
                 color="Median", color_continuous_scale="Blues",
                 text="Median",
                 title="Median Monthly Income by Job Level",
                 labels={"Median": "Median Income ($)"})
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    _chart(fig)

    # Career growth
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    section_header("Career Growth & Attrition")
    tenure_cols = [
        ("YearsAtCompany",         "Years at Company"),
        ("YearsInCurrentRole",     "Years in Current Role"),
        ("YearsSinceLastPromotion","Years Since Last Promotion"),
        ("YearsWithCurrManager",   "Years with Current Manager"),
    ]
    for i in range(0, len(tenure_cols), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(tenure_cols):
                tc, tl = tenure_cols[i + j]
                with col:
                    grp = tenure_vs_attrition(df, tc, bins=8)
                    _chart(tenure_attrition_line(grp, f"{tc}_bin"))

    section_header("Training Frequency vs Attrition")
    grp_tr = attrition_by_column(df, "TrainingTimesLastYear")
    _chart(attrition_rate_bar(grp_tr, "TrainingTimesLastYear",
                              "Attrition by Training Times Last Year"))

    download_button(df, "Download Compensation Data", "hr_compensation.csv")


# =================================================================
# PAGE 5 — EMPLOYEE EXPERIENCE
# =================================================================
elif PAGE == "🌟 Employee Experience":
    st.markdown(
        "<h1 style='font-size:1.9rem;color:#1e293b;'>🌟 Employee Experience</h1>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    # Satisfaction dims
    section_header("Satisfaction Dimensions by Attrition")
    sat_dims = [
        ("JobSatisfaction",         "JobSatisfactionLabel",         "Job Satisfaction"),
        ("EnvironmentSatisfaction", "EnvironmentSatisfactionLabel", "Environment Satisfaction"),
        ("RelationshipSatisfaction","RelationshipSatisfactionLabel","Relationship Satisfaction"),
        ("WorkLifeBalance",         "WorkLifeBalanceLabel",         "Work-Life Balance"),
        ("JobInvolvement",          "JobInvolvementLabel",          "Job Involvement"),
    ]
    for i in range(0, len(sat_dims), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(sat_dims):
                nc, lc, title = sat_dims[i + j]
                with col:
                    _chart(satisfaction_bar(df, nc, lc))

    # Overtime deep-dive
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    section_header("Overtime Deep-Dive")

    c1, c2 = st.columns(2)
    with c1:
        section_header("Overtime vs Work-Life Balance")
        wlb_ot = (
            df.groupby(["OverTime", "WorkLifeBalanceLabel"], observed=True)
            .size().reset_index(name="Count")
        )
        fig = px.bar(wlb_ot, x="WorkLifeBalanceLabel", y="Count",
                     color="OverTime", barmode="group",
                     color_discrete_map={"No": "#3b82f6", "Yes": "#ef4444"},
                     title="Work-Life Balance Distribution by Overtime",
                     category_orders={"WorkLifeBalanceLabel": ["Bad","Good","Better","Best"]})
        _chart(fig)

    with c2:
        section_header("Overtime vs Job Satisfaction")
        js_ot = (
            df.groupby(["OverTime", "JobSatisfactionLabel"], observed=True)
            .size().reset_index(name="Count")
        )
        fig = px.bar(js_ot, x="JobSatisfactionLabel", y="Count",
                     color="OverTime", barmode="group",
                     color_discrete_map={"No": "#3b82f6", "Yes": "#ef4444"},
                     title="Job Satisfaction Distribution by Overtime",
                     category_orders={"JobSatisfactionLabel": ["Low","Medium","High","Very High"]})
        _chart(fig)

    section_header("Overtime Work-Life Balance Heatmap by Job Role")
    _chart(overtime_wlb_heatmap(df))

    # Distance & Travel
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    section_header("Commute & Travel")

    c3, c4 = st.columns(2)
    with c3:
        grp_dg = attrition_by_column(df, "DistanceGroup")
        _chart(attrition_rate_bar(grp_dg, "DistanceGroup",
                                  "Attrition by Commute Distance Group"))
    with c4:
        _chart(travel_bar(df))

    section_header("Distance from Home Distribution by Attrition")
    fig = px.histogram(df, x="DistanceFromHome", color="Attrition",
                       color_discrete_map={"No": "#3b82f6", "Yes": "#ef4444"},
                       barmode="overlay", nbins=25, opacity=0.75,
                       title="Distance from Home Distribution",
                       labels={"DistanceFromHome": "Distance from Home (km)"})
    _chart(fig)

    download_button(df, "Download Experience Data", "hr_experience.csv")


# =================================================================
# PAGE 6 — SEGMENT ANALYSIS
# =================================================================
elif PAGE == "🔬 Segment Analysis":
    st.markdown(
        "<h1 style='font-size:1.9rem;color:#1e293b;'>🔬 Segment Analysis</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#6b7280;'>Select up to 3 variables to calculate attrition "
        "rates per segment. Only segments with ≥10 employees are shown.</p>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    SEGMENT_VARS = [
        "Department", "JobRole", "JobLevel", "Gender", "MaritalStatus",
        "BusinessTravel", "OverTime", "AgeGroup", "IncomeGroup", "TenureGroup",
        "DistanceGroup", "JobSatisfactionLabel", "WorkLifeBalanceLabel",
        "EnvironmentSatisfactionLabel", "JobInvolvementLabel",
    ]

    c1, c2, c3 = st.columns(3)
    with c1:
        v1 = st.selectbox("Variable 1", SEGMENT_VARS, index=0, key="sv1")
    with c2:
        v2 = st.selectbox("Variable 2", ["— None —"] + SEGMENT_VARS, index=3, key="sv2")
    with c3:
        v3 = st.selectbox("Variable 3", ["— None —"] + SEGMENT_VARS, index=0, key="sv3")

    min_n = st.slider("Minimum employees per segment", 5, 50, 10, 5)

    chosen = [v for v in [v1, v2 if v2 != "— None —" else None,
                            v3 if v3 != "— None —" else None] if v]
    seg_df = segment_analysis(df, chosen, min_n=min_n)

    if seg_df.empty:
        st.info("No segments found with the selected variables and minimum size.")
    else:
        section_header(f"Segment Results ({len(seg_df)} segments)")
        st.dataframe(
            seg_df.style
                  .background_gradient(subset=["AttritionRate"], cmap="YlOrRd")
                  .format({"AttritionRate": "{:.1f}%", "Total": "{:,}",
                            "Left": "{:,}", "Stayed": "{:,}"}),
            use_container_width=True,
        )
        download_button(seg_df, "Download Segment Results", "hr_segments.csv")

        # Bar chart of top 20 segments
        top20 = seg_df.head(20)
        label_col = " × ".join(chosen)
        top20 = top20.copy()
        top20[label_col] = top20[chosen].apply(
            lambda r: " | ".join([str(r[c]) for c in chosen]), axis=1
        )
        fig = px.bar(
            top20.sort_values("AttritionRate"),
            x="AttritionRate", y=label_col, orientation="h",
            color="AttritionRate", color_continuous_scale="Reds",
            text="AttritionRate",
            title=f"Top 20 Segments by Attrition Rate (min n={min_n})",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        _chart(fig, height=max(400, 30 * len(top20)))

        # Heatmap (only for exactly 2 variables)
        if len(chosen) == 2:
            section_header(f"Heatmap: {chosen[0]} × {chosen[1]}")
            _chart(segment_heatmap(seg_df, chosen[0], chosen[1]))

    # Pre-built interesting segments
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    section_header("Pre-Built Segments")
    pre_segs = [
        (["OverTime", "JobSatisfactionLabel"],  "Overtime × Job Satisfaction"),
        (["OverTime", "WorkLifeBalanceLabel"],  "Overtime × Work-Life Balance"),
        (["OverTime", "AgeGroup"],              "Overtime × Age Group"),
        (["IncomeGroup", "OverTime"],           "Income Group × Overtime"),
        (["AgeGroup", "IncomeGroup"],           "Age Group × Income Group"),
    ]
    for vars_combo, title in pre_segs:
        with st.expander(f"📋 {title}"):
            seg = segment_analysis(df, vars_combo, min_n=10)
            if not seg.empty:
                st.dataframe(seg.style.background_gradient(
                    subset=["AttritionRate"], cmap="YlOrRd"
                ).format({"AttritionRate": "{:.1f}%"}), use_container_width=True)
                _chart(segment_heatmap(seg, vars_combo[0], vars_combo[1]))
            else:
                st.write("Insufficient data.")


# =================================================================
# PAGE 7 — STATISTICAL ANALYSIS
# =================================================================
elif PAGE == "📐 Statistical Analysis":
    st.markdown(
        "<h1 style='font-size:1.9rem;color:#1e293b;'>📐 Statistical Analysis</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#6b7280;'>Statistical tests assess whether observed differences "
        "between employees who stayed and left are likely due to chance.<br>"
        "<strong>Important:</strong> statistical association ≠ causation.</p>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    with st.spinner("Running statistical tests…"):
        stats_df = run_all_statistical_tests(df)

    section_header("Test Results Table")
    display_cols = ["Variable", "Test", "Statistic", "p-value", "Significant", "Interpretation"]
    display_cols = [c for c in display_cols if c in stats_df.columns]

    st.dataframe(
        stats_df[display_cols].style.apply(
            lambda row: [
                "background-color: #fef2f2" if row.get("Significant") == "Yes ✓" else ""
                for _ in row
            ], axis=1
        ),
        use_container_width=True,
        height=450,
    )
    download_button(stats_df, "Download Statistical Results", "hr_statistics.csv")

    # Significant variables chart
    sig_df = get_significant_vars(stats_df)
    if not sig_df.empty:
        section_header(f"Statistically Significant Variables (n={len(sig_df)})")
        pval_df = sig_df.copy()
        pval_df["p-value"] = pd.to_numeric(pval_df["p-value"], errors="coerce")
        pval_df = pval_df.dropna(subset=["p-value"])
        pval_df["-log10(p)"] = -np.log10(pval_df["p-value"].clip(lower=1e-300))
        fig = px.bar(
            pval_df.sort_values("-log10(p)", ascending=False).head(20),
            x="-log10(p)", y="Variable", orientation="h",
            color="-log10(p)", color_continuous_scale="Blues",
            text="-log10(p)",
            title="Top Significant Variables (−log₁₀ p-value)",
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        _chart(fig, height=450)

    # Interpretation guide
    with st.expander("📖 How to Read These Results"):
        st.markdown("""
**Chi-Square Test** (categorical variables)
- Tests whether the distribution of a categorical variable differs between employees who left and stayed.
- A p-value < 0.05 indicates a statistically significant association at the 5% level.
- **Cramér's V**: effect size (0 = no association, 1 = perfect association).

**Mann–Whitney U Test** (numerical variables)
- Compares medians between the two groups without assuming a normal distribution.
- A p-value < 0.05 indicates the distributions differ significantly.
- **Rank-biserial r**: effect size (0 = no difference, 1 = complete separation).

**Caution**: A statistically significant result means the observed difference is unlikely to be due to chance in this dataset. It does not imply that the variable *causes* attrition.
        """)


# =================================================================
# PAGE 8 — DATA EXPLORER
# =================================================================
elif PAGE == "🗃 Data Explorer":
    st.markdown(
        "<h1 style='font-size:1.9rem;color:#1e293b;'>🗃 Data Explorer</h1>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    # Column selector
    all_cols = df.columns.tolist()
    selected_cols = st.multiselect(
        "Select columns to display", all_cols, default=all_cols[:12], key="explorer_cols"
    )

    # Text search
    search_term = st.text_input("Search (filters JobRole, Department, MaritalStatus)", "")

    display_df = df[selected_cols].copy() if selected_cols else df.copy()
    if search_term:
        mask = pd.Series(False, index=display_df.index)
        for col in ["JobRole", "Department", "MaritalStatus"]:
            if col in display_df.columns:
                mask |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
        display_df = display_df[mask]

    st.markdown(f"**{len(display_df):,}** records shown")
    st.dataframe(display_df, use_container_width=True, height=480)

    c1, c2 = st.columns(2)
    with c1:
        download_button(display_df, "Download Filtered Data", "hr_explorer.csv")
    with c2:
        stats_display = get_descriptive_stats(df)
        download_button(stats_display, "Download Summary Statistics", "hr_summary_stats.csv")

    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    section_header("Descriptive Statistics")
    st.dataframe(get_descriptive_stats(df).style.background_gradient(
        subset=["mean", "std"], cmap="Blues"
    ), use_container_width=True)

    # Data quality report
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    section_header("Data Quality Report")
    report = get_data_quality_report(df_full)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rows",     f"{report['shape'][0]:,}")
    c2.metric("Total Columns",  f"{report['shape'][1]:,}")
    c3.metric("Missing Values", f"{sum(report['missing'].values()):,}")
    c4.metric("Duplicate Rows", f"{report['duplicate_rows']:,}")

    col_info = pd.DataFrame({
        "Column":   list(report["dtypes"].keys()),
        "Dtype":    list(report["dtypes"].values()),
    })
    missing_series = pd.Series(report["missing"])
    col_info["Missing"] = col_info["Column"].map(missing_series).fillna(0).astype(int)

    st.dataframe(col_info, use_container_width=True)

    if report["outlier_summary"]:
        section_header("Potential Outliers (IQR Method)")
        out_df = pd.DataFrame.from_dict(
            report["outlier_summary"], orient="index", columns=["Outlier Count"]
        ).reset_index().rename(columns={"index": "Column"})
        st.dataframe(out_df, use_container_width=True)


# =================================================================
# PAGE 9 — KEY INSIGHTS
# =================================================================
elif PAGE == "💡 Key Insights":
    st.markdown(
        "<h1 style='font-size:1.9rem;color:#1e293b;'>💡 Key Insights</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#6b7280;'>All insights are automatically generated from the data. "
        "Language is intentionally cautious — association ≠ causation.</p>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    with st.spinner("Generating insights…"):
        insights = generate_key_insights(df)

    for ins in insights:
        insight_card(
            title=ins["title"],
            observation=ins["observation"],
            metric=ins["metric"],
            interpretation=ins["interpretation"],
        )

    # Correlation chart
    section_header("Correlation with Attrition")
    _chart(correlation_heatmap(df), height=500)


# =================================================================
# PAGE 10 — ABOUT PROJECT
# =================================================================
elif PAGE == "ℹ️ About Project":
    st.markdown(
        "<h1 style='font-size:1.9rem;color:#1e293b;'>ℹ️ About This Project</h1>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
## Employee Attrition & Workforce Analytics

**Author:** Mayur Pandey

---

### Project Overview
This is an end-to-end HR analytics application that explores factors associated with
employee attrition using the IBM HR Analytics Employee Attrition & Performance dataset.
The platform is designed as a professional portfolio project, not a basic exploratory notebook.

---

### Dataset
- **Source:** [Kaggle — IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset)
- **Records:** 1,470 employees
- **Features:** 35 original columns covering demographics, job attributes, compensation, satisfaction, and attrition
- **Target variable:** `Attrition` (Yes / No)
- ⚠️ This is a **fictional dataset** created by IBM data scientists for demonstration purposes.
  It does not represent actual IBM employee data.

---

### Technology Stack
| Component | Library |
|---|---|
| Data Processing | Pandas, NumPy |
| Visualisation | Plotly, Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Statistics | SciPy |
| ML Support | Scikit-learn |

---

### Dashboard Sections
| Page | Description |
|---|---|
| Executive Overview | KPIs, top-line attrition metrics, key observations |
| Workforce Demographics | Age, gender, education, job level distributions |
| Attrition Analysis | Attrition rates across all key dimensions |
| Compensation & Career | Income analysis, career growth patterns |
| Employee Experience | Satisfaction scores, overtime, commute analysis |
| Segment Analysis | Interactive multi-variable segment explorer |
| Statistical Analysis | Chi-square and Mann–Whitney U tests with p-values |
| Data Explorer | Filterable, searchable, downloadable data table |
| Key Insights | Auto-generated evidence-based findings |

---

### Analytical Approach
- All insights are derived computationally from the actual dataset values.
- No analytical results are hardcoded.
- Statistical language uses cautious framing: "associated with", "shows a higher observed rate".
- Causality is never claimed unless causal evidence exists.
- Effect sizes are reported alongside p-values to avoid p-value-only interpretation.

---

### Limitations
- The dataset is fictional and should not be used to draw conclusions about any real organisation.
- The dataset is cross-sectional; causal inference requires longitudinal or experimental data.
- Sample sizes for some job roles are small, limiting conclusions for those groups.
- No machine-learning predictive model is deployed (this is a descriptive analytics project).

---

### How to Run
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the dashboard
streamlit run app.py
```

---

### Project Files
```
IBM-HR-Analytics/
├── data/WA_Fn-UseC_-HR-Employee-Attrition.csv
├── app.py
├── src/
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── analysis.py
│   ├── statistics.py
│   ├── visualizations.py
│   └── utils.py
├── notebooks/HR_Analytics_EDA.ipynb
├── requirements.txt
├── README.md
└── .gitignore
```
    """)


# ─────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────
st.sidebar.markdown(
    "<hr style='border-color:#334155;'>"
    "<p style='color:#475569; font-size:0.72rem; text-align:center;'>"
    "IBM HR Analytics Platform<br>© 2024 Mayur Pandey</p>",
    unsafe_allow_html=True,
)
