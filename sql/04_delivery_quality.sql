SELECT state, COUNT(*) AS delivered_orders,
       ROUND(100.0*SUM(is_late)/NULLIF(COUNT(*),0),2) AS late_delivery_pct,
       ROUND(AVG(delivery_days),1) AS avg_delivery_days,
       ROUND(AVG(review_score),2) AS avg_review_score
FROM fact_orders WHERE is_delivered=1
GROUP BY state HAVING COUNT(*)>=20 ORDER BY late_delivery_pct DESC;
