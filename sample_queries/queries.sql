SELECT
    o.order_id,
    o.customer_id,
    IFF(o.status = 'CANCELLED', 0, o.total_amount) AS billable_amount,
    DATEADD('day', -30, o.order_date) AS lookback_date
FROM orders o
WHERE o.order_date >= DATEADD('month', -1, CURRENT_DATE());

SELECT
    c.customer_id,
    c.name,
    LISTAGG(o.order_id, ',') AS order_ids
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name;
