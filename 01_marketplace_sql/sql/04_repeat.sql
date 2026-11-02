-- 04. Повторные покупатели: минимум два доставленных заказа
WITH orders_by_customer AS (
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY customer_id
)
SELECT COUNT(*) AS buyers,
       SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) AS repeat_buyers,
       ROUND(100.0 * SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS repeat_buyer_share_pct
FROM orders_by_customer;
