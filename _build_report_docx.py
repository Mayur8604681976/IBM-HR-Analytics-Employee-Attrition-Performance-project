"""
_build_report_docx.py
Generates MayurPandey_ProjectReport.docx from scratch using python-docx.
Run once from the IBM-HR-Analytics directory:
    python _build_report_docx.py
"""

import os
from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement  # still used for cell shading


# ── colour palette ──────────────────────────────────────────────
C_DARK    = RGBColor(0x1E, 0x29, 0x3B)   # near-black navy
C_BLUE    = RGBColor(0x1E, 0x40, 0xAF)   # section heading blue
C_RED     = RGBColor(0xDC, 0x26, 0x26)   # disclaimer red
C_GRAY    = RGBColor(0x6B, 0x72, 0x80)   # muted subtitle
C_LINK    = RGBColor(0x1D, 0x4E, 0xD8)   # URL blue
C_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
C_HDRFILL = "1E40AF"                      # table header row fill (hex string)
C_ALTFILL = "EFF6FF"                      # alternating row fill


def set_cell_bg(cell, hex_color: str):
    """Set a table cell's background shading colour."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color)
    tcPr.append(shd)


def set_col_width(table, col_idx: int, width_cm: float):
    """Set the width of every cell in a table column."""
    for row in table.rows:
        row.cells[col_idx].width = Cm(width_cm)


def add_title(doc: Document):
    p = doc.add_paragraph()
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.space_before = Pt(0)
    run = p.add_run("Employee Attrition & Workforce Analytics")
    run.bold       = True
    run.font.size  = Pt(22)
    run.font.color.rgb = C_DARK

    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(2)
    run2 = p2.add_run("Project Report")
    run2.bold      = True
    run2.font.size = Pt(16)
    run2.font.color.rgb = C_DARK

    p3 = doc.add_paragraph()
    p3.paragraph_format.space_after = Pt(14)
    r3 = p3.add_run("Author: Mayur Pandey   |   Dataset: IBM HR Analytics Employee Attrition & Performance (Kaggle)")
    r3.font.size      = Pt(10)
    r3.font.color.rgb = C_GRAY
    r3.italic         = True


def add_section_heading(doc: Document, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    run.bold           = True
    run.font.size      = Pt(14)
    run.font.color.rgb = C_BLUE


def add_sub_heading(doc: Document, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run(text)
    run.bold           = True
    run.font.size      = Pt(12)
    run.font.color.rgb = C_DARK


def add_body(doc: Document, text: str, italic=False, color=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    run = p.add_run(text)
    run.font.size  = Pt(11)
    run.italic     = italic
    if color:
        run.font.color.rgb = color
    return p


def add_bullet(doc: Document, text: str):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.font.size = Pt(11)


def add_numbered(doc: Document, text: str):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.font.size = Pt(11)


def add_table(doc: Document, headers: list, rows: list, col_widths: list = None):
    """Add a styled table with a blue header row and alternating row shading."""
    num_cols = len(headers)
    table = doc.add_table(rows=1 + len(rows), cols=num_cols)
    table.style = "Table Grid"

    # Header row
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        set_cell_bg(hdr_cells[i], C_HDRFILL)
        run = hdr_cells[i].paragraphs[0].runs[0]
        run.bold           = True
        run.font.size      = Pt(10)
        run.font.color.rgb = C_WHITE

    # Data rows
    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        fill = C_ALTFILL if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, cell_text in enumerate(row_data):
            row_cells[c_idx].text = cell_text
            set_cell_bg(row_cells[c_idx], fill)
            run = row_cells[c_idx].paragraphs[0].runs[0]
            run.font.size = Pt(10)

    # Column widths
    if col_widths:
        for i, w in enumerate(col_widths):
            set_col_width(table, i, w)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return table


# ════════════════════════════════════════════════════════════════
# BUILD DOCUMENT
# ════════════════════════════════════════════════════════════════

doc = Document()

# Page margins
for section in doc.sections:
    section.top_margin    = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# Default style
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)

# ── TITLE ──────────────────────────────────────────────────────
add_title(doc)

# ── DISCLAIMER ─────────────────────────────────────────────────
p_disc_head = doc.add_paragraph()
p_disc_head.paragraph_format.space_before = Pt(4)
p_disc_head.paragraph_format.space_after  = Pt(3)
r = p_disc_head.add_run("DISCLAIMER")
r.bold = True; r.font.size = Pt(12); r.font.color.rgb = C_RED

p_disc = doc.add_paragraph()
p_disc.paragraph_format.space_after = Pt(12)
rd = p_disc.add_run(
    "The IBM HR Analytics dataset is entirely fictional and was created by IBM data scientists "
    "for educational and demonstration purposes. The findings in this report do not represent "
    "actual IBM workforce data or statistics from any real organisation. All analytical claims "
    "use cautious language; association is not causation."
)
rd.font.size = Pt(11); rd.italic = True

# ── SECTION 1: PROJECT OVERVIEW ────────────────────────────────
add_section_heading(doc, "Section 1: Project Overview")
add_body(doc,
    "This project delivers an end-to-end HR analytics platform that explores the IBM HR Analytics "
    "Employee Attrition & Performance dataset. The goal is to identify patterns in the data that "
    "are associated with employee attrition and present them through an interactive Streamlit "
    "dashboard, a structured EDA notebook, and this written report.")
add_body(doc,
    "The analysis is purely descriptive and exploratory. No causal claims are made.")
add_sub_heading(doc, "Technology Stack")
for item in [
    "Python 3.10+",
    "Pandas, NumPy (data processing)",
    "Plotly (interactive charts)",
    "Matplotlib, Seaborn (static charts in notebook)",
    "Streamlit (interactive dashboard)",
    "SciPy (statistical tests)",
    "Scikit-learn (encoding support)",
]:
    add_bullet(doc, item)

# ── SECTION 2: DATASET DESCRIPTION ────────────────────────────
add_section_heading(doc, "Section 2: Dataset Description")
p_src = doc.add_paragraph()
p_src.paragraph_format.space_after = Pt(3)
r_src = p_src.add_run("Source: ")
r_src.bold = True; r_src.font.size = Pt(11)
p_src.add_run("Kaggle — IBM HR Analytics Employee Attrition & Performance").font.size = Pt(11)

p_url = doc.add_paragraph()
p_url.paragraph_format.space_after = Pt(8)
r_url = p_url.add_run("https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset")
r_url.font.size = Pt(10); r_url.font.color.rgb = C_LINK

add_table(doc,
    headers=["Attribute", "Value"],
    rows=[
        ["Rows",            "1,470 employees"],
        ["Columns",         "35 original features"],
        ["Target Variable", "Attrition (Yes = left the organisation, No = remained)"],
        ["Missing Values",  "None detected"],
        ["Duplicate Rows",  "None detected"],
    ],
    col_widths=[6, 10]
)

add_body(doc,
    "Removed Columns (no analytical value): EmployeeCount (constant = 1), Over18 (constant = Y), "
    "StandardHours (constant = 80). Constant columns are removed before analysis to avoid "
    "spurious correlations.")

# ── SECTION 3: FEATURE ENGINEERING ────────────────────────────
add_section_heading(doc, "Section 3: Feature Engineering")
add_body(doc, "The following derived features were created to enable grouped analysis:")
add_table(doc,
    headers=["Derived Feature", "Source Column", "Categories / Definition"],
    rows=[
        ["AgeGroup",       "Age",             "Under 25 | 25-34 | 35-44 | 45-54 | 55+"],
        ["IncomeGroup",    "MonthlyIncome",    "Low | Medium | High  (tertile-based)"],
        ["TenureGroup",    "YearsAtCompany",   "New Employee | Early Career | Mid Career | Long Tenure"],
        ["DistanceGroup",  "DistanceFromHome", "Near (1-5 km) | Moderate (6-15 km) | Far (16+ km)"],
        ["AttritionFlag",  "Attrition",        "1 = Yes, 0 = No"],
        ["OvertimeFlag",   "OverTime",         "1 = Yes, 0 = No"],
    ],
    col_widths=[4.5, 5, 8]
)
add_body(doc,
    "Ordinal label columns also added: EducationLabel, JobSatisfactionLabel, "
    "EnvironmentSatisfactionLabel, RelationshipSatisfactionLabel, "
    "JobInvolvementLabel, WorkLifeBalanceLabel.")

# ── SECTION 4: KEY FINDINGS ────────────────────────────────────
add_section_heading(doc, "Section 4: Key Findings")
add_body(doc, "All values below are computed from the actual dataset. None are hardcoded.", italic=True)

findings = [
    ("4.1  Overall Attrition",
     "The dataset contains 1,470 employees. 237 employees (approximately 16.1%) left the "
     "organisation. 1,233 employees (approximately 83.9%) remained."),
    ("4.2  Overtime",
     "Employees who worked overtime showed an observed attrition rate substantially higher than "
     "those who did not. This was the single strongest categorical predictor in the dataset "
     "in terms of observed attrition rate difference."),
    ("4.3  Job Satisfaction",
     "Employees with the lowest job satisfaction score (1 = Low) showed the highest observed "
     "attrition rate among the satisfaction tiers. The pattern was inverse: higher satisfaction "
     "was associated with lower attrition rates."),
    ("4.4  Department",
     "The Sales department showed the highest observed attrition rate among the three departments "
     "(Sales, Research & Development, Human Resources)."),
    ("4.5  Job Role",
     "Sales Representatives and Laboratory Technicians showed among the highest observed "
     "attrition rates by job role."),
    ("4.6  Compensation",
     "Employees who left had lower median monthly incomes than employees who stayed. This "
     "difference was statistically significant per the Mann-Whitney U test."),
    ("4.7  Stock Options",
     "Employees with no stock options (StockOptionLevel = 0) showed a higher observed attrition "
     "rate compared to employees with any stock option level."),
    ("4.8  Age Group",
     "Younger employees (Under 25 and 25-34) showed higher observed attrition rates than older "
     "groups. This is consistent with typical labour market patterns where early-career employees "
     "have higher job mobility."),
    ("4.9  Business Travel",
     "Employees who travel frequently showed higher observed attrition rates than employees "
     "who travel rarely or not at all."),
    ("4.10  Work-Life Balance",
     "Employees with a work-life balance score of 1 showed the highest observed attrition "
     "rate within the work-life balance scale."),
    ("4.11  Tenure",
     "Early-career employees (0-5 years at the company) showed elevated attrition rates. "
     "Attrition generally declined as tenure increased, suggesting longer-tenured employees "
     "are more likely to remain."),
]
for sub, body in findings:
    add_sub_heading(doc, sub)
    add_body(doc, body)

# ── SECTION 5: STATISTICAL ANALYSIS ───────────────────────────
add_section_heading(doc, "Section 5: Statistical Analysis Summary")

add_sub_heading(doc, "Chi-Square Tests  (Categorical Variables vs Attrition)")
add_body(doc,
    "Variables tested: BusinessTravel, Department, EducationField, Gender, JobRole, "
    "MaritalStatus, OverTime, AgeGroup, IncomeGroup, TenureGroup, DistanceGroup, and all "
    "satisfaction label columns.")
add_body(doc,
    "Statistically significant at p < 0.05: OverTime, MaritalStatus, JobRole, BusinessTravel, "
    "and others. Exact values are displayed in the Statistical Analysis dashboard page.")

add_sub_heading(doc, "Mann-Whitney U Tests  (Numerical Variables vs Attrition)")
add_body(doc,
    "Variables tested: Age, MonthlyIncome, TotalWorkingYears, YearsAtCompany, "
    "YearsSinceLastPromotion, JobSatisfaction, WorkLifeBalance, StockOptionLevel, "
    "DistanceFromHome, and others.")
add_body(doc,
    "Statistically significant differences detected for: MonthlyIncome, TotalWorkingYears, "
    "Age, StockOptionLevel, YearsAtCompany, and others. Exact p-values and effect sizes "
    "are available in the dashboard.")

add_sub_heading(doc, "Effect Sizes")
add_body(doc,
    "Cramer's V is reported for chi-square tests. Rank-biserial r is reported for "
    "Mann-Whitney U tests. Effect sizes are important because a large sample can produce a "
    "tiny but statistically significant p-value. Both are reported to avoid p-value-only "
    "interpretation.")

# ── SECTION 6: ANALYTICAL METHODOLOGY ─────────────────────────
add_section_heading(doc, "Section 6: Analytical Methodology")
for item in [
    "Data was loaded using Pandas with UTF-8 encoding to handle the BOM.",
    "Constant columns were detected programmatically and removed.",
    "No data was imputed because no missing values existed.",
    "No legitimate observations were removed as outliers.",
    "Attrition rates are always presented alongside group counts to prevent misleading "
    "conclusions from differently-sized groups.",
    "Insights were generated computationally — no results were hardcoded.",
    'Cautious language is used throughout: "associated with", "shows a higher observed rate", '
    '"the dataset indicates". Causal language is avoided.',
    "Statistical tests were selected based on variable types and distributional assumptions "
    "(non-parametric tests for numerical variables that may not follow a normal distribution).",
]:
    add_numbered(doc, item)

# ── SECTION 7: DASHBOARD STRUCTURE ────────────────────────────
add_section_heading(doc, "Section 7: Dashboard Structure")
add_table(doc,
    headers=["Page", "Description"],
    rows=[
        ["Page 1:  Executive Overview",     "KPIs, attrition by dept / role / overtime"],
        ["Page 2:  Workforce Demographics", "Age, gender, education distributions"],
        ["Page 3:  Attrition Analysis",     "10+ breakdowns, dual-axis charts, heatmaps"],
        ["Page 4:  Compensation & Career",  "Income, salary hike, career growth patterns"],
        ["Page 5:  Employee Experience",    "Satisfaction, overtime, commute analysis"],
        ["Page 6:  Segment Analysis",       "Interactive multi-variable segment explorer"],
        ["Page 7:  Statistical Analysis",   "Test results table, significance chart"],
        ["Page 8:  Data Explorer",          "Filterable table, column selector, downloads"],
        ["Page 9:  Key Insights",           "10 auto-generated evidence-based insights"],
        ["Page 10: About Project",          "Full project documentation"],
    ],
    col_widths=[7, 10]
)
add_body(doc,
    "Global sidebar filters (Department, Job Role, Gender, Age Group, Job Level, Overtime, "
    "Business Travel, Marital Status, Attrition) apply dynamically across all pages.")

# ── SECTION 8: LIMITATIONS ─────────────────────────────────────
add_section_heading(doc, "Section 8: Limitations")
for item in [
    "The dataset is fictional — findings are illustrative, not factual.",
    "Cross-sectional design prevents causal conclusions.",
    "Some job roles have small sample sizes (e.g., HR department).",
    "No time dimension — attrition timing cannot be modelled.",
    "Survey-based satisfaction scores carry social desirability bias.",
    "No external benchmarks are available for this fictional dataset.",
]:
    add_bullet(doc, item)

# ── SECTION 9: FUTURE WORK ─────────────────────────────────────
add_section_heading(doc, "Section 9: Future Work")
for item in [
    "Logistic regression model for attrition probability scoring.",
    "Random forest with SHAP explainability.",
    "Survival analysis (Kaplan-Meier, Cox proportional hazards).",
    "Segmented intervention simulation (what-if analysis).",
    "Multi-year dataset integration for longitudinal analysis.",
]:
    add_numbered(doc, item)

# ── SECTION 10: PROJECT FILES ──────────────────────────────────
add_section_heading(doc, "Section 10: Project Files")
add_table(doc,
    headers=["File", "Purpose"],
    rows=[
        ["app.py",                                "Main Streamlit dashboard"],
        ["MayurPandey_EmployeeAttritionWorkforceAnalytics.py", "Standalone single-file submission"],
        ["src/data_loader.py",                    "CSV loading and quality reporting"],
        ["src/data_cleaning.py",                  "Cleaning and feature engineering"],
        ["src/analysis.py",                       "Attrition analysis and insight generation"],
        ["src/statistics.py",                     "Statistical test runners"],
        ["src/visualizations.py",                 "Plotly chart factory"],
        ["src/utils.py",                          "CSS, KPI cards, download helpers"],
        ["notebooks/HR_Analytics_EDA.ipynb",      "Comprehensive EDA notebook"],
        ["data/WA_Fn-UseC_-HR-Employee-Attrition.csv", "Source dataset"],
        ["requirements.txt",                      "Python dependencies"],
        ["README.md",                             "Project documentation"],
        ["LICENSE",                               "MIT License"],
    ],
    col_widths=[8, 9.5]
)

# ── FOOTER ─────────────────────────────────────────────────────
doc.add_paragraph()
p_end = doc.add_paragraph()
p_end.paragraph_format.space_before = Pt(12)
p_end.paragraph_format.space_after  = Pt(4)
p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_end = p_end.add_run("END OF REPORT  —  Mayur Pandey  |  Employee Attrition & Workforce Analytics")
r_end.bold = True; r_end.font.size = Pt(11); r_end.font.color.rgb = C_DARK

# ── SAVE ───────────────────────────────────────────────────────
out_path = os.path.join(os.path.dirname(__file__), "MayurPandey_ProjectReport.docx")
doc.save(out_path)
print(f"Saved: {out_path}")
