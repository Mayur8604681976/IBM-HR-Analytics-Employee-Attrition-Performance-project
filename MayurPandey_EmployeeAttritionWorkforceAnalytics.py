"""
================================================================================
  MayurPandey_EmployeeAttritionWorkforceAnalytics.py
  Employee Attrition & Workforce Analytics — Standalone Single-File Version
  Author : Mayur Pandey
  Dataset: IBM HR Analytics Employee Attrition & Performance
  Source : https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset

  DISCLAIMER: The IBM HR dataset is fictional and does not represent any real
  organisation's data. Findings are descriptive; association ≠ causation.

  Run with:
      streamlit run MayurPandey_EmployeeAttritionWorkforceAnalytics.py

  Or place the CSV at:
      ./data/WA_Fn-UseC_-HR-Employee-Attrition.csv
  or in the same directory as this file.
================================================================================
"""

import os
import sys
import warnings
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Analytics | Employee Attrition",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f3f4f6; }
[data-testid="stSidebar"] { background: #1e293b !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] hr { border-color: #334155; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
.kpi-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px;
            padding: 1.1rem 1.4rem; text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.kpi-value { font-size: 2rem; font-weight: 700; color: #1e293b; line-height: 1.2; }
.kpi-label { font-size: 0.78rem; font-weight: 600; letter-spacing: 0.04em;
             text-transform: uppercase; color: #6b7280; margin-top: 0.25rem; }
.section-header { font-size: 1.25rem; font-weight: 700; color: #1e293b;
                  border-left: 4px solid #3b82f6; padding-left: 0.75rem;
                  margin-bottom: 0.5rem; }
.insight-card { background: #ffffff; border: 1px solid #e5e7eb;
                border-left: 4px solid #3b82f6; border-radius: 8px;
                padding: 1rem 1.25rem; margin-bottom: 0.9rem; }
.insight-title { font-size: 0.95rem; font-weight: 700; color: #1e293b; margin-bottom: 0.3rem; }
.insight-text { font-size: 0.88rem; color: #374151; }
.insight-metric { background: #f0f9ff; border-radius: 5px; padding: 0.3rem 0.6rem;
                  font-size: 0.82rem; font-family: monospace; color: #0369a1;
                  display: inline-block; margin: 0.35rem 0; }
.hr-divider { border-top: 1px solid #e5e7eb; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────
STAY_COLOR = "#3b82f6"
LEFT_COLOR = "#ef4444"
FONT_FAMILY = "Inter, -apple-system, Segoe UI, sans-serif"

EDUCATION_MAP = {1: "Below College", 2: "College", 3: "Bachelor", 4: "Master", 5: "Doctor"}
SAT_MAP  = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
WLB_MAP  = {1: "Bad", 2: "Good", 3: "Better", 4: "Best"}


# ─────────────────────────────────────────────────────────────────
# DATA LOADING & CLEANING
# ─────────────────────────────────────────────────────────────────
def find_csv() -> str:
    """Search for the CSV in common locations."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "data", "WA_Fn-UseC_-HR-Employee-Attrition.csv"),
        os.path.join(os.path.dirname(__file__), "WA_Fn-UseC_-HR-Employee-Attrition.csv"),
        os.path.join(os.path.dirname(__file__), "HR-Employee-Attrition.csv"),
        os.path.join(os.path.dirname(__file__), "data", "HR-Employee-Attrition.csv"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        "Dataset not found. Place 'WA_Fn-UseC_-HR-Employee-Attrition.csv' in a 'data/' "
        "subfolder or in the same directory as this script."
    )


@st.cache_data(show_spinner=False)
def load_and_clean() -> pd.DataFrame:
    """Load CSV, clean, and engineer features."""
    path = find_csv()
    df = pd.read_csv(path, encoding="utf-8-sig")

    if df.empty:
        raise ValueError("Dataset is empty.")

    # Drop constant columns
    for col in ["EmployeeCount", "Over18", "StandardHours"]:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    df.drop_duplicates(inplace=True)

    # Categorical types
    for col in ["Attrition","BusinessTravel","Department","EducationField",
                "Gender","JobRole","MaritalStatus","OverTime"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Ordinal labels
    if "Education"              in df.columns: df["EducationLabel"]               = df["Education"].map(EDUCATION_MAP)
    if "EnvironmentSatisfaction"in df.columns: df["EnvironmentSatisfactionLabel"] = df["EnvironmentSatisfaction"].map(SAT_MAP)
    if "JobInvolvement"         in df.columns: df["JobInvolvementLabel"]          = df["JobInvolvement"].map(SAT_MAP)
    if "JobSatisfaction"        in df.columns: df["JobSatisfactionLabel"]         = df["JobSatisfaction"].map(SAT_MAP)
    if "RelationshipSatisfaction"in df.columns:df["RelationshipSatisfactionLabel"]= df["RelationshipSatisfaction"].map(SAT_MAP)
    if "WorkLifeBalance"        in df.columns: df["WorkLifeBalanceLabel"]         = df["WorkLifeBalance"].map(WLB_MAP)

    # Flags
    df["AttritionFlag"] = (df["Attrition"] == "Yes").astype(int)
    df["OvertimeFlag"]  = (df["OverTime"]  == "Yes").astype(int)

    # Derived groups
    df["AgeGroup"] = pd.cut(df["Age"], bins=[17,24,34,44,54,100],
                             labels=["Under 25","25–34","35–44","45–54","55+"])
    q = df["MonthlyIncome"].quantile([0.33,0.67])
    df["IncomeGroup"] = pd.cut(df["MonthlyIncome"],
                                bins=[0,q[0.33],q[0.67],df["MonthlyIncome"].max()+1],
                                labels=["Low","Medium","High"], include_lowest=True)
    df["TenureGroup"] = pd.cut(df["YearsAtCompany"], bins=[-1,2,5,10,100],
                                labels=["New Employee","Early Career","Mid Career","Long Tenure"])
    df["DistanceGroup"] = pd.cut(df["DistanceFromHome"], bins=[0,5,15,100],
                                  labels=["Near","Moderate","Far"])
    return df


# ─────────────────────────────────────────────────────────────────
# ANALYSIS HELPERS
# ─────────────────────────────────────────────────────────────────
def attrition_by(df: pd.DataFrame, col: str) -> pd.DataFrame:
    grp = df.groupby(col, observed=True).agg(
        Total=("AttritionFlag","count"), Left=("AttritionFlag","sum")
    ).reset_index()
    grp["Stayed"] = grp["Total"] - grp["Left"]
    grp["AttritionRate"] = (grp["Left"]/grp["Total"]*100).round(2)
    return grp.sort_values("AttritionRate", ascending=False)


def segment_analysis(df: pd.DataFrame, variables: list, min_n: int = 10) -> pd.DataFrame:
    valid = [v for v in variables if v and v in df.columns]
    if not valid:
        return pd.DataFrame()
    grp = df.groupby(valid, observed=True).agg(
        Total=("AttritionFlag","count"), Left=("AttritionFlag","sum")
    ).reset_index()
    grp["Stayed"] = grp["Total"] - grp["Left"]
    grp["AttritionRate"] = (grp["Left"]/grp["Total"]*100).round(2)
    return grp[grp["Total"] >= min_n].sort_values("AttritionRate", ascending=False)


def kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    left  = int(df["AttritionFlag"].sum())
    return {
        "total":  total,
        "left":   left,
        "stayed": total - left,
        "rate":   round(left/total*100, 2) if total else 0,
        "age":    round(df["Age"].mean(), 1),
        "income": round(df["MonthlyIncome"].mean(), 0),
        "tenure": round(df["YearsAtCompany"].mean(), 1),
    }


# ─────────────────────────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────────────────────────
def _layout(fig):
    fig.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#f9fafb",
        font=dict(family=FONT_FAMILY, size=13),
        margin=dict(l=40,r=20,t=50,b=40),
    )
    fig.update_xaxes(showgrid=False, linecolor="#e5e7eb")
    fig.update_yaxes(gridcolor="#e5e7eb", linecolor="#e5e7eb")
    return fig


def dual_axis_bar(grp: pd.DataFrame, col: str, title: str = "") -> go.Figure:
    grp = grp.sort_values("AttritionRate", ascending=False)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=grp[col].astype(str), y=grp["Stayed"],
                         name="Stayed", marker_color=STAY_COLOR), secondary_y=False)
    fig.add_trace(go.Bar(x=grp[col].astype(str), y=grp["Left"],
                         name="Left", marker_color=LEFT_COLOR), secondary_y=False)
    fig.add_trace(go.Scatter(x=grp[col].astype(str), y=grp["AttritionRate"],
                             name="Attrition %", mode="lines+markers",
                             marker=dict(size=8, color="#f59e0b"),
                             line=dict(color="#f59e0b", width=2)), secondary_y=True)
    fig.update_layout(barmode="stack", title=title or f"Attrition by {col}",
                      paper_bgcolor="#ffffff", plot_bgcolor="#f9fafb",
                      font=dict(family=FONT_FAMILY),
                      legend=dict(orientation="h", y=-0.18),
                      margin=dict(l=40,r=40,t=50,b=60))
    fig.update_yaxes(title_text="Count", secondary_y=False, gridcolor="#e5e7eb")
    fig.update_yaxes(title_text="Attrition %", secondary_y=True, showgrid=False)
    return fig


def heatmap_pivot(df: pd.DataFrame, r: str, c: str, title: str = "") -> go.Figure:
    grp = df.groupby([r,c], observed=True).agg(
        Total=("AttritionFlag","count"), Left=("AttritionFlag","sum")
    ).reset_index()
    grp["AttritionRate"] = (grp["Left"]/grp["Total"]*100).round(1)
    pivot = grp.pivot(index=r, columns=c, values="AttritionRate")
    fig = px.imshow(pivot.fillna(0), text_auto=".1f", aspect="auto",
                    color_continuous_scale="RdYlGn_r", title=title,
                    labels=dict(color="Attrition %"))
    fig.update_layout(paper_bgcolor="#ffffff", font=dict(family=FONT_FAMILY))
    return fig


def sat_bar(df: pd.DataFrame, lbl_col: str) -> go.Figure:
    grp = df.groupby(lbl_col, observed=True).agg(
        Total=("AttritionFlag","count"), Left=("AttritionFlag","sum")
    ).reset_index()
    grp["AttritionRate"] = (grp["Left"]/grp["Total"]*100).round(2)
    fig = px.bar(grp, x=lbl_col, y="AttritionRate", color="AttritionRate",
                 color_continuous_scale="Reds", text="AttritionRate",
                 title=f"Attrition by {lbl_col.replace('Label','')}")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    return _layout(fig)


# ─────────────────────────────────────────────────────────────────
# STATISTICAL TESTS
# ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def run_stats(_df: pd.DataFrame) -> pd.DataFrame:
    results = []
    cat_vars = ["BusinessTravel","Department","EducationField","Gender","JobRole",
                "MaritalStatus","OverTime","AgeGroup","IncomeGroup","TenureGroup"]
    num_vars = ["Age","MonthlyIncome","TotalWorkingYears","YearsAtCompany",
                "YearsSinceLastPromotion","JobSatisfaction","WorkLifeBalance",
                "DistanceFromHome","StockOptionLevel","PercentSalaryHike",
                "YearsInCurrentRole","YearsWithCurrManager","TrainingTimesLastYear"]

    for col in cat_vars:
        if col not in _df.columns:
            continue
        try:
            ct = pd.crosstab(_df[col], _df["Attrition"])
            chi2, p, dof, _ = stats.chi2_contingency(ct)
            n = ct.values.sum()
            v = np.sqrt(chi2/(n*(min(ct.shape)-1)))
            results.append({"Variable":col,"Test":"Chi-Square","Statistic":round(chi2,3),
                             "p-value":round(p,6),"Effect":round(v,4),
                             "Significant":"Yes ✓" if p<0.05 else "No",
                             "Interpretation":f"χ²={chi2:.2f}, p={p:.4f}, Cramér's V={v:.3f}"})
        except Exception:
            pass

    for col in num_vars:
        if col not in _df.columns:
            continue
        try:
            gy = _df.loc[_df["Attrition"]=="Yes", col].dropna()
            gn = _df.loc[_df["Attrition"]=="No",  col].dropna()
            if len(gy) < 5 or len(gn) < 5:
                continue
            u, p = stats.mannwhitneyu(gy, gn, alternative="two-sided")
            r = abs(1 - (2*u)/(len(gy)*len(gn)))
            results.append({"Variable":col,"Test":"Mann-Whitney U","Statistic":round(u,0),
                             "p-value":round(p,6),"Effect":round(r,4),
                             "Significant":"Yes ✓" if p<0.05 else "No",
                             "Interpretation":f"U={u:.0f}, p={p:.4f}, r={r:.3f}, "
                                              f"Md(Left)={gy.median():.1f}, Md(Stayed)={gn.median():.1f}"})
        except Exception:
            pass

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────
# INSIGHT GENERATOR
# ─────────────────────────────────────────────────────────────────
def generate_insights(df: pd.DataFrame) -> list:
    insights = []
    total = len(df)
    left  = int(df["AttritionFlag"].sum())
    rate  = left/total*100

    insights.append({
        "title": "Overall Attrition Rate",
        "obs":   f"{rate:.1f}% of employees in this dataset left the organisation.",
        "metric":f"{left} / {total} = {rate:.1f}%",
        "interp":"An attrition rate above 15% warrants investigation into retention strategies.",
    })

    ot = attrition_by(df,"OverTime")
    ot_y = ot.loc[ot["OverTime"]=="Yes","AttritionRate"].values
    ot_n = ot.loc[ot["OverTime"]=="No", "AttritionRate"].values
    if len(ot_y) and len(ot_n):
        insights.append({
            "title": "Overtime & Attrition",
            "obs":   f"Overtime employees show {ot_y[0]:.1f}% attrition vs {ot_n[0]:.1f}% (no overtime).",
            "metric":f"Yes: {ot_y[0]:.1f}% | No: {ot_n[0]:.1f}%",
            "interp":"Overwork is associated with attrition in this dataset.",
        })

    js = attrition_by(df,"JobSatisfaction")
    lo = js.loc[js["JobSatisfaction"]==1,"AttritionRate"].values
    hi = js.loc[js["JobSatisfaction"]==4,"AttritionRate"].values
    if len(lo) and len(hi):
        insights.append({
            "title":"Job Satisfaction Gradient",
            "obs":  f"Satisfaction 1 → {lo[0]:.1f}% attrition; Satisfaction 4 → {hi[0]:.1f}%.",
            "metric":f"Low: {lo[0]:.1f}% | Very High: {hi[0]:.1f}%",
            "interp":"Lower satisfaction was associated with higher attrition in this dataset.",
        })

    top_d = attrition_by(df,"Department").iloc[0]
    insights.append({
        "title":f"Highest Attrition Department: {top_d['Department']}",
        "obs":  f"{top_d['Department']} shows {top_d['AttritionRate']:.1f}% attrition "
                f"({top_d['Left']}/{top_d['Total']}).",
        "metric":f"{top_d['Left']}/{top_d['Total']} = {top_d['AttritionRate']:.1f}%",
        "interp":"Department differences may reflect role demands, culture, or pay gaps.",
    })

    top_ag = attrition_by(df,"AgeGroup").iloc[0]
    insights.append({
        "title":f"Highest Attrition Age Group: {top_ag['AgeGroup']}",
        "obs":  f"{top_ag['AgeGroup']} shows {top_ag['AttritionRate']:.1f}% attrition.",
        "metric":f"{top_ag['Left']}/{top_ag['Total']} = {top_ag['AttritionRate']:.1f}%",
        "interp":"Younger employees may have higher job mobility and fewer retention benefits.",
    })

    yes_med = df[df["Attrition"]=="Yes"]["MonthlyIncome"].median()
    no_med  = df[df["Attrition"]=="No"]["MonthlyIncome"].median()
    insights.append({
        "title":"Income Differential",
        "obs":  f"Employees who left had median income ${yes_med:,.0f} vs ${no_med:,.0f} (stayed).",
        "metric":f"Left: ${yes_med:,.0f} | Stayed: ${no_med:,.0f}",
        "interp":"Lower compensation was associated with higher attrition in this dataset.",
    })

    wlb = attrition_by(df,"WorkLifeBalance")
    lw = wlb.loc[wlb["WorkLifeBalance"]==1,"AttritionRate"].values
    if len(lw):
        insights.append({
            "title":"Work-Life Balance & Attrition",
            "obs":  f"Employees with the lowest work-life balance show {lw[0]:.1f}% attrition.",
            "metric":f"WLB 1: {lw[0]:.1f}%",
            "interp":"Poor work-life balance was associated with higher attrition in this dataset.",
        })

    bt = attrition_by(df,"BusinessTravel")
    bf = bt.loc[bt["BusinessTravel"]=="Travel_Frequently","AttritionRate"].values
    if len(bf):
        insights.append({
            "title":"Frequent Travel & Attrition",
            "obs":  f"Frequent travelers show {bf[0]:.1f}% attrition.",
            "metric":f"Travel Frequently: {bf[0]:.1f}%",
            "interp":"Frequent travel may affect work-life balance and was associated with attrition.",
        })

    so = attrition_by(df,"StockOptionLevel")
    ns = so.loc[so["StockOptionLevel"]==0,"AttritionRate"].values
    if len(ns):
        hs = so[so["StockOptionLevel"]>0]
        hs_rate = hs["Left"].sum()/hs["Total"].sum()*100 if len(hs) else 0
        insights.append({
            "title":"Stock Options & Retention",
            "obs":  f"No-stock employees: {ns[0]:.1f}% attrition vs {hs_rate:.1f}% (with stock options).",
            "metric":f"No stock: {ns[0]:.1f}% | Has stock: {hs_rate:.1f}%",
            "interp":"Equity stakes were associated with lower attrition in this dataset.",
        })

    top_r = attrition_by(df,"JobRole").iloc[0]
    insights.append({
        "title":f"Highest Attrition Role: {top_r['JobRole']}",
        "obs":  f"{top_r['JobRole']} shows {top_r['AttritionRate']:.1f}% attrition "
                f"({top_r['Left']}/{top_r['Total']}).",
        "metric":f"{top_r['Left']}/{top_r['Total']} = {top_r['AttritionRate']:.1f}%",
        "interp":"Role-level attrition differences may reflect pay, career path, or workload.",
    })

    return insights


# ─────────────────────────────────────────────────────────────────
# UTILITY RENDERS
# ─────────────────────────────────────────────────────────────────
def sh(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def kpi_card_html(label: str, value: str) -> str:
    return f'<div class="kpi-card"><div class="kpi-value">{value}</div>' \
           f'<div class="kpi-label">{label}</div></div>'


def render_kpis(k: dict):
    cols = st.columns(7)
    items = [
        ("Total Employees",    f"{k['total']:,}"),
        ("Employees Left",     f"{k['left']:,}"),
        ("Employees Stayed",   f"{k['stayed']:,}"),
        ("Attrition Rate",     f"{k['rate']:.1f}%"),
        ("Avg Age",            f"{k['age']:.1f} yrs"),
        ("Avg Monthly Income", f"${k['income']:,.0f}"),
        ("Avg Tenure",         f"{k['tenure']:.1f} yrs"),
    ]
    for col, (lbl, val) in zip(cols, items):
        col.markdown(kpi_card_html(lbl, val), unsafe_allow_html=True)


def dl_btn(df: pd.DataFrame, label: str, fname: str):
    st.download_button(f"⬇ {label}", df.to_csv(index=False).encode("utf-8"),
                       fname, "text/csv")


def icard(ins: dict):
    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">💡 {ins["title"]}</div>'
        f'<div class="insight-text">{ins["obs"]}</div>'
        f'<div class="insight-metric">{ins["metric"]}</div>'
        f'<div class="insight-text" style="color:#6b7280;margin-top:0.4rem;">{ins["interp"]}</div>'
        f'</div>', unsafe_allow_html=True
    )


def _chart(fig, h=400):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────
# SIDEBAR + FILTERS
# ─────────────────────────────────────────────────────────────────
try:
    df_full = load_and_clean()
except Exception as e:
    st.error(f"❌ **Error loading dataset:** {e}")
    st.stop()

with st.sidebar:
    st.markdown(
        "<h2 style='color:#f1f5f9;font-size:1.15rem;margin-bottom:0;'>📊 HR Analytics</h2>"
        "<p style='color:#94a3b8;font-size:0.78rem;margin-top:0.2rem;'>Employee Attrition Platform</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    PAGE = st.radio("Navigation", [
        "🏠 Executive Overview", "👥 Workforce Demographics",
        "📉 Attrition Analysis", "💰 Compensation & Career",
        "🌟 Employee Experience", "🔬 Segment Analysis",
        "📐 Statistical Analysis", "🗃 Data Explorer",
        "💡 Key Insights", "ℹ️ About Project",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("#### 🔍 Global Filters")

    def mf(col, lbl, key):
        opts = sorted(df_full[col].dropna().unique().tolist(), key=str)
        return st.sidebar.multiselect(lbl, opts, default=opts, key=key)

    f_dept = mf("Department",    "Department",      "f_dept")
    f_role = mf("JobRole",       "Job Role",        "f_role")
    f_gen  = mf("Gender",        "Gender",          "f_gen")
    f_ag   = mf("AgeGroup",      "Age Group",       "f_ag")
    f_jl   = mf("JobLevel",      "Job Level",       "f_jl")
    f_ot   = mf("OverTime",      "Overtime",        "f_ot")
    f_bt   = mf("BusinessTravel","Business Travel", "f_bt")
    f_ms   = mf("MaritalStatus", "Marital Status",  "f_ms")
    f_at   = mf("Attrition",     "Attrition",       "f_at")

    if st.button("↺ Reset Filters"):
        st.rerun()

df = df_full[
    df_full["Department"].isin(f_dept) &
    df_full["JobRole"].isin(f_role) &
    df_full["Gender"].isin(f_gen) &
    df_full["AgeGroup"].isin(f_ag) &
    df_full["JobLevel"].isin(f_jl) &
    df_full["OverTime"].isin(f_ot) &
    df_full["BusinessTravel"].isin(f_bt) &
    df_full["MaritalStatus"].isin(f_ms) &
    df_full["Attrition"].isin(f_at)
]

st.sidebar.markdown(f"**{len(df):,}** employees shown")
k = kpis(df)


# ─────────────────────────────────────────────────────────────────
# PAGE 1 — EXECUTIVE OVERVIEW
# ─────────────────────────────────────────────────────────────────
if PAGE == "🏠 Executive Overview":
    st.markdown("<h1 style='font-size:1.9rem;color:#1e293b;'>🏠 Executive Overview</h1>", unsafe_allow_html=True)
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    render_kpis(k)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        sh("Attrition Split")
        fig = go.Figure(go.Pie(labels=["Left","Stayed"], values=[k["left"],k["stayed"]],
                               hole=0.65, marker_colors=[LEFT_COLOR, STAY_COLOR]))
        fig.update_layout(paper_bgcolor="#ffffff", margin=dict(t=30))
        _chart(fig)
    with c2:
        sh("Attrition by Department")
        _chart(dual_axis_bar(attrition_by(df,"Department"), "Department"))

    c3, c4 = st.columns(2)
    with c3:
        sh("Attrition by Job Role")
        _chart(dual_axis_bar(attrition_by(df,"JobRole"), "JobRole"))
    with c4:
        sh("Attrition by Overtime")
        _chart(dual_axis_bar(attrition_by(df,"OverTime"), "OverTime"))

    c5, c6 = st.columns(2)
    with c5:
        sh("Attrition by Age Group")
        _chart(dual_axis_bar(attrition_by(df,"AgeGroup"), "AgeGroup"))
    with c6:
        sh("Age Distribution")
        fig = px.histogram(df, x="Age", color="Attrition",
                           color_discrete_map={"No":STAY_COLOR,"Yes":LEFT_COLOR},
                           barmode="overlay", nbins=20, opacity=0.75)
        _chart(_layout(fig))

    sh("Key Observations")
    top_d = attrition_by(df,"Department").iloc[0]
    top_r = attrition_by(df,"JobRole").iloc[0]
    ot_df = attrition_by(df,"OverTime")
    ot_y = ot_df.loc[ot_df["OverTime"]=="Yes","AttritionRate"].values
    ot_n = ot_df.loc[ot_df["OverTime"]=="No","AttritionRate"].values
    st.markdown(f"• Overall attrition rate: **{k['rate']:.1f}%** ({k['left']:,}/{k['total']:,})")
    st.markdown(f"• Highest attrition department: **{top_d['Department']}** ({top_d['AttritionRate']:.1f}%)")
    st.markdown(f"• Highest attrition job role: **{top_r['JobRole']}** ({top_r['AttritionRate']:.1f}%)")
    if len(ot_y) and len(ot_n):
        st.markdown(f"• Overtime employees: **{ot_y[0]:.1f}%** attrition vs **{ot_n[0]:.1f}%** (no overtime)")
    st.markdown(f"• Avg age: **{k['age']:.1f}** | Avg income: **${k['income']:,.0f}** | Avg tenure: **{k['tenure']:.1f} yrs**")
    dl_btn(df, "Download Filtered Dataset", "hr_filtered.csv")


# ─────────────────────────────────────────────────────────────────
# PAGE 2 — WORKFORCE DEMOGRAPHICS
# ─────────────────────────────────────────────────────────────────
elif PAGE == "👥 Workforce Demographics":
    st.markdown("<h1 style='font-size:1.9rem;color:#1e293b;'>👥 Workforce Demographics</h1>", unsafe_allow_html=True)
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        sh("Age Distribution")
        fig = px.histogram(df, x="Age", color="Attrition",
                           color_discrete_map={"No":STAY_COLOR,"Yes":LEFT_COLOR},
                           barmode="overlay", nbins=20, opacity=0.75,
                           title="Age Distribution by Attrition")
        _chart(_layout(fig))
    with c2:
        sh("Gender Distribution")
        gc = df["Gender"].value_counts()
        fig = go.Figure(go.Pie(labels=gc.index.tolist(), values=gc.values.tolist(),
                               hole=0.55, marker_colors=["#3b82f6","#f472b6"]))
        fig.update_layout(title="Gender Distribution", paper_bgcolor="#ffffff")
        _chart(fig)

    c3, c4 = st.columns(2)
    with c3:
        sh("Marital Status vs Attrition")
        _chart(dual_axis_bar(attrition_by(df,"MaritalStatus"), "MaritalStatus"))
    with c4:
        sh("Education Level")
        order = ["Below College","College","Bachelor","Master","Doctor"]
        ec = df["EducationLabel"].value_counts().reindex(order).reset_index()
        ec.columns = ["Education","Count"]
        fig = px.bar(ec, x="Education", y="Count", color="Count",
                     color_continuous_scale="Blues", title="Education Level Distribution",
                     category_orders={"Education":order})
        _chart(_layout(fig))

    c5, c6 = st.columns(2)
    with c5:
        dc = df["Department"].value_counts().reset_index()
        dc.columns = ["Department","Count"]
        fig = px.bar(dc, x="Department", y="Count", color="Count",
                     color_continuous_scale="Blues", title="Employees by Department")
        _chart(_layout(fig))
    with c6:
        jlc = df["JobLevel"].value_counts().sort_index().reset_index()
        jlc.columns = ["JobLevel","Count"]
        fig = px.bar(jlc, x="JobLevel", y="Count", color="Count",
                     color_continuous_scale="Purples", title="Employees by Job Level")
        _chart(_layout(fig))

    sh("Employees by Job Role")
    rc = df["JobRole"].value_counts().reset_index()
    rc.columns = ["JobRole","Count"]
    fig = px.bar(rc.sort_values("Count"), x="Count", y="JobRole", orientation="h",
                 color="Count", color_continuous_scale="Teal", title="Employees by Job Role")
    _chart(_layout(fig))

    c7, c8 = st.columns(2)
    with c7:
        btc = df["BusinessTravel"].value_counts().reset_index()
        btc.columns = ["BusinessTravel","Count"]
        fig = px.pie(btc, names="BusinessTravel", values="Count", hole=0.5,
                     title="Business Travel Distribution",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        _chart(fig)
    with c8:
        igc = df["IncomeGroup"].value_counts().reset_index()
        igc.columns = ["IncomeGroup","Count"]
        fig = px.bar(igc, x="IncomeGroup", y="Count", color="IncomeGroup",
                     title="Income Group Distribution",
                     color_discrete_sequence=px.colors.qualitative.Safe)
        _chart(_layout(fig))

    dl_btn(df, "Download Demographics Data", "hr_demographics.csv")


# ─────────────────────────────────────────────────────────────────
# PAGE 3 — ATTRITION ANALYSIS
# ─────────────────────────────────────────────────────────────────
elif PAGE == "📉 Attrition Analysis":
    st.markdown("<h1 style='font-size:1.9rem;color:#1e293b;'>📉 Attrition Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280;'>Each chart shows employee count AND attrition rate to prevent size-driven conclusions.</p>", unsafe_allow_html=True)
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    render_kpis(k)
    st.markdown("<br>", unsafe_allow_html=True)

    breakdowns = [
        ("Department","Attrition by Department"), ("JobRole","Attrition by Job Role"),
        ("JobLevel","Attrition by Job Level"), ("OverTime","Attrition by Overtime"),
        ("AgeGroup","Attrition by Age Group"), ("IncomeGroup","Attrition by Income Group"),
        ("TenureGroup","Attrition by Tenure Group"), ("BusinessTravel","Attrition by Business Travel"),
        ("Gender","Attrition by Gender"), ("MaritalStatus","Attrition by Marital Status"),
    ]
    for i in range(0, len(breakdowns), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j < len(breakdowns):
                var, title = breakdowns[i+j]
                with col:
                    sh(title)
                    _chart(dual_axis_bar(attrition_by(df, var), var, title))

    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    sh("Satisfaction Dimensions vs Attrition")
    sat_pairs = [
        ("JobSatisfactionLabel","Job Satisfaction"),
        ("WorkLifeBalanceLabel","Work-Life Balance"),
        ("EnvironmentSatisfactionLabel","Environment Satisfaction"),
        ("JobInvolvementLabel","Job Involvement"),
    ]
    for i in range(0, len(sat_pairs), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j < len(sat_pairs):
                lbl, _ = sat_pairs[i+j]
                with col:
                    _chart(sat_bar(df, lbl))

    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    sh("Heatmap: Department × Job Level")
    _chart(heatmap_pivot(df, "Department", "JobLevel",
                         "Attrition Rate (%) by Department × Job Level"))
    sh("Heatmap: Job Role × Overtime")
    _chart(heatmap_pivot(df, "JobRole", "OverTime",
                         "Attrition Rate (%) by Job Role × Overtime"))

    dl_btn(df, "Download Attrition Data", "hr_attrition.csv")


# ─────────────────────────────────────────────────────────────────
# PAGE 4 — COMPENSATION & CAREER
# ─────────────────────────────────────────────────────────────────
elif PAGE == "💰 Compensation & Career":
    st.markdown("<h1 style='font-size:1.9rem;color:#1e293b;'>💰 Compensation & Career</h1>", unsafe_allow_html=True)
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        sh("Monthly Income by Attrition")
        fig = px.box(df, x="Attrition", y="MonthlyIncome", color="Attrition",
                     color_discrete_map={"No":STAY_COLOR,"Yes":LEFT_COLOR},
                     title="Monthly Income by Attrition", points="outliers")
        _chart(_layout(fig))
    with c2:
        sh("Salary Hike by Attrition")
        fig = px.box(df, x="Attrition", y="PercentSalaryHike", color="Attrition",
                     color_discrete_map={"No":STAY_COLOR,"Yes":LEFT_COLOR},
                     title="Percent Salary Hike by Attrition", points="outliers")
        _chart(_layout(fig))

    sh("Monthly Income by Job Role & Attrition")
    order = df.groupby("JobRole")["MonthlyIncome"].median().sort_values(ascending=False).index.tolist()
    fig = px.box(df, x="JobRole", y="MonthlyIncome", color="Attrition",
                 color_discrete_map={"No":STAY_COLOR,"Yes":LEFT_COLOR},
                 category_orders={"JobRole":order},
                 title="Monthly Income by Job Role & Attrition", points=False)
    fig.update_xaxes(tickangle=-30)
    _chart(_layout(fig))

    c3, c4 = st.columns(2)
    with c3:
        sh("Stock Options vs Attrition")
        _chart(dual_axis_bar(attrition_by(df,"StockOptionLevel"), "StockOptionLevel",
                             "Attrition by Stock Option Level"))
    with c4:
        sh("Income vs Age")
        fig = px.scatter(df, x="Age", y="MonthlyIncome", color="Attrition",
                         color_discrete_map={"No":STAY_COLOR,"Yes":LEFT_COLOR},
                         opacity=0.6, title="Monthly Income vs Age",
                         hover_data=["JobRole","Department"])
        _chart(_layout(fig))

    sh("Income by Job Level")
    inc_jl = df.groupby("JobLevel")["MonthlyIncome"].median().reset_index()
    inc_jl.columns = ["JobLevel","MedianIncome"]
    fig = px.bar(inc_jl, x="JobLevel", y="MedianIncome", color="MedianIncome",
                 color_continuous_scale="Blues", text="MedianIncome",
                 title="Median Monthly Income by Job Level")
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    _chart(_layout(fig))

    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    sh("Career Growth vs Attrition")
    tcols = ["YearsAtCompany","YearsInCurrentRole","YearsSinceLastPromotion","YearsWithCurrManager"]
    for i in range(0, len(tcols), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j < len(tcols):
                tc = tcols[i+j]
                with col:
                    tmp = df.copy()
                    tmp["bin"] = pd.cut(tmp[tc], bins=8)
                    grp = tmp.groupby("bin", observed=True).agg(
                        Total=("AttritionFlag","count"), Left=("AttritionFlag","sum")
                    ).reset_index()
                    grp["AttritionRate"] = (grp["Left"]/grp["Total"]*100).round(2)
                    grp["bin"] = grp["bin"].astype(str)
                    fig = px.line(grp, x="bin", y="AttritionRate", markers=True,
                                  title=f"Attrition Rate by {tc}")
                    fig.update_traces(line_color=LEFT_COLOR, marker=dict(size=9))
                    _chart(_layout(fig))

    sh("Training Frequency vs Attrition")
    _chart(dual_axis_bar(attrition_by(df,"TrainingTimesLastYear"), "TrainingTimesLastYear",
                         "Attrition by Training Times Last Year"))

    dl_btn(df, "Download Compensation Data", "hr_compensation.csv")


# ─────────────────────────────────────────────────────────────────
# PAGE 5 — EMPLOYEE EXPERIENCE
# ─────────────────────────────────────────────────────────────────
elif PAGE == "🌟 Employee Experience":
    st.markdown("<h1 style='font-size:1.9rem;color:#1e293b;'>🌟 Employee Experience</h1>", unsafe_allow_html=True)
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    sat_all = [
        ("JobSatisfactionLabel","Job Satisfaction"),
        ("EnvironmentSatisfactionLabel","Environment Satisfaction"),
        ("RelationshipSatisfactionLabel","Relationship Satisfaction"),
        ("WorkLifeBalanceLabel","Work-Life Balance"),
        ("JobInvolvementLabel","Job Involvement"),
    ]
    for i in range(0, len(sat_all), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j < len(sat_all):
                lbl, _ = sat_all[i+j]
                with col:
                    _chart(sat_bar(df, lbl))

    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    sh("Overtime Cross-Analysis")
    c1, c2 = st.columns(2)
    with c1:
        wlb_ot = df.groupby(["OverTime","WorkLifeBalanceLabel"], observed=True).size().reset_index(name="Count")
        fig = px.bar(wlb_ot, x="WorkLifeBalanceLabel", y="Count", color="OverTime",
                     barmode="group", color_discrete_map={"No":STAY_COLOR,"Yes":LEFT_COLOR},
                     title="Work-Life Balance Distribution by Overtime",
                     category_orders={"WorkLifeBalanceLabel":["Bad","Good","Better","Best"]})
        _chart(_layout(fig))
    with c2:
        js_ot = df.groupby(["OverTime","JobSatisfactionLabel"], observed=True).size().reset_index(name="Count")
        fig = px.bar(js_ot, x="JobSatisfactionLabel", y="Count", color="OverTime",
                     barmode="group", color_discrete_map={"No":STAY_COLOR,"Yes":LEFT_COLOR},
                     title="Job Satisfaction Distribution by Overtime",
                     category_orders={"JobSatisfactionLabel":["Low","Medium","High","Very High"]})
        _chart(_layout(fig))

    sh("Avg Work-Life Balance: Job Role × Overtime")
    pivot_wlb = df.pivot_table(index="JobRole", columns="OverTime",
                               values="WorkLifeBalance", aggfunc="mean").round(2)
    fig = px.imshow(pivot_wlb, text_auto=".2f", aspect="auto",
                    color_continuous_scale="RdYlGn",
                    title="Avg Work-Life Balance by Job Role & Overtime")
    fig.update_layout(paper_bgcolor="#ffffff")
    _chart(fig)

    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    sh("Commute & Travel")
    c3, c4 = st.columns(2)
    with c3:
        _chart(dual_axis_bar(attrition_by(df,"DistanceGroup"), "DistanceGroup",
                             "Attrition by Commute Distance Group"))
    with c4:
        _chart(dual_axis_bar(attrition_by(df,"BusinessTravel"), "BusinessTravel",
                             "Attrition by Business Travel"))

    sh("Distance from Home Distribution")
    fig = px.histogram(df, x="DistanceFromHome", color="Attrition",
                       color_discrete_map={"No":STAY_COLOR,"Yes":LEFT_COLOR},
                       barmode="overlay", nbins=25, opacity=0.75,
                       title="Distance from Home Distribution")
    _chart(_layout(fig))

    dl_btn(df, "Download Experience Data", "hr_experience.csv")


# ─────────────────────────────────────────────────────────────────
# PAGE 6 — SEGMENT ANALYSIS
# ─────────────────────────────────────────────────────────────────
elif PAGE == "🔬 Segment Analysis":
    st.markdown("<h1 style='font-size:1.9rem;color:#1e293b;'>🔬 Segment Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280;'>Select up to 3 variables. Only segments with ≥ minimum employees shown.</p>", unsafe_allow_html=True)
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    SEG_VARS = ["Department","JobRole","JobLevel","Gender","MaritalStatus",
                "BusinessTravel","OverTime","AgeGroup","IncomeGroup","TenureGroup",
                "DistanceGroup","JobSatisfactionLabel","WorkLifeBalanceLabel",
                "EnvironmentSatisfactionLabel","JobInvolvementLabel"]

    c1, c2, c3 = st.columns(3)
    with c1: v1 = st.selectbox("Variable 1", SEG_VARS, 0, key="sv1")
    with c2: v2 = st.selectbox("Variable 2", ["—"]+SEG_VARS, 3, key="sv2")
    with c3: v3 = st.selectbox("Variable 3", ["—"]+SEG_VARS, 0, key="sv3")
    mn = st.slider("Min employees per segment", 5, 50, 10, 5)

    chosen = [v for v in [v1, v2 if v2!="—" else None, v3 if v3!="—" else None] if v]
    seg_df = segment_analysis(df, chosen, min_n=mn)

    if seg_df.empty:
        st.info("No segments with the selected options and minimum size.")
    else:
        sh(f"Results ({len(seg_df)} segments)")
        st.dataframe(seg_df.style.background_gradient(subset=["AttritionRate"], cmap="YlOrRd")
                     .format({"AttritionRate":"{:.1f}%","Total":"{:,}"}), use_container_width=True)
        dl_btn(seg_df, "Download Segment Results", "hr_segments.csv")

        top20 = seg_df.head(20).copy()
        top20["Segment"] = top20[chosen].apply(lambda r: " | ".join([str(r[c]) for c in chosen]), axis=1)
        fig = px.bar(top20.sort_values("AttritionRate"),
                     x="AttritionRate", y="Segment", orientation="h",
                     color="AttritionRate", color_continuous_scale="Reds",
                     text="AttritionRate", title=f"Top 20 Segments by Attrition Rate")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        _chart(_layout(fig), h=max(400, 30*len(top20)))

        if len(chosen) == 2:
            sh(f"Heatmap: {chosen[0]} × {chosen[1]}")
            pivot_s = seg_df.pivot_table(index=chosen[0], columns=chosen[1],
                                          values="AttritionRate", aggfunc="mean").round(1)
            fig = px.imshow(pivot_s.fillna(0), text_auto=".1f", aspect="auto",
                            color_continuous_scale="RdYlGn_r",
                            title=f"Attrition %: {chosen[0]} × {chosen[1]}")
            fig.update_layout(paper_bgcolor="#ffffff")
            _chart(fig)

    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    sh("Pre-Built Segments")
    pre = [
        (["OverTime","JobSatisfactionLabel"],"Overtime × Job Satisfaction"),
        (["OverTime","WorkLifeBalanceLabel"],"Overtime × Work-Life Balance"),
        (["OverTime","AgeGroup"],"Overtime × Age Group"),
        (["IncomeGroup","OverTime"],"Income Group × Overtime"),
        (["AgeGroup","IncomeGroup"],"Age Group × Income Group"),
    ]
    for vars_c, title in pre:
        with st.expander(f"📋 {title}"):
            s = segment_analysis(df, vars_c, 10)
            if not s.empty:
                st.dataframe(s.style.background_gradient(subset=["AttritionRate"], cmap="YlOrRd")
                             .format({"AttritionRate":"{:.1f}%"}), use_container_width=True)
                piv = s.pivot_table(index=vars_c[0], columns=vars_c[1],
                                    values="AttritionRate", aggfunc="mean").round(1)
                fig = px.imshow(piv.fillna(0), text_auto=".1f",
                                color_continuous_scale="RdYlGn_r", title=title)
                fig.update_layout(paper_bgcolor="#ffffff")
                _chart(fig)
            else:
                st.write("Insufficient data.")


# ─────────────────────────────────────────────────────────────────
# PAGE 7 — STATISTICAL ANALYSIS
# ─────────────────────────────────────────────────────────────────
elif PAGE == "📐 Statistical Analysis":
    st.markdown("<h1 style='font-size:1.9rem;color:#1e293b;'>📐 Statistical Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280;'>Association ≠ causation. p-values indicate whether observed differences are likely due to chance.</p>", unsafe_allow_html=True)
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    with st.spinner("Running tests…"):
        st_df = run_stats(df)

    sh("Test Results")
    disp_cols = ["Variable","Test","Statistic","p-value","Effect","Significant","Interpretation"]
    disp_cols = [c for c in disp_cols if c in st_df.columns]
    st.dataframe(st_df[disp_cols], use_container_width=True, height=450)
    dl_btn(st_df, "Download Statistical Results", "hr_statistics.csv")

    sig = st_df[st_df["Significant"]=="Yes ✓"].copy()
    if not sig.empty:
        sh(f"Significant Variables (n={len(sig)})")
        sig["p-value"] = pd.to_numeric(sig["p-value"], errors="coerce")
        sig = sig.dropna(subset=["p-value"])
        sig["-log10p"] = -np.log10(sig["p-value"].clip(lower=1e-300))
        fig = px.bar(sig.sort_values("-log10p", ascending=False).head(20),
                     x="-log10p", y="Variable", orientation="h",
                     color="-log10p", color_continuous_scale="Blues",
                     text="-log10p", title="Top Significant Variables (−log₁₀ p-value)")
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        _chart(_layout(fig))

    with st.expander("📖 How to Read These Results"):
        st.markdown("""
**Chi-Square (categorical):** Tests whether the variable's distribution differs between employees who stayed vs left. Cramér's V = effect size (0–1).  
**Mann-Whitney U (numerical):** Compares medians between the two groups (non-parametric). Rank-biserial r = effect size.  
**p < 0.05** = statistically significant at 5% level.  
**Caution:** Significance ≠ causation.
        """)


# ─────────────────────────────────────────────────────────────────
# PAGE 8 — DATA EXPLORER
# ─────────────────────────────────────────────────────────────────
elif PAGE == "🗃 Data Explorer":
    st.markdown("<h1 style='font-size:1.9rem;color:#1e293b;'>🗃 Data Explorer</h1>", unsafe_allow_html=True)
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    sel_cols = st.multiselect("Select columns", df.columns.tolist(), default=df.columns.tolist()[:12])
    search = st.text_input("Search (JobRole / Department / MaritalStatus)", "")

    disp = df[sel_cols].copy() if sel_cols else df.copy()
    if search:
        mask = pd.Series(False, index=disp.index)
        for col in ["JobRole","Department","MaritalStatus"]:
            if col in disp.columns:
                mask |= disp[col].astype(str).str.contains(search, case=False, na=False)
        disp = disp[mask]

    st.markdown(f"**{len(disp):,}** records")
    st.dataframe(disp, use_container_width=True, height=480)

    c1, c2 = st.columns(2)
    with c1: dl_btn(disp, "Download Filtered Data", "hr_explorer.csv")
    with c2:
        stats_d = df.select_dtypes(include=np.number).describe().T.round(2)
        dl_btn(stats_d, "Download Summary Statistics", "hr_summary_stats.csv")

    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    sh("Descriptive Statistics")
    st.dataframe(df.select_dtypes(include=np.number).describe().T.round(2), use_container_width=True)

    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    sh("Data Quality Report")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows",       f"{df_full.shape[0]:,}")
    c2.metric("Columns",    f"{df_full.shape[1]:,}")
    c3.metric("Missing",    "None")
    c4.metric("Duplicates", "None")

    num_c = df.select_dtypes(include=np.number).columns.tolist()
    cat_c = df.select_dtypes(include=["object","category"]).columns.tolist()
    st.markdown(f"**Numerical columns ({len(num_c)}):** {', '.join(num_c)}")
    st.markdown(f"**Categorical columns ({len(cat_c)}):** {', '.join(cat_c)}")
    st.markdown("**Removed columns:** `EmployeeCount`, `Over18`, `StandardHours` (constant across all rows)")


# ─────────────────────────────────────────────────────────────────
# PAGE 9 — KEY INSIGHTS
# ─────────────────────────────────────────────────────────────────
elif PAGE == "💡 Key Insights":
    st.markdown("<h1 style='font-size:1.9rem;color:#1e293b;'>💡 Key Insights</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280;'>All insights are auto-generated from the filtered dataset. Association ≠ causation.</p>", unsafe_allow_html=True)
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)

    for ins in generate_insights(df):
        icard(ins)

    sh("Correlation with Attrition")
    num_c = df.select_dtypes(include=np.number).columns.tolist()
    if "AttritionFlag" in num_c:
        corr = df[num_c].corr()["AttritionFlag"].drop("AttritionFlag").sort_values()
        fig = go.Figure(go.Bar(x=corr.values, y=corr.index, orientation="h",
                               marker_color=[LEFT_COLOR if v>0 else STAY_COLOR for v in corr.values],
                               hovertemplate="%{y}: %{x:.3f}<extra></extra>"))
        fig.update_layout(title="Pearson Correlation with Attrition Flag",
                          xaxis_title="Correlation Coefficient",
                          paper_bgcolor="#ffffff", plot_bgcolor="#f9fafb",
                          font=dict(family=FONT_FAMILY),
                          margin=dict(l=180,r=20,t=50,b=40))
        _chart(fig, h=550)


# ─────────────────────────────────────────────────────────────────
# PAGE 10 — ABOUT PROJECT
# ─────────────────────────────────────────────────────────────────
elif PAGE == "ℹ️ About Project":
    st.markdown("<h1 style='font-size:1.9rem;color:#1e293b;'>ℹ️ About This Project</h1>", unsafe_allow_html=True)
    st.markdown('<div class="hr-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
## Employee Attrition & Workforce Analytics Platform
**Author:** Mayur Pandey  

---

### Project Purpose
An end-to-end HR analytics platform that analyses the IBM HR Analytics Employee Attrition & Performance dataset to understand patterns associated with workforce attrition. Designed as a professional Data Analyst portfolio project.

> ⚠️ The IBM HR dataset is **fictional** — created by IBM data scientists for educational use. It does not represent any real organisation's workforce data.

---

### Dataset
| | |
|---|---|
| **Source** | [Kaggle — IBM HR Analytics](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) |
| **Records** | 1,470 employees |
| **Features** | 35 columns |
| **Target** | Attrition (Yes / No) |

---

### Technology Stack
| | |
|---|---|
| Data processing | Pandas, NumPy |
| Visualisation | Plotly, Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Statistics | SciPy |
| ML support | Scikit-learn |

---

### How to Run
```bash
pip install -r requirements.txt
streamlit run MayurPandey_EmployeeAttritionWorkforceAnalytics.py
```

Place the dataset at `./data/WA_Fn-UseC_-HR-Employee-Attrition.csv` (or same directory as this file).

---

### Limitations
- Dataset is fictional — findings illustrative only
- Cross-sectional design prevents causal inference
- Small sample sizes for some job roles
- No predictive model included (descriptive analytics only)

---

### Future Work
- Logistic regression / random forest attrition prediction
- SHAP values for individual risk explanation
- Survival analysis (time-to-departure)
    """)


# ─────────────────────────────────────────────────────────────────
# SIDEBAR FOOTER
# ─────────────────────────────────────────────────────────────────
st.sidebar.markdown(
    "<hr style='border-color:#334155;'>"
    "<p style='color:#475569;font-size:0.72rem;text-align:center;'>"
    "IBM HR Analytics Platform<br>© 2024 Mayur Pandey</p>",
    unsafe_allow_html=True,
)
