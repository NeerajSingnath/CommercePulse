SELECT segment, COUNT(*) AS customers,
       ROUND(AVG(lifetime_gmv_brl),2) AS avg_customer_ltv_proxy_brl,
       ROUND(SUM(lifetime_gmv_brl),2) AS total_historical_gmv_brl
FROM dim_customers GROUP BY segment ORDER BY total_historical_gmv_brl DESC;
