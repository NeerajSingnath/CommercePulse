# CommercePulse — Executive Summary

**Data:** OLIST ORIGINAL. These numbers are from this project's current processed data. **Historical order coverage only**; no causal claims.

## Key business indicators

- Delivered merchandise GMV (excluding freight): **R$ 13,220,248.93**
- Delivered orders: **96,470**; AOV: **R$ 137.04**
- Observed late delivery rate: **8.11%** of delivered orders
- Average customer review: **4.16/5**
- Repeat buyer share (2+ delivered orders; full dataset): **2.91%**
- Highest-GMV category: **Health Beauty**; leading state: **SP**

## Hypotheses to validate

1. Target higher-delay states with seller SLA monitoring and carrier diagnostics. Late orders have an observed review average of 2.57, versus 4.29 for on-time deliveries. This is association, **not proof** that lateness causes lower reviews.
2. Improve repeat purchases with targeted campaigns for customers with a single purchase, then test incremental lift against a holdout group.
3. Track category GMV and freight costs separately; do not confuse payment totals with merchandise GMV, and do not call GMV net revenue or profit.

## Data and modeling caveats

- This dataset has no purchase cost, return/refund truth, marketing spend, or reliable profits.
- Customer inactivity is not proof of churn; RFM is descriptive.
- Delivery risk ML is retrospective, uses checkout-time features, and is evaluated on a later chronological holdout.
- If demo data were used, **replace with original Olist data before describing results as real-world findings**.
