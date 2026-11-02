-- 02. Месячная динамика: CTE + LAG; YYYY-MM вычисляется портируемой SUBSTR
WITH monthly AS (
  SELECT SUBSTR(order_date, 1, 7) AS month,
         COUNT(*) AS orders,
         ROUND(SUM(quantity * price_rub), 2) AS revenue_rub,
         ROUND(SUM(quantity * (price_rub - purchase_cost_rub) - commission_rub - logistics_rub - acquiring_rub - tax_rub - ads_rub), 2) AS profit_rub
  FROM orders
  WHERE order_status = 'delivered'
  GROUP BY SUBSTR(order_date, 1, 7)
), compared AS (
  SELECT *, LAG(revenue_rub) OVER (ORDER BY month) AS prev_revenue_rub
  FROM monthly
)
SELECT month, orders, revenue_rub, profit_rub, prev_revenue_rub,
       ROUND(100.0 * (revenue_rub - prev_revenue_rub) / NULLIF(prev_revenue_rub, 0), 2) AS revenue_mom_pct
FROM compared
ORDER BY month;
