"""
Endpoint de inicialización para cargar datos CSV a PostgreSQL
Se ejecuta UNA VEZ después del deploy
"""
from fastapi import APIRouter, HTTPException
import csv
from pathlib import Path

router = APIRouter()

@router.post("/admin/init-database")
async def initialize_database():
    """
    Carga los CSVs a PostgreSQL
    ⚠️ Solo ejecutar UNA VEZ después del deploy
    """
    try:
        from app import get_db_connection, DATA_DIR
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        results = {"status": "success", "tables": {}}
        
        # 1. Limpiar tablas
        cursor.execute("DROP TABLE IF EXISTS returns, order_items, orders, products, stores, customers CASCADE;")
        conn.commit()
        
        # 2. Crear schema
        schema_file = Path(__file__).parent / "schema_postgres.sql"
        with open(schema_file, "r", encoding="utf-8") as f:
            cursor.execute(f.read())
            conn.commit()
        
        # 3. Cargar datos
        tables = [
            ("customers", ["customer_id", "created_at", "country", "channel"]),
            ("stores", ["store_id", "store_name", "city"]),
            ("products", ["product_id", "category", "brand"]),
            ("orders", ["order_id", "customer_id", "order_date", "store_id", "status", "total_amount", "discount_amount", "shipping_amount"]),
            ("order_items", ["order_id", "product_id", "qty", "unit_price", "unit_cost"]),
            ("returns", ["return_id", "order_id", "return_date", "amount_returned"]),
        ]
        
        for table, columns in tables:
            csv_file = DATA_DIR / f"{table}.csv"
            
            with open(csv_file, "r", encoding="utf-8") as f:
                rows = []
                seen = set()
                for row in csv.reader(f):
                    if row and row[0] not in seen:
                        seen.add(row[0])
                        rows.append(row[:len(columns)])
            
            placeholders = ",".join(["%s"] * len(columns))
            sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
            
            cursor.executemany(sql, rows)
            conn.commit()
            
            results["tables"][table] = len(rows)
        
        # 4. Actualizar secuencias
        for table, cols in tables:
            if table != "order_items":  # order_items no tiene PK serial
                cursor.execute(f"SELECT setval('{table}_{cols[0]}_seq', COALESCE((SELECT MAX({cols[0]}) FROM {table}), 1));")
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/admin/database-status")
async def database_status():
    """
    Verifica el estado de la base de datos
    """
    try:
        from app import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        tables = ["customers", "stores", "products", "orders", "order_items", "returns"]
        counts = {}
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except:
                counts[table] = "tabla no existe"
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "counts": counts}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
