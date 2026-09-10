# Care Transition Efficiency & Placement Outcome Analytics

## Overview

The **Care Transition Efficiency & Placement Outcome Analytics** project analyzes the operational flow of the Unaccompanied Alien Children (UAC) Program.

The project moves beyond simple monitoring of children in custody by analyzing how children move through different stages of the care pipeline, with particular focus on:

- CBP custody
- Transfer to HHS care
- HHS care population
- Discharge from HHS care
- Operational pressure
- Transfer and discharge activity
- Temporal patterns and outcome stability

The objective is to identify patterns, pressure points, and changes in operational activity that can support data-driven decision-making and policy evaluation.

---

## Problem Statement

The UAC program involves multiple stages of care:

1. Apprehension and placement in CBP custody
2. Transfer from CBP custody to HHS care
3. Medical screening, sheltering, and case management
4. Discharge from HHS care to vetted sponsors

While aggregate custody counts provide information about the size of the population being served, they do not by themselves explain how efficiently the overall process is operating.

This project therefore focuses on analyzing:

- How transfer activity relates to CBP custody
- How discharge activity relates to the HHS care population
- Where operational pressure appears
- How activity changes over time
- Whether aggregate outcome indicators remain stable

---

## Objectives

### Primary Objectives

- Measure CBP-to-HHS transfer activity
- Evaluate discharge activity from HHS care
- Identify operational pressure points
- Analyze changes in care activity over time
- Develop meaningful KPIs for the UAC care pipeline

### Secondary Objectives

- Identify periods of elevated operational pressure
- Compare yearly and monthly activity
- Examine reporting-day patterns
- Provide an interactive dashboard for stakeholders
- Produce analytical findings suitable for policy and operational review

---

## Dataset

The project uses data from the UAC Program containing the following variables:

| Column | Description |
|---|---|
| Date | Reporting date |
| Apprehended | Children apprehended and placed in CBP custody |
| CBP Custody | Children in CBP custody |
| Transferred | Children transferred out of CBP custody |
| HHS Care | Children in HHS care |
| Discharged | Children discharged from HHS care |

The original dataset contains reporting observations across the period analyzed in this project.

---

## Analytical Framework

The project is divided into seven analytical phases.

### Phase 1 — Data Understanding

Examines:

- Dataset structure
- Data types
- Missing values
- Blank records
- Duplicate records
- Date coverage
- Reporting frequency
- Descriptive statistics
- Distribution of variables

Notebook:

`notebooks/01_data_understanding.ipynb`

---

### Phase 2 — Data Cleaning

The raw dataset is prepared for analysis by:

- Removing completely blank rows
- Renaming columns
- Converting dates
- Converting numeric fields
- Removing formatting characters such as commas
- Checking missing values
- Checking duplicate dates
- Checking invalid negative values
- Checking logical inconsistencies
- Sorting observations chronologically

Output:

`data/processed/uac_cleaned.csv`

Notebook:

`notebooks/02_data_cleaning.ipynb`

---

### Phase 3 — Exploratory Data Analysis

Explores the major characteristics and patterns in the dataset.

Analysis includes:

- Descriptive statistics
- Pipeline population comparison
- Time-series trends
- Monthly activity
- Yearly activity
- Operational pressure
- Distributions
- Correlations
- Day-of-week patterns
- High-pressure reporting periods

Notebook:

`notebooks/03_exploratory_analysis.ipynb`

---

### Phase 4 — Care Pipeline Analysis

Examines how activity moves through the major stages of the UAC care process.

The analysis focuses on:

- Apprehension
- CBP custody
- Transfers
- HHS care
- Discharges

The objective is to understand the relationship between incoming activity, transfers, care populations, and exits.

Notebook:

`notebooks/04_care_pipeline_analysis.ipynb`

---

### Phase 5 — Efficiency & Outcome Analysis

Key indicators include:

#### Transfer Efficiency Ratio

```text
Transfer Efficiency =
Transfers / CBP Custody
Discharge Effectiveness
Discharge Effectiveness =
Discharges / HHS Care
Pipeline Throughput
Pipeline Throughput =
Total Discharges / Total Apprehensions
Outcome Stability

Stability is examined using variation in the calculated indicators across the observation period.

Notebook:

notebooks/05_efficiency_analysis.ipynb

Important: These aggregate ratios are operational indicators. They do not directly measure the actual processing time of an individual child or case.

Phase 6 — Bottleneck & Pressure Analysis

Operational pressure is evaluated using two derived measures.

CBP Net Pressure
CBP Net Pressure =
Apprehended − Transferred
HHS Net Pressure
HHS Net Pressure =
Transferred − Discharged

The analysis examines:

Daily pressure
Cumulative pressure
Pressure distributions
High-pressure periods
Pressure thresholds
Standardized pressure comparisons

These measures are treated as operational pressure indicators, rather than automatically being interpreted as literal administrative backlogs.

Notebook:

notebooks/06_backlog_bottleneck_analysis.ipynb

Phase 7 — Temporal & Outcome Analysis

Examines how activity changes across time.

Analysis includes:

Monthly transfer activity
Monthly discharge activity
Year-over-year activity
Year-over-year percentage changes
Day-of-week activity
Monthly operational pressure
Yearly outcome stability
Temporal KPI summaries

Notebook:

notebooks/07_temporal_outcome_analysis.ipynb

Key Performance Indicators

The dashboard presents the major indicators developed during the analysis.

KPI	Purpose
Transfer Efficiency Ratio	Measures transfers relative to CBP custody
Discharge Effectiveness	Measures discharges relative to HHS care
Pipeline Throughput	Compares total exits with total entries
CBP Net Pressure	Indicates pressure between apprehension and transfer activity
HHS Net Pressure	Indicates pressure between transfer and discharge activity
Outcome Stability	Measures variation in efficiency indicators over time
Dashboard

The project includes an interactive Streamlit dashboard designed to communicate analytical results to non-technical stakeholders.

Dashboard Sections
1. Executive Overview

Displays:

Total apprehensions
Total transfers
Total discharges
Transfer efficiency
Discharge effectiveness
Pipeline throughput
2. Care Pipeline

Visualizes activity across the major stages of the care process.

3. Efficiency Analysis

Displays:

Transfer efficiency trends
Discharge effectiveness trends
Efficiency distributions
High- and low-efficiency periods
4. Pressure & Bottleneck Analysis

Displays:

CBP pressure
HHS pressure
Cumulative pressure
High-pressure periods
Pressure thresholds
5. Temporal Analysis

Displays:

Monthly trends
Yearly comparisons
Year-over-year changes
Reporting-day patterns
Project Structure
Care-Transition-Analytics/
│
├── data/
│   ├── raw/
│   │   └── HHS_Unaccompanied_Alien_Children_Program.csv
│   │
│   └── processed/
│       ├── uac_cleaned.csv
│       └── uac_eda.csv
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_exploratory_analysis.ipynb
│   ├── 04_care_pipeline_analysis.ipynb
│   ├── 05_efficiency_analysis.ipynb
│   ├── 06_backlog_bottleneck_analysis.ipynb
│   └── 07_temporal_outcome_analysis.ipynb
│
├── src/
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── kpi_calculations.py
│   ├── bottleneck_analysis.py
│   └── visualization.py
│
├── dashboard/
│   ├── app.py
│   ├── components.py
│   └── styles.css
│
├── reports/
│   ├── research_paper.pdf
│   ├── executive_summary.pdf
│   └── figures/
│
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
Technology Stack
Python
Pandas — data manipulation
NumPy — numerical analysis
Matplotlib — data visualization
Seaborn — statistical visualization
Plotly — interactive visualization
Streamlit — dashboard development
Jupyter Notebook — analytical workflow
Git & GitHub — version control
Installation

Clone the repository:

git clone <your-repository-url>
cd Care-Transition-Analytics

Create a virtual environment:

python -m venv .venv

Activate the environment on Windows:

.venv\Scripts\activate

Install the dependencies:

pip install -r requirements.txt
Running the Analysis

Open Jupyter Notebook:

jupyter notebook

Run the notebooks in order:

01 → 02 → 03 → 04 → 05 → 06 → 07

The cleaned dataset generated during Phase 2 is used by the later analysis stages.

Running the Dashboard

From the project root:

streamlit run dashboard/app.py

The dashboard will open in your browser.

Outputs

The project produces three major outputs:

1. Analytical Notebooks

Detailed analysis of the UAC care pipeline.

2. Interactive Dashboard

A stakeholder-oriented Streamlit dashboard for exploring KPIs, trends, efficiency, and operational pressure.

3. Reports
Research paper
Executive summary
Analytical figures
Limitations

The dataset and analytical approach have several limitations.

Aggregate Data

The analysis is based on aggregate reporting data rather than individual case records.

No Individual Processing Time

The available variables do not directly provide the elapsed time for an individual transfer or discharge.

Therefore, the calculated efficiency ratios should not be interpreted as actual processing-time measurements.

Placement Interpretation

Discharge activity is analyzed at an aggregate level. It should not automatically be interpreted as individual reunification success unless the underlying data explicitly supports that interpretation.

Uneven Reporting Frequency

The dataset does not contain observations for every calendar day. Missing dates should therefore not automatically be interpreted as zero activity.

Stock vs Flow Measures

CBP/HHS population values represent custody or care populations, while apprehensions, transfers, and discharges represent activity measures. These should be interpreted separately.

Conclusion

The project reframes the UAC dataset from a simple population-monitoring dataset into an operational analytics framework.

By combining pipeline analysis, efficiency indicators, pressure measures, and temporal analysis, the project provides a structured view of how activity changes across the UAC care process.

The resulting dashboard and analytical reports are intended to help stakeholders identify operational patterns, periods of elevated pressure, and changes in aggregate care activity that may warrant further investigation.

Future Improvements

Potential future extensions include:

Incorporating individual-level case data
Adding actual processing-time measurements
Adding facility-level analysis
Including geographic analysis
Adding demographic outcome analysis where appropriate
Connecting the dashboard to regularly updated data
Adding automated reporting
Developing predictive models if sufficiently detailed longitudinal data becomes available
Author

Mahi Ahalawat

Robotics & AI Engineering Student

License

This project is intended for educational, analytical, and research purposes.


### One thing I'd change before you put this on GitHub

For the **final GitHub version**, don't leave:

```text
<your-repository-url>