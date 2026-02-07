"""
Dashboard BI - FastAPI Backend
Examen BI - Parte B
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from typing import List, Dict
import json

load_dotenv()

app = FastAPI(title="Dashboard BI - Examen")

# CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Conexión a PostgreSQL"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.get("/")
async def root():
    """Redirigir a dashboard"""
    return FileResponse("static/index.html")

@app.get("/api/kpis")
async def get_kpis():
    """KPIs principales para Executive Dashboard"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Net Sales MTD y YTD
    cur.execute("""
        WITH monthly_sales AS (
            SELECT 
                TO_CHAR(o.order_date, 'YYYY-MM') AS month_period,
                SUM(oi.qty * oi.unit_price) - SUM(o.discount_amount) AS net_sales
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.status = 'paid'
            GROUP BY TO_CHAR(o.order_date, 'YYYY-MM')
        )
        SELECT 
            (SELECT net_sales FROM monthly_sales ORDER BY month_period DESC LIMIT 1) as net_sales_mtd,
            (SELECT SUM(net_sales) FROM monthly_sales) as net_sales_ytd
    """)
    sales = cur.fetchone()
    
    # Gross Margin
    cur.execute("""
        SELECT 
            SUM(oi.qty * oi.unit_price) AS revenue,
            SUM(oi.qty * oi.unit_cost) AS cogs
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'paid'
    """)
    margin = cur.fetchone()
    gross_margin = float(margin['revenue']) - float(margin['cogs'])
    gross_margin_pct = (gross_margin / float(margin['revenue'])) * 100 if margin['revenue'] else 0
    
    # Órdenes y AOV
    cur.execute("""
        SELECT 
            COUNT(DISTINCT order_id) as total_orders,
            SUM(total_amount) / COUNT(DISTINCT order_id) as aov
        FROM orders
        WHERE status = 'paid'
    """)
    orders_data = cur.fetchone()
    
    # Returns
    cur.execute("""
        SELECT 
            SUM(r.amount_returned) as total_returns,
            (SELECT SUM(oi.qty * oi.unit_price) 
             FROM orders o 
             JOIN order_items oi ON o.order_id = oi.order_id 
             WHERE o.status = 'paid') as gross_sales
        FROM returns r
    """)
    returns_data = cur.fetchone()
    return_rate = (float(returns_data['total_returns']) / float(returns_data['gross_sales'])) * 100 if returns_data['gross_sales'] else 0
    
    cur.close()
    conn.close()
    
    return {
        "net_sales_mtd": float(sales['net_sales_mtd']),
        "net_sales_ytd": float(sales['net_sales_ytd']),
        "gross_margin": gross_margin,
        "gross_margin_pct": round(gross_margin_pct, 2),
        "total_orders": orders_data['total_orders'],
        "aov": float(orders_data['aov']),
        "return_rate": round(return_rate, 2),
        "total_returns": float(returns_data['total_returns'])
    }

@app.get("/api/monthly-trend")
async def get_monthly_trend():
    """Tendencia mensual de ventas"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            TO_CHAR(o.order_date, 'YYYY-MM') AS month,
            SUM(oi.qty * oi.unit_price) AS gross_sales,
            SUM(o.discount_amount) AS discounts,
            COALESCE(SUM(r.amount_returned), 0) AS returns
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        LEFT JOIN returns r ON o.order_id = r.order_id
        WHERE o.status = 'paid'
        GROUP BY TO_CHAR(o.order_date, 'YYYY-MM')
        ORDER BY month
    """)
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return [
        {
            "month": row['month'],
            "gross_sales": float(row['gross_sales']),
            "discounts": float(row['discounts']),
            "returns": float(row['returns']),
            "net_sales": float(row['gross_sales']) - float(row['discounts']) - float(row['returns'])
        }
        for row in results
    ]

@app.get("/api/sales-by-city")
async def get_sales_by_city():
    """Ventas por ciudad"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            s.city,
            SUM(oi.qty * oi.unit_price) - SUM(o.discount_amount) AS net_sales
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN stores s ON o.store_id = s.store_id
        WHERE o.status = 'paid'
        GROUP BY s.city
        ORDER BY net_sales DESC
    """)
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{"city": row['city'], "net_sales": float(row['net_sales'])} for row in results]

@app.get("/api/top-products")
async def get_top_products():
    """Top 10 productos por margen"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            p.category || ' - ' || p.brand AS product_name,
            SUM(oi.qty * oi.unit_price) AS revenue,
            SUM(oi.qty * oi.unit_cost) AS cogs,
            SUM(oi.qty * oi.unit_price) - SUM(oi.qty * oi.unit_cost) AS gross_margin
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status = 'paid'
        GROUP BY p.category, p.brand
        ORDER BY gross_margin DESC
        LIMIT 10
    """)
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return [
        {
            "product_name": row['product_name'],
            "revenue": float(row['revenue']),
            "cogs": float(row['cogs']),
            "gross_margin": float(row['gross_margin']),
            "gross_margin_pct": round((float(row['gross_margin']) / float(row['revenue'])) * 100, 2)
        }
        for row in results
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
