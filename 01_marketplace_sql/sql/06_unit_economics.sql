-- 06. Экономика по категориям: закупка и переменные расходы уже вычтены
SELECT category,
       COUNT(*) AS orders,
       ROUND(SUM(quantity * price_rub), 2) AS revenue_rub,
       ROUND(SUM(quantity * purchase_cost_rub), 2) AS purchase_cost_rub,
       ROUND(SUM(commission_rub + logistics_rub + acquiring_rub + tax_rub + ads_rub), 2) AS fees_other_rub,
       ROUND(SUM(quantity * (price_rub - purchase_cost_rub) - commission_rub - logistics_rub - acquiring_rub - tax_rub - ads_rub), 2) AS contribution_profit_rub,
       ROUND(100.0 * SUM(quantity * (price_rub - purchase_cost_rub) - commission_rub - logistics_rub - acquiring_rub - tax_rub - ads_rub) / NULLIF(SUM(quantity * price_rub), 0), 2) AS margin_pct
FROM orders
WHERE order_status = 'delivered'
GROUP BY category
ORDER BY contribution_profit_rub DESC;
