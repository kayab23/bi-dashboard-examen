-- ============================================================================
-- Script para cargar datos CSV a PostgreSQL en Render
-- Ejecutar después de crear el schema con schema_postgres.sql
-- ============================================================================

-- IMPORTANTE: Este script asume que ya ejecutaste schema_postgres.sql

-- Desactivar triggers y constraints temporalmente para carga rápida
SET session_replication_role = 'replica';

-- 1. Cargar customers
\COPY customers(customer_id, created_at, country, channel) FROM 'customers.csv' WITH CSV HEADER DELIMITER ',';

-- 2. Cargar stores
\COPY stores(store_id, store_name, city) FROM 'stores.csv' WITH CSV HEADER DELIMITER ',';

-- 3. Cargar products
\COPY products(product_id, category, brand) FROM 'products.csv' WITH CSV HEADER DELIMITER ',';

-- 4. Cargar orders
\COPY orders(order_id, customer_id, store_id, order_date, status, total_amount, discount_amount, shipping_amount) FROM 'orders.csv' WITH CSV HEADER DELIMITER ',';

-- 5. Cargar order_items
\COPY order_items(order_item_id, order_id, product_id, qty, unit_price, unit_cost) FROM 'order_items.csv' WITH CSV HEADER DELIMITER ',';

-- 6. Cargar returns
\COPY returns(return_id, order_id, return_date, amount_returned, reason) FROM 'returns.csv' WITH CSV HEADER DELIMITER ',';

-- Reactivar triggers y constraints
SET session_replication_role = 'origin';

-- Actualizar secuencias para que los IDs continúen correctamente
SELECT setval('customers_customer_id_seq', (SELECT MAX(customer_id) FROM customers));
SELECT setval('stores_store_id_seq', (SELECT MAX(store_id) FROM stores));
SELECT setval('products_product_id_seq', (SELECT MAX(product_id) FROM products));
SELECT setval('orders_order_id_seq', (SELECT MAX(order_id) FROM orders));
SELECT setval('order_items_order_item_id_seq', (SELECT MAX(order_item_id) FROM order_items));
SELECT setval('returns_return_id_seq', (SELECT MAX(return_id) FROM returns));

-- Verificar carga
SELECT 'customers' AS tabla, COUNT(*) AS registros FROM customers
UNION ALL
SELECT 'stores', COUNT(*) FROM stores
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'returns', COUNT(*) FROM returns;

-- Verificar totales
SELECT 
    SUM(oi.qty * oi.unit_price) as gross_sales,
    SUM(o.discount_amount) as total_discounts,
    COUNT(DISTINCT o.order_id) as total_orders
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'paid';
