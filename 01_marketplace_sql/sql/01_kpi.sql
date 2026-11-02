-- 01. Общий результат по доставленным заказам
SELECT
    COUNT(*) AS delivered_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(quantity * price_rub), 2) AS revenue_rub,
    ROUND(SUM(quantity * purchase_cost_rub + commission_rub + logistics_rub + acquiring_rub + tax_rub + ads_rub), 2) AS variable_cost_rub,
    ROUND(SUM(quantity * (price_rub - purchase_cost_rub) - commission_rub - logistics_rub - acquiring_rub - tax_rub - ads_rub), 2) AS contribution_profit_rub,
    ROUND(100.0 * SUM(quantity * (price_rub - purchase_cost_rub) - commission_rub - logistics_rub - acquiring_rub - tax_rub - ads_rub) / NULLIF(SUM(quantity * price_rub), 0), 2) AS contribution_margin_pct,
    ROUND(AVG(quantity * price_rub), 2) AS avg_order_value_rub
FROM orders
WHERE order_status = 'delivered';

