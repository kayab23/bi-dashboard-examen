-- ============================================================================
-- Schema PostgreSQL para Dashboard BI
-- ============================================================================

-- Tabla customers
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    country VARCHAR(50) NOT NULL,
    channel VARCHAR(50) NOT NULL
);

-- Tabla stores
CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL
);

-- Tabla products
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL
);

-- Tabla orders
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    store_id INTEGER REFERENCES stores(store_id),
    order_date TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    shipping_amount DECIMAL(12,2) DEFAULT 0
);

-- Tabla order_items
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    qty INTEGER NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    unit_cost DECIMAL(12,2) NOT NULL
);

-- Tabla returns
CREATE TABLE returns (
    return_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    return_date TIMESTAMP NOT NULL,
    amount_returned DECIMAL(12,2) NOT NULL
);

-- Índices para performance
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_returns_order ON returns(order_id);
