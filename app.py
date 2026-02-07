"""
Dashboard BI - FastAPI Backend
Soporta SQL Server (local) y PostgreSQL (Render)
Implementa TODOS los requerimientos del examen BI
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Detectar tipo de base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
DB_TYPE = os.getenv("DB_TYPE", "sqlserver" if not DATABASE_URL else "postgresql")

# Importar driver correspondiente (lazy import para evitar errores)
if DB_TYPE == "postgresql" or DATABASE_URL:
    try:
        # Intentar psycopg v3 primero (compatible con Python 3.13)
        import psycopg
        PSYCOPG_VERSION = 3
        DB_TYPE = "postgresql"
        print(f"✅ psycopg v3 importado. DB_TYPE={DB_TYPE}")
    except ImportError:
        try:
            # Fallback a psycopg2 (Python 3.11 y anterior)
            import psycopg2
            import psycopg2.extras
            PSYCOPG_VERSION = 2
            DB_TYPE = "postgresql"
            print(f"✅ psycopg2 importado. DB_TYPE={DB_TYPE}")
        except ImportError as e:
            print(f"⚠️  Ningún driver PostgreSQL disponible: {e}")
            DB_TYPE = "none"
            PSYCOPG_VERSION = 0
else:
    try:
        import pyodbc
        PSYCOPG_VERSION = 0
    except ImportError:
        print("⚠️  pyodbc no disponible")
        PSYCOPG_VERSION = 0

app = FastAPI(title="Dashboard BI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Determinar ruta absoluta del directorio static
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"  # Para cargar CSVs

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

def get_db_connection():
    """Conexión a base de datos (SQL Server o PostgreSQL)"""
    if DB_TYPE == "postgresql":
        # PostgreSQL (Render)
        if PSYCOPG_VERSION == 3:
            # psycopg v3
            conn = psycopg.connect(DATABASE_URL)
        else:
            # psycopg2
            conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        # SQL Server (Local)
        server = os.getenv("SQL_SERVER", "DESKTOP-CCBH45L")
        database = os.getenv("SQL_DATABASE", "BI_Prueba")
        driver = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
        
        conn_str = f"DRIVER={{{driver}}}; SERVER={server}; DATABASE={database}; Trusted_Connection=yes;"
        return pyodbc.connect(conn_str)

@app.get("/")
async def root():
    """Servir dashboard"""
    return FileResponse("static/index.html")

@app.get("/api/filters")
async def get_filters():
    """Obtener opciones para filtros (ciudades, canales, categorías, fechas)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ciudades
        cursor.execute("SELECT DISTINCT city FROM stores ORDER BY city")
        cities = [row[0] for row in cursor.fetchall()]
        
        # Canales
        cursor.execute("SELECT DISTINCT channel FROM customers WHERE channel IS NOT NULL ORDER BY channel")
        channels = [row[0] for row in cursor.fetchall()]
        
        # Categorías
        cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        
        # Rango de fechas y meses disponibles
        cursor.execute("""
            SELECT 
                MIN(order_date) as min_date, 
                MAX(order_date) as max_date,
                COUNT(DISTINCT FORMAT(order_date, 'yyyy-MM')) as total_months
            FROM orders WHERE status = 'paid'
        """)
        date_row = cursor.fetchone()
        
        # Lista de meses únicos
        cursor.execute("""
            SELECT DISTINCT FORMAT(order_date, 'yyyy-MM') as month
            FROM orders 
            WHERE status = 'paid'
            ORDER BY month
        """)
        months = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            "cities": cities,
            "channels": channels,
            "categories": categories,
            "months": months,
            "date_range": {
                "min": date_row[0].strftime('%Y-%m-%d') if date_row[0] else None,
                "max": date_row[1].strftime('%Y-%m-%d') if date_row[1] else None,
                "total_months": date_row[2]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/kpis")
async def get_kpis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    channel: Optional[str] = Query(None)
):
    """
    KPIs principales para Executive Dashboard
    Página 1: Net Sales (MTD y YTD), Gross Margin y %, Órdenes, AOV, Unidades, Returns (% y $)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construir WHERE clause
        where_conditions = ["o.status = 'paid'"]
        if start_date:
            where_conditions.append(f"o.order_date >= '{start_date}'")
        if end_date:
            where_conditions.append(f"o.order_date <= '{end_date}'")
        if city:
            where_conditions.append(f"s.city = '{city}'")
        if channel:
            where_conditions.append(f"c.channel = '{channel}'")
        
        where_clause = " AND ".join(where_conditions)
        
        # Query para KPIs
        query = f"""
        WITH base_sales AS (
            SELECT 
                o.order_id,
                o.order_date,
                YEAR(o.order_date) AS year,
                MONTH(o.order_date) AS month,
                oi.qty * oi.unit_price AS gross_sale,
                o.discount_amount / NULLIF((SELECT SUM(qty) FROM order_items WHERE order_id = o.order_id), 0) * oi.qty AS item_discount,
                oi.qty * oi.unit_cost AS cogs,
                oi.qty AS units
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN stores s ON o.store_id = s.store_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE {where_clause}
        ),
        returns_calc AS (
            SELECT 
                ISNULL(SUM(r.amount_returned), 0) AS total_returns
            FROM returns r
            JOIN orders o ON r.order_id = o.order_id
            JOIN stores s ON o.store_id = s.store_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE {where_clause}
        ),
        current_period AS (
            SELECT 
                MAX(YEAR(order_date)) AS current_year,
                MAX(MONTH(order_date)) AS current_month
            FROM orders o
            JOIN stores s ON o.store_id = s.store_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE {where_clause}
        )
        SELECT 
            -- MTD (Month-to-Date del mes MÁS RECIENTE con datos)
            ISNULL((SELECT TOP 1 SUM(gross_sale - item_discount) 
             FROM base_sales 
             GROUP BY year, month
             ORDER BY year DESC, month DESC), 0) AS net_sales_mtd,
            -- YTD (Year-to-Date antes de returns)
            ISNULL((SELECT SUM(gross_sale - item_discount) FROM base_sales), 0) AS gross_ytd,
            -- Gross Margin
            ISNULL((SELECT SUM(gross_sale - item_discount - cogs) FROM base_sales), 0) AS gross_margin,
            -- Total Orders
            (SELECT COUNT(DISTINCT order_id) FROM base_sales) AS total_orders,
            -- Total Units
            (SELECT SUM(units) FROM base_sales) AS total_units,
            -- Total Returns
            (SELECT total_returns FROM returns_calc) AS total_returns,
            -- Gross Sales
            ISNULL((SELECT SUM(gross_sale) FROM base_sales), 0) AS gross_sales
        """
        
        cursor.execute(query)
        row = cursor.fetchone()
        
        net_sales_mtd = float(row[0] or 0)
        gross_ytd = float(row[1] or 0)
        gross_margin = float(row[2] or 0)
        total_orders = int(row[3] or 0)
        total_units = int(row[4] or 0)
        total_returns = float(row[5] or 0)
        gross_sales = float(row[6] or 0)
        
        # Net Sales YTD = Gross YTD - Returns
        net_sales_ytd = gross_ytd - total_returns
        
        # Cálculos derivados
        aov = net_sales_ytd / total_orders if total_orders > 0 else 0
        gross_margin_pct = (gross_margin / net_sales_ytd * 100) if net_sales_ytd > 0 else 0
        return_rate = (total_returns / gross_sales * 100) if gross_sales > 0 else 0
        
        cursor.close()
        conn.close()
        
        return {
            "net_sales_mtd": round(net_sales_mtd, 2),
            "net_sales_ytd": round(net_sales_ytd, 2),
            "gross_margin": round(gross_margin, 2),
            "gross_margin_pct": round(gross_margin_pct, 2),
            "total_orders": total_orders,
            "total_units": total_units,
            "aov": round(aov, 2),
            "return_rate": round(return_rate, 2),
            "total_returns": round(total_returns, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en /api/kpis: {str(e)}")

@app.get("/api/monthly-trend")
async def get_monthly_trend(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    channel: Optional[str] = Query(None)
):
    """Tendencia mensual con variación vs mes anterior"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        where_conditions = ["o.status = 'paid'"]
        if start_date:
            where_conditions.append(f"o.order_date >= '{start_date}'")
        if end_date:
            where_conditions.append(f"o.order_date <= '{end_date}'")
        if city:
            where_conditions.append(f"s.city = '{city}'")
        if channel:
            where_conditions.append(f"c.channel = '{channel}'")
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
        WITH monthly_base AS (
            SELECT 
                FORMAT(o.order_date, 'yyyy-MM') AS month,
                o.order_id,
                SUM(oi.qty * oi.unit_price) AS item_sales,
                o.discount_amount
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN stores s ON o.store_id = s.store_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE {where_clause}
            GROUP BY FORMAT(o.order_date, 'yyyy-MM'), o.order_id, o.discount_amount
        ),
        monthly_agg AS (
            SELECT 
                month,
                SUM(item_sales) AS gross_sales,
                SUM(discount_amount) AS discounts
            FROM monthly_base
            GROUP BY month
        ),
        monthly_returns AS (
            SELECT 
                FORMAT(o.order_date, 'yyyy-MM') AS month,
                SUM(r.amount_returned) AS returns
            FROM returns r
            JOIN orders o ON r.order_id = o.order_id
            JOIN stores s ON o.store_id = s.store_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE {where_clause}
            GROUP BY FORMAT(o.order_date, 'yyyy-MM')
        )
        SELECT 
            ma.month,
            ma.gross_sales,
            ma.discounts,
            ISNULL(mr.returns, 0) AS returns,
            ma.gross_sales - ma.discounts - ISNULL(mr.returns, 0) AS net_sales,
            LAG(ma.gross_sales - ma.discounts - ISNULL(mr.returns, 0), 1) OVER (ORDER BY ma.month) AS prev_net_sales
        FROM monthly_agg ma
        LEFT JOIN monthly_returns mr ON ma.month = mr.month
        ORDER BY ma.month
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            net_sales = float(row[4])
            prev_sales = float(row[5]) if row[5] else net_sales
            pct_change = ((net_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
            
            result.append({
                "month": row[0],
                "gross_sales": round(float(row[1]), 2),
                "discounts": round(float(row[2]), 2),
                "returns": round(float(row[3]), 2),
                "net_sales": round(net_sales, 2),
                "pct_change": round(pct_change, 2)
            })
        
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en /api/monthly-trend: {str(e)}")

@app.get("/api/sales-by-city")
async def get_sales_by_city(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    channel: Optional[str] = Query(None)
):
    """Net Sales por ciudad (NO filtrar por ciudad aquí)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        where_conditions = ["o.status = 'paid'"]
        if start_date:
            where_conditions.append(f"o.order_date >= '{start_date}'")
        if end_date:
            where_conditions.append(f"o.order_date <= '{end_date}'")
        if channel:
            where_conditions.append(f"c.channel = '{channel}'")
        # NO filtrar por ciudad - queremos ver TODAS las ciudades
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
        WITH order_totals AS (
            SELECT 
                o.order_id,
                o.store_id,
                SUM(oi.qty * oi.unit_price) AS order_sales,
                o.discount_amount
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE {where_clause}
            GROUP BY o.order_id, o.store_id, o.discount_amount
        )
        SELECT 
            s.city,
            SUM(ot.order_sales - ot.discount_amount) AS net_sales
        FROM order_totals ot
        JOIN stores s ON ot.store_id = s.store_id
        GROUP BY s.city
        ORDER BY net_sales DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        result = [{"city": row[0], "net_sales": round(float(row[1]), 2)} for row in rows]
        
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en /api/sales-by-city: {str(e)}")

@app.get("/api/sales-by-channel")
async def get_sales_by_channel(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    city: Optional[str] = Query(None)
):
    """Net Sales por canal"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        where_conditions = ["o.status = 'paid'"]
        if start_date:
            where_conditions.append(f"o.order_date >= '{start_date}'")
        if end_date:
            where_conditions.append(f"o.order_date <= '{end_date}'")
        if city:
            where_conditions.append(f"s.city = '{city}'")
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
        SELECT 
            c.channel,
            SUM(oi.qty * oi.unit_price) AS net_sales,
            COUNT(DISTINCT o.order_id) AS orders
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN stores s ON o.store_id = s.store_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE {where_clause}
        GROUP BY c.channel
        ORDER BY net_sales DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        result = [{"channel": row[0], "net_sales": round(float(row[1]), 2), "orders": int(row[2])} for row in rows]
        
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en /api/sales-by-channel: {str(e)}")

@app.get("/api/sales-by-category")
async def get_sales_by_category(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    channel: Optional[str] = Query(None)
):
    """Net Sales por categoría con % mix"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        where_conditions = ["o.status = 'paid'"]
        if start_date:
            where_conditions.append(f"o.order_date >= '{start_date}'")
        if end_date:
            where_conditions.append(f"o.order_date <= '{end_date}'")
        if city:
            where_conditions.append(f"s.city = '{city}'")
        if channel:
            where_conditions.append(f"c.channel = '{channel}'")
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
        WITH category_sales AS (
            SELECT 
                p.category,
                SUM(oi.qty * oi.unit_price) AS gross_sales
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN stores s ON o.store_id = s.store_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE {where_clause}
            GROUP BY p.category
        )
        SELECT 
            category,
            gross_sales,
            gross_sales * 100.0 / SUM(gross_sales) OVER () AS pct_mix
        FROM category_sales
        ORDER BY gross_sales DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        result = [{"category": row[0], "net_sales": round(float(row[1]), 2), "pct_mix": round(float(row[2]), 2)} for row in rows]
        
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en /api/sales-by-category: {str(e)}")

@app.get("/api/top-products")
async def get_top_products(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    channel: Optional[str] = Query(None)
):
    """Top 10 productos por margen bruto"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        where_conditions = ["o.status = 'paid'"]
        if start_date:
            where_conditions.append(f"o.order_date >= '{start_date}'")
        if end_date:
            where_conditions.append(f"o.order_date <= '{end_date}'")
        if city:
            where_conditions.append(f"s.city = '{city}'")
        if channel:
            where_conditions.append(f"c.channel = '{channel}'")
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
        SELECT TOP 10
            p.category + '-' + p.brand AS product_name,
            SUM(oi.qty * oi.unit_price) AS revenue,
            SUM(oi.qty * oi.unit_cost) AS cogs,
            SUM(oi.qty * (oi.unit_price - oi.unit_cost)) AS gross_margin,
            (SUM(oi.qty * (oi.unit_price - oi.unit_cost)) * 100.0 / NULLIF(SUM(oi.qty * oi.unit_price), 0)) AS gross_margin_pct
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        JOIN stores s ON o.store_id = s.store_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE {where_clause}
        GROUP BY p.category, p.brand
        ORDER BY gross_margin DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        result = [
            {
                "product_name": row[0],
                "revenue": round(float(row[1]), 2),
                "cogs": round(float(row[2]), 2),
                "gross_margin": round(float(row[3]), 2),
                "gross_margin_pct": round(float(row[4]), 2)
            } for row in rows
        ]
        
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en /api/top-products: {str(e)}")

@app.get("/api/new-vs-returning")
async def get_new_vs_returning(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    channel: Optional[str] = Query(None)
):
    """Clientes nuevos vs recurrentes por mes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        where_conditions = ["o.status = 'paid'"]
        if start_date:
            where_conditions.append(f"o.order_date >= '{start_date}'")
        if end_date:
            where_conditions.append(f"o.order_date <= '{end_date}'")
        if city:
            where_conditions.append(f"s.city = '{city}'")
        if channel:
            where_conditions.append(f"c.channel = '{channel}'")
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
        WITH first_purchase AS (
            SELECT 
                o.customer_id,
                FORMAT(MIN(o.order_date), 'yyyy-MM') AS cohort_month
            FROM orders o
            WHERE o.status = 'paid'
            GROUP BY o.customer_id
        ),
        monthly_orders AS (
            SELECT 
                FORMAT(o.order_date, 'yyyy-MM') AS month,
                o.customer_id,
                fp.cohort_month
            FROM orders o
            JOIN stores s ON o.store_id = s.store_id
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN first_purchase fp ON o.customer_id = fp.customer_id
            WHERE {where_clause}
        )
        SELECT 
            month,
            COUNT(DISTINCT CASE WHEN month = cohort_month THEN customer_id END) AS new_customers,
            COUNT(DISTINCT CASE WHEN month != cohort_month THEN customer_id END) AS returning_customers
        FROM monthly_orders
        GROUP BY month
        ORDER BY month
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        result = [
            {
                "month": row[0],
                "new_customers": int(row[1]),
                "returning_customers": int(row[2])
            } for row in rows
        ]
        
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en /api/new-vs-returning: {str(e)}")

# ============================================================================
# ADMIN ENDPOINTS - Inicialización de Datos
# ============================================================================

from init_data import router as init_router
app.include_router(init_router, tags=["admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
