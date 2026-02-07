"""
Script OPTIMIZADO para cargar datos CSV a PostgreSQL Render
Con progress bar y manejo de errores mejorado
"""
import psycopg2
import csv
from pathlib import Path
import sys

DATABASE_URL = "postgresql://bi_prueba_user:85BgxjeqGd6TGB1ogDR7UUGwcuskFyqk@dpg-d63pn0er433s73dtmhkg-a.oregon-postgres.render.com/bi_prueba"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

print("🚀 Carga OPTIMIZADA a PostgreSQL Render\n")

# Conectar
print("📡 Conectando...")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
conn.autocommit = False
print("✅ Conectado\n")

# Limpiar
print("🗑️  Limpiando...")
cursor.execute("DROP TABLE IF EXISTS returns, order_items, orders, products, stores, customers CASCADE;")
conn.commit()
print("✅ Limpiado\n")

# Schema
print("📋 Creando schema...")
with open(BASE_DIR / "schema_postgres.sql", "r", encoding="utf-8") as f:
    cursor.execute(f.read())
    conn.commit()
print("✅ Schema creado\n")

print("📊 Cargando datos:\n")

# Configuración optimizada
configs = [
    ("customers", ["customer_id", "created_at", "country", "channel"], 1000, True),
    ("stores", ["store_id", "store_name", "city"], 100, True),
    ("products", ["product_id", "category", "brand"], 100, True),
    ("orders", ["order_id", "customer_id", "order_date", "store_id", "status", "total_amount", "discount_amount", "shipping_amount"], 1000, True),
    ("order_items", ["order_id", "product_id", "qty", "unit_price", "unit_cost"], 2000, False),  # Sin PK serial
    ("returns", ["return_id", "order_id", "return_date", "amount_returned"], 500, True),  # Con return_id
]

for table, columns, batch_size, has_sequence in configs:
    csv_file = DATA_DIR / f"{table}.csv"
    print(f"  [{table}]", end=" ", flush=True)
    
    try:
        # Leer y limpiar
        with open(csv_file, "r", encoding="utf-8") as f:
            rows = []
            seen = set()
            for row in csv.reader(f):
                if row and row[0] not in seen:
                    seen.add(row[0])
                    rows.append(row[:len(columns)])
        
        if not rows:
            print("⚠️  Vacío")
            continue
        
        # Insertar en lotes grandes
        placeholders = ",".join(["%s"] * len(columns))
        sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
        
        total = len(rows)
        for i in range(0, total, batch_size):
            batch = rows[i:i+batch_size]
            cursor.executemany(sql, batch)
            progress = min(i + batch_size, total)
            print(f"\r  [{table}] {progress}/{total}", end="", flush=True)
        
        conn.commit()
        print(f"\r  [{table}] ✅ {total:,} registros")
    
    except Exception as e:
        print(f"\r  [{table}] ❌ {str(e)[:50]}")
        conn.rollback()

# Secuencias
print("\n🔄 Secuencias...", end=" ", flush=True)
for table, cols, _, has_seq in configs:
    if has_seq:
        cursor.execute(f"SELECT setval('{table}_{cols[0]}_seq', COALESCE((SELECT MAX({cols[0]}) FROM {table}), 1));")
conn.commit()
print("✅")

# Verificar
print("\n📊 Ver, _ificación:\n")
for table, _, _ in configs:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table.ljust(15)} {cursor.fetchone()[0]:>6,}")

cursor.execute("""
    SELECT 
        COALESCE(SUM(oi.qty * oi.unit_price), 0),
        COUNT(DISTINCT o.order_id)
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status = 'paid'
""")
result = cursor.fetchone()
if result and result[0]:
    print(f"\n  💰 Gross Sales: ${float(result[0]):,.2f}")
    print(f"  📦 Órdenes:     {result[1]:,}")
else:
    print("\n  ⚠️  No hay datos de ventas")

cursor.close()
conn.close()

print("\n✅ COMPLETADO!")
print("⏭️  SIGUIENTE: Crear Web Service en Render")
