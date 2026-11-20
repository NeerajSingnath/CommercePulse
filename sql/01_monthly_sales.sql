-- Grain: one delivered order. GMV excludes freight and cancellations.
SELECT order_month, COUNT(DISTINCT order_id) AS delivered_orders,
       ROUND(SUM(gmv_brl),2) AS merchandise_gmv_brl,
       ROUND(SUM(gmv_brl)/NULLIF(COUNT(DISTINCT order_id),0),2) AS aov_brl
FROM fact_orders WHERE is_delivered=1
GROUP BY order_month ORDER BY order_month;
