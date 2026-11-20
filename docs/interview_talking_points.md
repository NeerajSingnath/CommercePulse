# 90-second interview pitch + defense

## Pitch

"I developed **CommercePulse**, an end-to-end e-commerce business analytics project using the publicly released Olist order dataset. It ingests seven relational CSVs, models them as order and line-item facts with customer/product/date dimensions, validates joins to prevent duplicate sales, stores the model in SQLite, and answers revenue, customer-segmentation and logistics questions through SQL, a multi-page Python dashboard, and a Power BI-ready semantic model. I also built a late-delivery risk baseline evaluated on a chronological holdout. I distinguish merchandise GMV from net revenue, treat customer inactivity as a heuristic rather than churn, and explicitly avoid post-delivery target leakage."

**Only use the phrase "publicly released Olist" after replacing synthetic demo data with the real download.** For the bundled demo, say "Olist-shaped synthetic test data".

## Common interview questions

**Why SQL and Python?** SQL provides auditable analytical calculations and a reproducible relational warehouse; Python handles validations, feature engineering and model evaluation.

**How do you avoid double-counting?** Group review and payment tables to one row per order before joining `fact_orders`. Keep product line-item fact separate and reconcile its delivered GMV against the order-level total.

**Why a star schema?** Fact granularity is explicit and slicer behavior is predictable. The transaction-to-line-item relationship is one-to-many; customer and product dimensions supply descriptors.

**Why delivered GMV rather than revenue?** The dataset cannot reconcile returns, taxes or recognized revenue. Calling this merchandise GMV is analytically honest.

**Is the model accurate enough?** Use measured ROC-AUC and average precision from `models/metrics.json`. Compare with test-set late prevalence. It is a retrospective baseline, not production-grade, and accuracy should not be exaggerated.

**What is leakage?** Including actual delivery duration or eventual review in checkout-time risk features would reveal future outcomes and inflate evaluation.

**Can you infer why a customer churned?** No. RFM flags inactivity and recency; missing full marketing/customer-journey data prevents causal explanations.

**What could the company do next?** Monitor carrier SLA by state/seller, identify high-risk orders for proactive communication, A/B-test retention incentives and investigate categories with high shipping costs.
