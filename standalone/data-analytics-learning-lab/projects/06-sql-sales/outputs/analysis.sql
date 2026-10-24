WITH monthly AS (
SELECT strftime('%Y-%m',o.date) AS month,p.category,SUM(o.quantity*p.price) AS revenue
FROM orders o JOIN products p ON o.product_id=p.product_id GROUP BY 1,2)
SELECT *,revenue-LAG(revenue) OVER (PARTITION BY category ORDER BY month) AS revenue_change FROM monthly ORDER BY month,category;
