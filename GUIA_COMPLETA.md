# 📋 Guía Completa: Dashboard BI - Despliegue Render + Power BI

Este documento detalla todos los pasos para completar el examen BI con ambas versiones del dashboard.

---

## 🎯 Objetivos

1. **Dashboard Web** - Deployable en Render, accesible vía URL pública
2. **Dashboard Power BI** - Local con datos embebidos + exportación PDF

---

## 🚀 PARTE 1: Dashboard Web (Render + PostgreSQL)

### Paso 1: Exportar Datos SQL Server → CSV

```powershell
cd dashboard_web
.\export_data.ps1
```

**Resultado esperado:** 6 archivos CSV en `c:\temp\`
- customers.csv
- stores.csv  
- products.csv
- orders.csv
- order_items.csv
- returns.csv

---

### Paso 2: Crear Base de Datos PostgreSQL en Render

1. Ir a [https://render.com](https://render.com)
2. Crear cuenta gratuita (con GitHub)
3. Click **"New" → "PostgreSQL"**
4. Configurar:
   - **Name:** `bi-dashboard-db`
   - **Database:** `bi_prueba`
   - **Region:** Oregon (US West)
   - **Instance Type:** Free
5. Click **"Create Database"**
6. Esperar ~1 minuto a que se active
7. **Copiar la "External Database URL"** (formato: `postgresql://user:password@dpg-XXXX-a.oregon-postgres.render.com/bi_prueba`)

---

### Paso 3: Cargar Schema y Datos a PostgreSQL

```powershell
# Instalar psql si no está instalado (Windows con Chocolatey)
choco install postgresql

# Conectar a PostgreSQL de Render
$DB_URL = "postgresql://user:password@dpg-XXXX-a.oregon-postgres.render.com/bi_prueba"
psql $DB_URL

# Dentro de psql:
\i dashboard_web/schema_postgres.sql

# Cargar cada CSV:
\copy customers FROM 'c:/temp/customers.csv' DELIMITER ',' CSV HEADER;
\copy stores FROM 'c:/temp/stores.csv' DELIMITER ',' CSV HEADER;
\copy products FROM 'c:/temp/products.csv' DELIMITER ',' CSV HEADER;
\copy orders FROM 'c:/temp/orders.csv' DELIMITER ',' CSV HEADER;
\copy order_items FROM 'c:/temp/order_items.csv' DELIMITER ',' CSV HEADER;
\copy returns FROM 'c:/temp/returns.csv' DELIMITER ',' CSV HEADER;

# Verificar datos:
SELECT COUNT(*) FROM orders;  -- Debe ser ~18000

\q
```

**Problema con CSV?** Si sqlcmd genera formato incompatible, usa alternativa:

```powershell
# Alternativa: Export a CSV limpio desde PowerShell
$tables = @("customers", "stores", "products", "orders", "order_items", "returns")
foreach ($table in $tables) {
    Invoke-Sqlcmd -ServerInstance "DESKTOP-CCBH45L" -Database "BI_Prueba" -Query "SELECT * FROM $table" | 
    Export-Csv "c:\temp\$table.csv" -NoTypeInformation
}
```

---

### Paso 4: Crear Repositorio GitHub

```powershell
cd dashboard_web
git init
git add .
git commit -m "Initial commit - Dashboard BI Examen"

# Crear repo en GitHub (vía web): https://github.com/new
# Nombre sugerido: bi-dashboard-examen

git remote add origin https://github.com/TU_USUARIO/bi-dashboard-examen.git
git branch -M main
git push -u origin main
```

---

### Paso 5: Deploy Web Service en Render

1. En Render, click **"New" → "Web Service"**
2. Click **"Connect a repository"** → Seleccionar tu repo de GitHub
3. Configurar:
   - **Name:** `bi-dashboard-examen`
   - **Region:** Oregon (US West)
   - **Root Directory:** `.` (dejar vacío o `dashboard_web` si está en subdirectorio)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
4. **Variables de entorno:**
   - Click "Advanced" → "Add Environment Variable"
   - **Key:** `DATABASE_URL`
   - **Value:** (pegar la Internal Database URL de PostgreSQL Render)
     - **Importante:** Usar la **Internal** Database URL, NO la External
     - Formato: `postgresql://user:password@dpg-XXXX:5432/bi_prueba`
5. Click **"Create Web Service"**
6. Esperar ~5 minutos al deploy

---

### Paso 6: Verificar Dashboard Web

**URL:** `https://bi-dashboard-examen-XXXX.onrender.com`

**Checklist de verificación:**
- [ ] KPI Cards muestran valores correctos (Net Sales ~$4.2M YTD)
- [ ] Gráfico de tendencia mensual renderiza
- [ ] Página "Drivers Dashboard" muestra ventas por ciudad y top productos
- [ ] No hay errores en la consola del navegador

**Si hay errores:**
1. Ver logs en Render: Panel del servicio → "Logs"
2. Verificar DATABASE_URL está correcta
3. Verificar que las tablas tienen datos: `psql $DB_URL -c "SELECT COUNT(*) FROM orders"`

---

## 💼 PARTE 2: Dashboard Power BI Local

### Paso 1: Instalar Power BI Desktop

- Descargar: [https://powerbi.microsoft.com/desktop](https://powerbi.microsoft.com/desktop)
- Versión requerida: Desktop (gratuita)

---

### Paso 2: Conectar a SQL Server

1. Abrir Power BI Desktop
2. **"Obtener datos" → "SQL Server"**
3. Configurar conexión:
   - **Servidor:** `DESKTOP-CCBH45L`
   - **Base de datos:** `BI_Prueba`
   - **Modo de conectividad:** **Import** (NO DirectQuery)
4. Seleccionar tablas:
   - [x] customers
   - [x] stores
   - [x] products
   - [x] orders
   - [x] order_items
   - [x] returns
5. Click **"Cargar"**

---

### Paso 3: Crear Relaciones (Model View)

En la vista de "Modelo":

```
orders (1) → (*) order_items  [order_id]
customers (1) → (*) orders    [customer_id]
stores (1) → (*) orders       [store_id]
products (1) → (*) order_items [product_id]
orders (1) → (*) returns      [order_id]
```

**Cardinalidades:**
- orders → order_items: 1:N
- customers → orders: 1:N
- stores → orders: 1:N
- products → order_items: 1:N
- orders → returns: 1:N

---

### Paso 4: Crear Medidas DAX

```dax
Net Sales = 
VAR GrossSales = SUMX(order_items, order_items[qty] * order_items[unit_price])
VAR Discounts = SUM(orders[discount_amount])
VAR Returns = CALCULATE(SUMX(returns, returns[quantity] * RELATED(order_items[unit_price])))
RETURN GrossSales - Discounts - Returns

Gross Margin = 
VAR Revenue = [Net Sales]
VAR COGS = SUMX(order_items, order_items[qty] * RELATED(products[cost]))
RETURN Revenue - COGS

Gross Margin % = 
DIVIDE([Gross Margin], [Net Sales], 0)

Total Orders = 
COUNTROWS(orders)

AOV (Average Order Value) = 
DIVIDE([Net Sales], [Total Orders], 0)

Return Rate % = 
VAR TotalItems = SUM(order_items[qty])
VAR ReturnedItems = SUM(returns[quantity])
RETURN DIVIDE(ReturnedItems, TotalItems, 0) * 100
```

---

### Paso 5: Crear Página 1 - Executive Dashboard

**Elementos:**

1. **KPI Cards** (6 tarjetas)
   - Net Sales MTD: $774K (filtro: mes actual en slicer)
   - Net Sales YTD: $4.2M
   - Gross Margin: 22.4%
   - Total Orders: 18,000
   - AOV: $234
   - Return Rate: 2.8%

2. **Line Chart**: Monthly Sales Trend
   - Eje X: order_date (Month)
   - Eje Y: [Net Sales]
   - Línea secundaria: [Gross Margin]

3. **Gauge Chart**: Return Rate %
   - Valor: [Return Rate %]
   - Máximo: 10%
   - Zonas: 0-3% (verde), 3-6% (amarillo), 6-10% (rojo)

4. **Slicers** (filtros interactivos)
   - Date Range (order_date)
   - City (stores[city])
   - Channel (customers[channel])

---

### Paso 6: Crear Página 2 - Drivers Dashboard

**Elementos:**

1. **Map Visual**: Sales by City
   - Location: stores[city] + stores[country]
   - Size: [Net Sales]
   - Color: [Gross Margin %]

2. **Bar Chart**: Top 10 Products by Gross Margin
   - Eje Y: products[product_name]
   - Eje X: [Gross Margin]
   - Ordenar: Descendente
   - Filtro: Top 10

3. **Stacked Column Chart**: Customer Mix (Online vs Store)
   - Eje X: order_date (Month)
   - Eje Y: [Net Sales]
   - Leyenda: customers[channel]

4. **Table**: Store Performance
   - Columnas:
     - stores[city]
     - stores[store_name]
     - [Net Sales]
     - [Total Orders]
     - [AOV]
     - [Return Rate %]
   - Ordenar por [Net Sales] DESC

---

### Paso 7: Formatear Dashboards

**Tema y colores:**
- Fondo: Blanco o gris claro (#F8FAFC)
- Colores primarios: Gradiente morado (#667eea → #764ba2)
- Fuente: Segoe UI

**Interactividad:**
- Aplicar slicers a ambas páginas
- Configurar tooltips en gráficos
- Agregar botones de navegación entre páginas

---

### Paso 8: Guardar y Exportar

1. **Guardar .pbix:**
   ```
   dashboard_web/bi_dashboard_examen.pbix
   ```

2. **Exportar a PDF:**
   - Archivo → Exportar → Exportar a PDF
   - Opciones:
     - [x] Página 1: Executive Dashboard
     - [x] Página 2: Drivers Dashboard
   - Guardar como:
     ```
     respuestas_examen_bi/bi_dashboard_examen.pdf
     ```

---

## ✅ PARTE 3: Entrega Final

### Estructura de carpetas final:

```
bi_prueba_dataset/
├── respuestas_examen_bi/
│   ├── README.md
│   ├── answers.sql
│   ├── answers_ejecutable.sql
│   ├── respuestas_seccion2.md
│   ├── star_schema_design.sql
│   ├── insights.md
│   ├── bi_dashboard_examen.pbix    # ← Nuevo
│   └── bi_dashboard_examen.pdf     # ← Nuevo
└── dashboard_web/
    ├── app.py
    ├── requirements.txt
    ├── schema_postgres.sql
    ├── static/
    │   ├── index.html
    │   ├── style.css
    │   └── script.js
    ├── .env.example
    ├── .gitignore
    ├── export_data.ps1
    └── README.md
```

### Documento de Entrega

Crear archivo `respuestas_examen_bi/ENTREGA.md`:

```markdown
# Entrega Examen BI - [TU NOMBRE]

## 📊 Dashboards

### Dashboard Web (Render)
- **URL:** https://bi-dashboard-examen-XXXX.onrender.com
- **Repositorio:** https://github.com/TU_USUARIO/bi-dashboard-examen
- **Tecnología:** FastAPI + PostgreSQL + Plotly.js
- **Estado:** ✅ Deployado y funcional

### Dashboard Power BI
- **Archivo:** bi_dashboard_examen.pbix
- **PDF:** bi_dashboard_examen.pdf
- **Páginas:** Executive Dashboard + Drivers Dashboard

## 📄 Documentación

- **Queries SQL:** answers.sql (5 queries, 60 pts)
- **Business Thinking:** respuestas_seccion2.md (5 preguntas, 25 pts)
- **Star Schema:** star_schema_design.sql (15 pts)
- **Insights:** insights.md (análisis completo con KPIs y recomendaciones)

## 🎯 Puntos Destacados

- Arquitectura escalable con FastAPI + PostgreSQL
- Dashboard responsivo con Plotly.js
- Power BI con medidas DAX optimizadas
- Star schema con granularidad LINE ITEM
- Insights con impacto calculado ($230K-$370K)

## 📧 Contacto

- **Email:** tu.email@example.com
- **GitHub:** github.com/TU_USUARIO
```

---

## 🐛 Troubleshooting

### Error: DATABASE_URL not found
**Solución:** Verificar variable de entorno en Render configurada correctamente

### Error: psycopg2 connection failed
**Solución:** Usar Internal Database URL, no External

### Error: CSV import failed en PostgreSQL
**Solución:** Limpiar CSVs con PowerShell Export-Csv en lugar de sqlcmd

### Power BI: Relaciones no se crean automáticamente
**Solución:** Crear manualmente en vista de Modelo con cardinalidad correcta

### Render: Deploy failed - ModuleNotFoundError
**Solución:** Verificar requirements.txt tiene todas las dependencias

---

## 📞 Recursos Adicionales

- **Render Docs:** https://render.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Power BI DAX:** https://dax.guide
- **PostgreSQL COPY:** https://www.postgresql.org/docs/current/sql-copy.html

---

**Fecha de entrega sugerida:** [FECHA]

**Puntuación esperada:** 100/100 pts

✅ **¡Éxito con tu examen BI!** 🚀
