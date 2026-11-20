# CommercePulse — Power BI Dashboard Build Kit

**Status:** Ready-to-import CSV data model, tested numeric definitions, DAX measures, and page-by-page design. **A native `.pbix` or `.pbip` has not been generated**; those need to be authored/verified inside Microsoft Power BI Desktop. The PNG is a *design concept*, not a Power BI screenshot.

## 1. Load the data (10 minutes)

1. Run `python scripts/quickstart.py --demo` once to generate a local demo and all the Power BI inputs. To use the genuine Olist data, run `pip install kagglehub`, then `python scripts/download_olist.py` and `python scripts/quickstart.py`.
2. Launch Power BI Desktop -> **Get data -> Text/CSV**, import each CSV in `data/powerbi/`: `fact_orders.csv`, `fact_items.csv`, `dim_customers.csv`, `dim_products.csv`, `dim_date.csv`. Optionally import `out_of_time_predictions.csv`.
3. Set these types in **Transform data**: `order_date` and `dim_date[date]` to **Date**; `purchased_at`, `delivered_at`, `estimated_delivery_at` to **Date/Time**; `gmv_brl`, `order_value_brl`, `price`, `freight_brl`, `review_score`, `delay_days` to decimals; `is_late`, `is_delivered` to whole numbers. Format money as **Brazilian Real (R$)**.
4. **Close & Apply**, then go to Model View and create the relationships below. All **single-direction**.

## 2. Data model (star schema, one-to-many)

| Dimension / parent | Parent key | Fact / child | Foreign key | Cardinality |
|---|---|---|---|---|
| `dim_date` | `date` | `fact_orders` | `order_date` | 1:* |
| `dim_customers` | `customer_unique_id` | `fact_orders` | `customer_unique_id` | 1:* |
| `fact_orders` | `order_id` | `fact_items` | `order_id` | 1:* |
| `dim_products` | `product_id` | `fact_items` | `product_id` | 1:* |
| `fact_orders` | `order_id` | `out_of_time_predictions` (optional) | `order_id` | 1:0..1 |

Important: **Never** join raw reviews and raw payments directly with raw item lines; those tables have multiple rows per order and would inflate GMV. The Python ETL aggregates them *before* joining to `fact_orders`. Use product metrics from `fact_items` and order-level KPIs from `fact_orders`.

Set `dim_date` as the **date table** using `dim_date[date]`. Sort `dim_date[month_name]` by `dim_date[month]`. Month charts should use `dim_date[year_month]` (ISO `YYYY-MM`).

## 3. DAX (5–10 minutes)

Open `MEASURES.dax`, use **Modeling -> New measure**, paste measures one by one. Suggested number formats:
- GMV / AOV: Currency (BRL), 0 or 2 decimals
- On-time / Late / Repeat: Percentage, 1 decimal
- Average review: Decimal, 2 decimals
- Orders / Customers: Whole number

The repeat share is an **all-time customer lifetime statistic**. The public Olist data is historical, not real-time. Neither spend nor margin data is available to calculate profit or marketing ROAS.

## 4. Page build specification (35–50 minutes)

### Page 1 — Executive Overview

- Title: **CommercePulse | Executive Overview**
- Top row: 5 cards: Merchandise GMV, Delivered Orders, AOV, On-Time %, Average Review
- Left middle: line chart `dim_date[year_month]` x `[Merchandise GMV]`
- Right middle: clustered bar `dim_products[category]` x `[Category GMV]` (Top 10)
- Bottom left: map/filled map `fact_orders[state]` with `[Merchandise GMV]` (or column chart if shape maps unavailable)
- Bottom right: payment mix by `fact_orders[payment_method]` and `[Delivered Orders]`
- Slicers: year-month, state, status. Keep data-origin banner visible.

### Page 2 — Customer Intelligence

- Cards: Unique Customers, Repeat Customer Share (All Time), Average Customer Lifetime GMV (All Time)
- Clustered bar: `dim_customers[segment]` vs count of `customer_unique_id`
- Scatter: `dim_customers[recency_days]` vs `dim_customers[lifetime_gmv_brl]`, size `lifetime_delivered_orders` (limit to relevant rows)
- Table: unique customer ID, segment, RFM, lifetime delivered orders, historical GMV.
- Add subtitle: "RFM segments use full-history customer behavior; they do not change with date slicers."

### Page 3 — Delivery and Satisfaction

- Cards: Late Delivery %, Average Delivery Days, Average Days Late, Average Review Score
- Bar: `fact_orders[state]` by `[Late Delivery %]`, filter small states if necessary
- Column chart: month vs `[Late Delivery %]`
- Bar chart: late vs on-time review averages (two card measures or calculated category column)
- Table: state, orders, late rate, average review
- Add caveat: "Late deliveries are correlated with lower review scores; this analysis does not establish causality."

### Page 4 — Predictive Risk (Retrospective)

- Import `out_of_time_predictions.csv` when present.
- Cards: model ROC-AUC and average precision entered from `models/metrics.json` as static annotations, NOT calculated from full order table.
- Bar: `risk_tier` vs COUNT(`order_id`), filtered to held-out predictions
- Table: `order_id`, `purchased_at`, `state`, `late_probability`, `is_late`
- Label this page **Historical out-of-time test only**, not "live prediction".

## 5. Design system

Use `commercepulse_theme.json` via **View -> Themes -> Browse for themes**.

- Deep navy page background `#0B1120`
- Cards `#14213B`
- Teal primary `#13B5A6`
- Blue `#4F8CFF`, violet `#7C5CFF`, orange `#F59E0B`, coral for risk `#FB7185`
- 16:9 page, compact legends, rounded cards, meaningful tooltips

## 6. Final checklist

- Confirm `[Merchandise GMV]` equals `reports/metrics.json:gross_merchandise_value_brl` **with all filters cleared**.
- Confirm `COUNTROWS(fact_orders)` equals `data/processed/quality_checks.json:unique_order_ids`.
- Verify `fact_orders[order_id]` and `dim_customers[customer_unique_id]` have unique keys; both are prechecked in ETL.
- Use the **same** period/state slicers on pages 1 and 3; clearly label Page 2 lifetime metrics.
- Save in Power BI Desktop using **File -> Save as -> `.pbix`**, name `CommercePulse_Business_Intelligence.pbix`.
- Screenshots must be from your actual Power BI Desktop file; `dashboard_layout_concept.png` is not a screenshot of Power BI.

## Official sources

- Original data: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Power BI project formats: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
