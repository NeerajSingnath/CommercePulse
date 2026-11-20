-- Grain: one line item. Never join payments to items without aggregating payments first.
SELECT category, ROUND(SUM(gmv_brl),2) AS merchandise_gmv_brl,
       COUNT(DISTINCT CASE WHEN is_delivered=1 THEN order_id END) AS delivered_orders,
       ROUND(SUM(CASE WHEN is_delivered=1 THEN item_freight_brl ELSE 0 END),2) AS freight_brl
FROM fact_items GROUP BY category ORDER BY merchandise_gmv_brl DESC LIMIT 20;
