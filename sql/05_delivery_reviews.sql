SELECT CASE WHEN is_late=1 THEN 'Late' ELSE 'On time' END AS delivery_type,
       COUNT(*) AS orders, ROUND(AVG(review_score),2) AS mean_review_score,
       ROUND(100.0*SUM(CASE WHEN review_score<=2 THEN 1 ELSE 0 END)/NULLIF(COUNT(review_score),0),2) AS low_review_pct
FROM fact_orders WHERE is_delivered=1 GROUP BY is_late ORDER BY is_late;
