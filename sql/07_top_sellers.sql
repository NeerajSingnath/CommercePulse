SELECT seller_id, ROUND(SUM(gmv_brl),2) AS gmv_brl,
       COUNT(DISTINCT CASE WHEN is_delivered=1 THEN order_id END) AS delivered_orders,
       ROUND(SUM(CASE WHEN is_delivered=1 THEN item_freight_brl ELSE 0 END),2) AS freight_brl
FROM fact_items GROUP BY seller_id ORDER BY gmv_brl DESC LIMIT 20;
