"""
Script para cargar datos CSV a PostgreSQL en Render
Usa psycopg2 desde Python (no requiere psql instalado)
"""
import psycopg2
import csv
import os
from pathlib import Path

# Credenciales PostgreSQL Render
DATABASE_URL = "postgresql://bi_prueba_user:85BgxjeqGd6TGB1ogDR7UUGwcuskFyqk@dpg-d63pn0er433s73dtmhkg-a.oregon-postgres.render.com/bi_prueba"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

print("🚀 Iniciando carga de datos a PostgreSQL Render...\n")

# Conectar a PostgreSQL
print("📡 Conectando a PostgreSQL...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("✅ Conexión exitosa\n")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit(1)

# 1. Crear schema
print("📋 Creando schema...")
try:
    with open(BASE_DIR / "schema_postgres.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
        cursor.execute(schema_sql)
        conn.commit()
        print("✅ Schema creado\n")
except Exception as e:
    print(f"⚠️  Schema ya existe o error: {e}\n")
    conn.rollback()

# 2. Cargar CSVs
tables_config = [
    {"table": "customers", "file": "customers.csv", "columns": ["customer_id", "created_at", "country", "channel"]},
    {"table": "stores", "file": "stores.csv", "columns": ["store_id", "store_name", "city"]},
    {"table": "products", "file": "products.csv", "columns": ["product_id", "category", "brand"]},
    {"table": "orders", "file": "orders.csv", "columns": ["order_id", "customer_id", "store_id", "order_date", "status", "total_amount", "discount_amount", "shipping_amount"]},
    {"table": "order_items", "file": "order_items.csv", "columns": ["order_item_id", "order_id", "product_id", "qty", "unit_price", "unit_cost"]},
    {"table": "returns", "file": "returns.csv", "columns": ["return_id", "order_id", "return_date", "amount_returned", "reason"]},
]

print("📊 Cargando datos...\n")

for config in tables_config:
    table = config["table"]
    csv_file = DATA_DIR / config["file"]
    columns = config["columns"]
    
    print(f"  [{table}] Cargando desde {config['file']}...", end=" ")
    
    try:
        # Limpiar tabla si existe
        cursor.execute(f"DELETE FROM {table};")
        
        # Leer CSV y insertar datos (sin headers)
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            if not rows:
                print("⚠️  Archivo vacío")
                continue
            
            # Preparar INSERT
            placeholders = ", ".join(["%s"] * len(columns))
            insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Insertar por lotes
            batch_size = 1000
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                values = [[val.strip() if val.strip() else None for val in row] for row in batch]
                cursor.executemany(insert_sql, values)
            
            conn.commit()
            print(f"✅ {len(rows)} registros")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()

# 3. Actualizar secuencias
print("\n🔄 Actualizando secuencias...")
sequences = [
    ("customers", "customer_id"),
    ("stores", "store_id"),
    ("products", "product_id"),
    ("orders", "order_id"),
    ("order_items", "order_item_id"),
    ("returns", "return_id"),
]

for table, id_column in sequences:
    try:
        cursor.execute(f"SELECT setval('{table}_{id_column}_seq', (SELECT MAX({id_column}) FROM {table}));")
        conn.commit()
    except:
        pass

print("✅ Secuencias actualizadas\n")

# 4. Verificar carga
print("📊 Verificación de datos:\n")

verify_queries = [
    ("customers", "SELECT COUNT(*) FROM customers"),
    ("stores", "SELECT COUNT(*) FROM stores"),
    ("products", "SELECT COUNT(*) FROM products"),
    ("orders", "SELECT COUNT(*) FROM orders"),
    ("order_items", "SELECT COUNT(*) FROM order_items"),
    ("returns", "SELECT COUNT(*) FROM returns"),
]

for table, query in verify_queries:
    cursor.execute(query)
    count = cursor.fetchone()[0]
    print(f"  ✅ {table.ljust(15)} - {count:>6,} registros")

# Verificar totales de negocio
print("\n📈 Validación de métricas:\n")

cursor.execute("""
    SELECT 
        SUM(oi.qty * oi.unit_price) as gross_sales,
        SUM(o.discount_amount) as total_discounts,
        COUNT(DISTINCT o.order_id) as total_orders
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status = 'paid'
""")

result = cursor.fetchone()
if result and result[0]:
    print(f"  💰 Gross Sales:     ${result[0]:>12,.2f}")
    print(f"  🎟️  Total Discounts: ${result[1]:>12,.2f}")
    print(f"  📦 Total Orders:    {result[2]:>12,}")
else:
    print("  ⚠️  No hay datos para calcular métricas")

cursor.close()
conn.close()

print("\n✅ Carga completada exitosamente!")
print("🎯 PostgreSQL en Render está listo con todos los datos")
