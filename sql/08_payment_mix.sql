-- First payment method on an order; multi-method payments are simplified to primary method.
SELECT COALESCE(payment_method,'Unknown') AS primary_payment_method,
       COUNT(*) AS delivered_orders, ROUND(SUM(gmv_brl),2) AS merchandise_gmv_brl,
       ROUND(AVG(payment_installments),2) AS mean_installments
FROM fact_orders WHERE is_delivered=1 GROUP BY payment_method ORDER BY delivered_orders DESC;
