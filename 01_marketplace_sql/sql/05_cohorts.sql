-- 05. Когортная таблица по месяцам первого доставленного заказа.
-- retention = активных покупателей когорты в месяце / её размер в первый месяц.
WITH activity AS (
    SELECT DISTINCT customer_id, SUBSTR(order_date, 1, 7) AS activity_month
    FROM orders
    WHERE order_status = 'delivered'
), first_month AS (
    SELECT customer_id, MIN(activity_month) AS cohort_month
    FROM activity GROUP BY customer_id
), cohort_activity AS (
    SELECT f.cohort_month, a.activity_month,
           ((CAST(SUBSTR(a.activity_month, 1, 4) AS INTEGER) - CAST(SUBSTR(f.cohort_month, 1, 4) AS INTEGER)) * 12
             + CAST(SUBSTR(a.activity_month, 6, 2) AS INTEGER) - CAST(SUBSTR(f.cohort_month, 6, 2) AS INTEGER)) AS month_number,
           COUNT(DISTINCT a.customer_id) AS active_buyers
    FROM activity a JOIN first_month f ON a.customer_id = f.customer_id
    GROUP BY f.cohort_month, a.activity_month
), sizes AS (
    SELECT cohort_month, active_buyers AS cohort_size FROM cohort_activity WHERE month_number = 0
)
SELECT c.cohort_month, c.month_number, s.cohort_size, c.active_buyers,
       ROUND(100.0 * c.active_buyers / NULLIF(s.cohort_size, 0), 2) AS retention_pct
FROM cohort_activity c JOIN sizes s ON c.cohort_month = s.cohort_month
ORDER BY c.cohort_month, c.month_number;
