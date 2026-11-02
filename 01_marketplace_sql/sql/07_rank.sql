-- 07. Три лучших SKU в каждой категории по выручке
WITH sales AS (
  SELECT category, product_id, SUM(quantity * price_rub) AS revenue_rub
  FROM orders WHERE order_status = 'delivered'
  GROUP BY category, product_id
), ranks AS (
  SELECT category, product_id, ROUND(revenue_rub, 2) AS revenue_rub,
         DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue_rub DESC) AS category_rank
  FROM sales
)
SELECT * FROM ranks WHERE category_rank <= 3
ORDER BY category, category_rank, product_id;
