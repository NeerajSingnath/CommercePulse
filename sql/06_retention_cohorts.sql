-- Customers who return in a later MONTH (not just additional orders in same month).
WITH first_purchase AS (
 SELECT customer_unique_id, MIN(order_month) AS cohort_month
 FROM fact_orders WHERE is_delivered=1 GROUP BY customer_unique_id
), customer_activity AS (
 SELECT DISTINCT o.customer_unique_id, f.cohort_month, o.order_month
 FROM fact_orders o JOIN first_purchase f ON o.customer_unique_id=f.customer_unique_id
 WHERE o.is_delivered=1
), cohort_sizes AS (
 SELECT cohort_month, COUNT(*) AS cohort_size FROM first_purchase GROUP BY cohort_month
)
SELECT a.cohort_month, a.order_month, COUNT(*) AS active_customers, c.cohort_size,
       ROUND(100.0*COUNT(*)/c.cohort_size,2) AS active_share_pct
FROM customer_activity a JOIN cohort_sizes c ON a.cohort_month=c.cohort_month
GROUP BY a.cohort_month,a.order_month,c.cohort_size ORDER BY a.cohort_month,a.order_month;
