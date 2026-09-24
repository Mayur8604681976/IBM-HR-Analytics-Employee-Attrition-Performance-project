# Employee Attrition & Workforce Analytics
### An Interactive HR Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20+-purple.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Project Overview

This is a complete, professional, interactive HR analytics platform built with Python and Streamlit.  
It analyses the IBM HR Analytics Employee Attrition & Performance dataset to identify patterns associated with employee attrition across demographics, compensation, satisfaction, overtime, and career growth.

> ⚠️ **Disclaimer:** The IBM HR dataset is fictional and was created by IBM data scientists for analytical demonstration. It does not represent real IBM workforce statistics or any actual organisation's data.

---

## 🎯 Business Problem

Organisations face significant costs from employee attrition — replacement costs, productivity loss, and knowledge drain. This project explores:

- Which employee characteristics are associated with higher attrition rates?
- Do overtime, satisfaction, and work-life balance differ between employees who left vs stayed?
- How do compensation and career progression relate to attrition patterns?
- Are observed differences statistically significant?

---

## 🏆 Objectives

1. Perform rigorous exploratory data analysis of the IBM HR dataset
2. Identify variables associated with employee attrition
3. Apply appropriate statistical tests (chi-square, Mann-Whitney U)
4. Build an interactive multi-page Streamlit dashboard
5. Auto-generate evidence-based insights from the data
6. Present a polished, portfolio-quality analytics project

---

## 📂 Dataset

| Attribute | Value |
|---|---|
| **Source** | [Kaggle — IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) |
| **Records** | 1,470 employees |
| **Features** | 35 columns |
| **Target** | `Attrition` (Yes / No) |

**Key variable groups:**
- Demographics: Age, Gender, MaritalStatus
- Job attributes: Department, JobRole, JobLevel, BusinessTravel
- Compensation: MonthlyIncome, PercentSalaryHike, StockOptionLevel
- Satisfaction: JobSatisfaction, EnvironmentSatisfaction, WorkLifeBalance
- Career: YearsAtCompany, YearsInCurrentRole, YearsSinceLastPromotion
- Work style: OverTime, TrainingTimesLastYear

---

## 🛠 Technology Stack

| Layer | Technology |
|---|---|
| Data Processing | Python, Pandas, NumPy |
| Visualisation | Plotly (interactive), Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Statistics | SciPy (chi-square, Mann-Whitney U) |
| ML Support | Scikit-learn |

---

## 🗂 Project Architecture

```
IBM-HR-Analytics/
│
├── data/
│   └── WA_Fn-UseC_-HR-Employee-Attrition.csv
│
├── app.py                        ← Main Streamlit application
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py            ← CSV loading, validation, quality report
│   ├── data_cleaning.py          ← Cleaning, feature engineering, KPIs
│   ├── analysis.py               ← Attrition rates, segment analysis, insights
│   ├── statistics.py             ← Chi-square, Mann-Whitney U tests
│   ├── visualizations.py         ← Plotly chart factory functions
│   └── utils.py                  ← CSS injection, KPI cards, download buttons
│
├── notebooks/
│   └── HR_Analytics_EDA.ipynb   ← Comprehensive EDA notebook
│
├── visualizations/               ← Saved chart images
├── assets/                       ← Static assets
│
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## 📊 Analysis Performed

### Workforce Overview
- Total employees, attrition count, and overall rate
- Demographic profile (age, gender, education, marital status)

### Attrition Analysis
- Attrition by department, job role, job level
- Attrition by age group, income group, tenure group
- Attrition by overtime, business travel, gender, marital status
- Dual-axis charts: count + rate simultaneously to prevent size-driven bias

### Compensation & Career
- Monthly income distribution by attrition status
- Income by job role and job level
- Salary hike and stock options vs attrition
- Career progression metrics (promotions, role tenure, manager tenure)

### Employee Experience
- All four satisfaction dimensions vs attrition
- Overtime interactions with satisfaction, work-life balance, income
- Commute distance and business travel analysis

### Segment Analysis
- Interactive multi-variable segment explorer (up to 3 variables)
- Pre-built segments: Overtime × Job Satisfaction, Income Group × Overtime, etc.

### Statistical Analysis
- Chi-square test for all categorical variables
- Mann-Whitney U test for all numerical variables
- Effect sizes (Cramér's V, rank-biserial r)
- p-values with significance indicators

---

## 🖥 Dashboard Features

| Page | Key Features |
|---|---|
| Executive Overview | 7 KPI cards, 4 attrition charts, auto key observations |
| Workforce Demographics | Age/gender/education/job distribution charts |
| Attrition Analysis | 10+ breakdowns, dual-axis charts, heatmaps |
| Compensation & Career | Income box plots, career growth lines, scatter charts |
| Employee Experience | Satisfaction heatmaps, overtime cross-tabs |
| Segment Analysis | Interactive variable selector, segment heatmaps |
| Statistical Analysis | Full test results table, -log10(p) significance chart |
| Data Explorer | Filterable table, column selector, text search, download |
| Key Insights | 10 auto-generated evidence-based insights |
| About Project | Full project documentation |

**Global sidebar filters:** Department, Job Role, Gender, Age Group, Job Level, Overtime, Business Travel, Marital Status, Attrition — all charts update dynamically.

---

## 💡 Key Insights (Dataset-Derived)

> Note: All insights are descriptive. Association ≠ causation.

1. **Overtime** employees show substantially higher observed attrition rates
2. **Low job satisfaction** is associated with higher attrition
3. **Sales department** shows the highest attrition rate among departments
4. **Employees who left** had lower median monthly incomes
5. **No stock options** (level 0) correlates with higher attrition
6. **Younger employees** (under 25) show the highest attrition rate by age group
7. **Frequent business travel** is associated with higher attrition
8. **Work-life balance score 1** ("Bad") is associated with highest attrition
9. **Early-career employees** (0-2 years) show elevated attrition
10. **Long periods without promotion** associated with higher attrition in some bins

---

## 📸 Screenshots

> *(Add dashboard screenshots here after running the application.)*

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip

### 1. Clone the repository
```bash
git clone https://github.com/your-username/IBM-HR-Analytics.git
cd IBM-HR-Analytics
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add the dataset
Place `WA_Fn-UseC_-HR-Employee-Attrition.csv` in the `data/` folder.

Download from Kaggle:  
https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset

### 4. Run the dashboard
```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

### 5. Run the notebook
```bash
jupyter notebook notebooks/HR_Analytics_EDA.ipynb
```

---

## ⚠️ Limitations

- Dataset is fictional; findings cannot be generalised to real organisations
- Cross-sectional data prevents causal inference
- Some job roles have small sample sizes
- No predictive model is included (this is a descriptive analytics project)

---

## 🔮 Future Improvements

- Add logistic regression / random forest attrition prediction
- SHAP explainability for individual employee risk
- Survival analysis (time-to-departure)
- Benchmarking against industry attrition rates
- HR department user authentication layer

---

## 👤 Author

**Mayur Pandey**  
Data Analyst | Python | SQL | Machine Learning  

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

The IBM HR dataset is provided under the [CC0: Public Domain](https://creativecommons.org/publicdomain/zero/1.0/) license on Kaggle.
