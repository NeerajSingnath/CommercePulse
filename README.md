# ◈ CommercePulse — E-Commerce Analytics & Delivery Risk Intelligence

**A reproducible Data Analyst portfolio project** combining SQL, Python ETL, data quality checks, customer RFM segmentation, temporal machine learning, a multi-page Streamlit dashboard, an interactive Plotly HTML report, and a ready-to-import Power BI dataset with measures/design system.

> **Important:** The downloadable package ships with **clearly labeled synthetic demo data** so it can run immediately without Kaggle access. The bundled KPI results are not findings from the real Olist dataset. Replace the demo data before using numbers in a real-world case study.

## Fast start on Windows (Python 3.10+)

```powershell
cd CommercePulse
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/quickstart.py --demo
streamlit run app/dashboard.py
```

Open `reports/interactive_dashboard.html` directly in any browser **without installing Streamlit**. The Power BI import tables are in `data/powerbi`.

## Switch to REAL Olist dataset

```powershell
pip install kagglehub
python scripts/download_olist.py
python scripts/quickstart.py
streamlit run app/dashboard.py
```

Or download manually from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce and extract the seven named CSVs directly to `data/raw/`, removing `SYNTHETIC_DEMO_DATA.txt` **only once all files have been replaced**. The script regenerates the warehouse, SQL outputs, model and report using the real inputs. Internet access is required for Kaggle downloads.

## Dashboard and analytic deliverables

| Area | What is included |
|---|---|
| **Streamlit dashboard** | Executive overview, Revenue & Products, Customer Intelligence, Logistics & Reviews, Historical Risk Model, filters and downloads |
| **SQL** | SQLite database and 8 reproducible SQL scripts: GMV, products, RFM, delivery SLA, reviews, retention cohorts, sellers and payment mix |
| **Power BI** | Import-ready 5-table model in `data/powerbi/`, DAX measures, four dashboard page specifications, dark theme, layout preview |
| **Machine learning** | Logistic regression baseline; only checkout-time input features; time-based 80/20 holdout; AUC, AP, precision/recall |
| **Reports** | Offline interactive HTML, machine-readable KPI report, SQL result CSVs, executive narrative |
| **Engineering** | Synthetic fixture generator, ETL validation, automated tests, Dockerfile, architecture and data dictionary |

## Project map

```text
CommercePulse/
├── app/dashboard.py                  # Multi-page Streamlit dashboard
├── src/pipeline.py                   # Input validation and star-schema ETL
├── src/database.py                   # SQL warehouse and queries
├── src/modeling.py                   # Chronological predictive evaluation
├── src/reports.py                    # Standalone HTML + executive summary
├── scripts/quickstart.py             # One-command pipeline
├── scripts/generate_demo.py          # Clearly labeled synthetic data
├── scripts/download_olist.py         # Fetch original public dataset
├── sql/                              # Eight analytical queries
├── data/raw/                         # Source CSVs, demo by default
├── data/processed/                   # Order/item facts and dimensions
├── data/powerbi/                     # Power BI import-ready CSVs
├── powerbi/                           # DAX, build guide, theme, preview
├── models/                            # Trained model + metrics + predictions
├── reports/                           # Offline HTML, SQL and narrative outputs
├── tests/                             # Join/GMV tests
└── docs/                              # Architecture, metrics, Q&A
```

## Data quality assurance

- Deduplicates key dimension records and prevents many-to-many fact inflation using pre-aggregated payment and review tables.
- Validates one row per order, orphan item counts and order-vs-item GMV reconciliation.
- Evaluates delivery-risk **only on delivered orders**, holds out the latest 20% chronologically, and excludes post-delivery leakage fields.
- Displays synthetic vs actual Olist data type visibly inside dashboard and report.

## Common commands

```bash
python scripts/quickstart.py --demo   # Regenerate deterministic demo + everything else
pytest -q                             # Automated correctness checks
streamlit run app/dashboard.py        # Dashboard, http://localhost:8501
python scripts/quickstart.py          # Rebuild from downloaded ORIGINAL CSVs
```

## Honest limitations

No ready-made native `.pbix` is shipped; Power BI Desktop must be used to author and save the interactive dashboard, following `powerbi/PowerBI_Build_Guide.md`. The static preview is a layout concept. Neither a live production model, profit calculation, nor proven causal conclusions are claimed. Dataset covers 2016–2018 history, not current Brazilian market activity.

## Attribution

Olist Brazilian E-Commerce Public Dataset, https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce. Public examples should credit the original publisher and respect the dataset license/terms. Demo data was independently synthesized and should not be described as original Olist records.
