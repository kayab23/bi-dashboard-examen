"""
Script mejorado para cargar datos CSV a PostgreSQL en Render
Maneja CSVs sin headers y limpieza de datos duplicados
"""
import psycopg2
import csv
from pathlib import Path
from decimal import Decimal

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
    conn.autocommit = False
    print("✅ Conexión exitosa\n")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit(1)

# 1. Limpiar tablas existentes (en orden correcto por FK)
print("🗑️  Limpiando tablas existentes...")
try:
    cursor.execute("DROP TABLE IF EXISTS returns CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS order_items CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS orders CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS products CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS stores CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS customers CASCADE;")
    conn.commit()
    print("✅ Tablas eliminadas\n")
except Exception as e:
    print(f"⚠️  Error limpiando: {e}\n")
    conn.rollback()

# 2. Crear schema
print("📋 Creando schema...")
try:
    with open(BASE_DIR / "schema_postgres.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
        cursor.execute(schema_sql)
        conn.commit()
        print("✅ Schema creado\n")
except Exception as e:
    print(f"❌ Error creando schema: {e}\n")
    conn.rollback()
    exit(1)

# 3. Cargar CSVs con mapeo correcto
print("📊 Cargando datos...\n")

# Mapeo: tabla -> (archivo, columnas_en_csv, columnas_en_tabla)
# Los CSVs de sqlcmd tienen el orden exacto de SELECT *
tables_config = [
    {
        "table": "customers",
        "file": "customers.csv",
        "columns": ["customer_id", "created_at", "country", "channel"]
    },
    {
        "table": "stores", 
        "file": "stores.csv",
        "columns": ["store_id", "store_name", "city"]
    },
    {
        "table": "products",
        "file": "products.csv",
        # Orden real en CSV: product_id, category, brand, unit_price(?), unit_cost(?)
        # Pero products solo tiene: product_id, category, brand
        "columns": ["product_id", "category", "brand"]
    },
    {
        "table": "orders",
        "file": "orders.csv",
        # CSV order: order_id, customer_id, order_date(?), store_id, status, total_amount, discount_amount, shipping_amount
        "columns": ["order_id", "customer_id", "order_date", "store_id", "status", "total_amount", "discount_amount", "shipping_amount"]
    },
    {
        "table": "order_items",
        "file": "order_items.csv",
        "columns": ["order_item_id", "order_id", "product_id", "qty", "unit_price", "unit_cost"]
    },
    {
        "table": "returns",
        "file": "returns.csv",
        "columns": ["return_id", "order_id", "return_date", "amount_returned", "reason"]
    },
]

for config in tables_config:
    table = config["table"]
    csv_file = DATA_DIR / config["file"]
    columns = config["columns"]
    
    print(f"  [{table}] Cargando desde {config['file']}...", end=" ", flush=True)
    
    try:
        # Leer CSV (sin headers, remover duplicados)
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Remover duplicados por ID (primera columna)
        seen_ids = set()
        unique_rows = []
        for row in rows:
            if row and row[0] not in seen_ids:
                seen_ids.add(row[0])
                # Tomar solo las columnas que necesitamos
                unique_rows.append(row[:len(columns)])
        
        if not unique_rows:
            print("⚠️  Archivo vacío")
            continue
        
        # Preparar INSERT
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Insertar por lotes
        batch_size = 500
        inserted = 0
        for i in range(0, len(unique_rows), batch_size):
            batch = unique_rows[i:i+batch_size]
            cursor.executemany(insert_sql, batch)
            inserted += len(batch)
        
        conn.commit()
        print(f"✅ {inserted} registros")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        # Continuar con la siguiente tabla

# 4. Actualizar secuencias
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
        cursor.execute(f"SELECT setval('{table}_{id_column}_seq', (SELECT COALESCE(MAX({id_column}), 1) FROM {table}));")
        conn.commit()
    except Exception as e:
        print(f"  ⚠️  {table}: {e}")

print("✅ Secuencias actualizadas\n")

# 5. Verificar carga
print("📊 Verificación de datos:\n")

verify_queries = [
    ("customers", "SELECT COUNT(*) FROM customers"),
    ("stores", "SELECT COUNT(*) FROM stores"),
    ("products", "SELECT COUNT(*) FROM products"),
    ("orders", "SELECT COUNT(*) FROM orders"),
    ("order_items", "SELECT COUNT(*) FROM order_items"),
    ("returns", "SELECT COUNT(*) FROM returns"),
]

total_records = 0
for table, query in verify_queries:
    cursor.execute(query)
    count = cursor.fetchone()[0]
    total_records += count
    print(f"  ✅ {table.ljust(15)} - {count:>6,} registros")

print(f"\n  📦 Total:           {total_records:>6,} registros")

# Verificar totales de negocio
print("\n📈 Validación de métricas:\n")

try:
    cursor.execute("""
        SELECT 
            COALESCE(SUM(oi.qty * oi.unit_price), 0) as gross_sales,
            COALESCE(SUM(o.discount_amount), 0) as total_discounts,
            COUNT(DISTINCT o.order_id) as total_orders
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status = 'paid'
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"  💰 Gross Sales:     ${float(result[0]):>12,.2f}")
        print(f"  🎟️  Total Discounts: ${float(result[1]):>12,.2f}")
        print(f"  📦 Total Orders:    {result[2]:>12,}")
except Exception as e:
    print(f"  ⚠️  Error calculando métricas: {e}")

cursor.close()
conn.close()

print("\n✅ Carga completada exitosamente!")
print("🎯 PostgreSQL en Render está listo con todos los datos")
print("\n⏭️  SIGUIENTE PASO: Crear Web Service en Render")
