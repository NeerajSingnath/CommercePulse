# 4–5 hour submission sprint

**Goal:** Submit a real-data analytics case study with functioning Python and Power BI dashboards. The repository is already authored; the biggest remaining manual task is creating and saving the native Power BI report in Desktop.

| Time | Action | Proof of completion |
|---|---|---|
| 0:00–0:20 | Extract ZIP; set up Python 3.11/3.12 environment, run sample pipeline and local dashboard | HTML and Streamlit tabs open; tests pass |
| 0:20–0:45 | Download genuine public Olist data with `pip install kagglehub` + `python scripts/download_olist.py`; run `python scripts/quickstart.py` | No `SYNTHETIC DEMO` banner; real-data model and report created |
| 0:45–2:00 | Import six prepared CSVs to Power BI Desktop; create five model relationships; copy DAX; build Executive Overview | Power BI overview page has 5 cards and 3+ charts |
| 2:00–3:00 | Add Customer and Delivery pages; set theme, interactions, state/date slicers; save `.pbix` | Three cross-filtering pages, correct GMV vs Python |
| 3:00–3:35 | Add ML retrospective test page; validate counts/labels; take clean screenshots | Page 4 + model caveats correct |
| 3:35–4:05 | Test SQL scripts, capture evidence and clean README/screenshots | End-to-end run and evidence |
| 4:05–4:40 | Final review and upload ZIP/GitHub plus `.pbix` separately (unless uploading together) | Working file links, no fake real-world claims |

## Non-negotiable integrity checks

- Never claim bundled demo metrics came from original Olist.
- When the real dataset is loaded, rerun all stages before taking screenshots.
- A `.png` layout concept is not a native Power BI dashboard; finish the `.pbix` in Power BI Desktop.
- Do not claim net sales, profit, churn labels, or a production-ready ML model from these fields.
- State 2016–2018 historical dataset window; do not imply current market performance.

## Submission bundle

1. `CommercePulse_Business_Intelligence.pbix` — created in Power BI Desktop
2. `CommercePulse` GitHub repo — code, data-source README, environment, tests
3. `reports/executive_summary.md` — regenerated from original data
4. `reports/interactive_dashboard.html` — offline interactive report
5. Optional 1–2 minute screen capture showing filters, SQL joins, and model evaluation
