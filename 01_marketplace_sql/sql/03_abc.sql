-- 03. Классификация товаров по доле в накопленной выручке
WITH product_sales AS (
  SELECT product_id, category,
         ROUND(SUM(quantity * price_rub), 2) AS revenue_rub
  FROM orders
  WHERE order_status = 'delivered'
  GROUP BY product_id, category
), shares AS (
  SELECT *, SUM(revenue_rub) OVER (ORDER BY revenue_rub DESC, product_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue,
            SUM(revenue_rub) OVER () AS total_revenue
  FROM product_sales
)
SELECT product_id, category, revenue_rub,
       ROUND(100.0 * revenue_rub / NULLIF(total_revenue, 0), 2) AS revenue_share_pct,
       ROUND(100.0 * cumulative_revenue / NULLIF(total_revenue, 0), 2) AS cumulative_share_pct,
       CASE WHEN (cumulative_revenue - revenue_rub) / NULLIF(total_revenue, 0) < 0.80 THEN 'A'
            WHEN (cumulative_revenue - revenue_rub) / NULLIF(total_revenue, 0) < 0.95 THEN 'B'
            ELSE 'C' END AS abc_group
FROM shares
ORDER BY revenue_rub DESC, product_id;
