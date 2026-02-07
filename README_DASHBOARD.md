# Dashboard BI - Examen Business Intelligence

## 🎯 Descripción

Dashboard interactivo que cumple con **TODOS** los requerimientos del examen BI:

### ✅ Página 1: Executive Dashboard
- **Net Sales MTD** (Month-to-Date del mes más reciente)
- **Net Sales YTD** (Year-to-Date total)
- **Gross Margin** ($ y %)
- **Órdenes** totales
- **AOV** (Average Order Value)
- **Unidades** vendidas
- **Returns** (% y $)
- **Tendencia mensual** con variación vs mes anterior

### ✅ Página 2: Drivers Dashboard
- **Net Sales por Ciudad** (gráfico de barras horizontal)
- **Net Sales por Canal** (gráfico de barras)
- **Top 10 Productos por Margen Bruto** (con % de margen)
- **Mix de Categorías** (pie chart con % participación)
- **Clientes Nuevos vs Recurrentes** por mes (stacked bar)

### ✅ Interactividad Obligatoria
- **Filtros por Fechas** (fecha inicio y fin)
- **Filtro por Ciudad** (todas las ciudades disponibles)
- **Filtro por Canal** (todos los canales)
- Los filtros se aplican a TODAS las visualizaciones

## 📊 Stack Tecnológico

- **Backend:** FastAPI + Python 3.11
- **Base de Datos:** SQL Server (BI_Prueba)
- **Frontend:** HTML5 + CSS3 + JavaScript
- **Visualizaciones:** Plotly.js 2.27.0
- **Conexión DB:** pyodbc + ODBC Driver 17

## 🚀 Cómo Ejecutar

### 1. Activar entorno virtual
```powershell
C:\Users\User\Documents\bi_prueba_dataset\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias (si no están)
```powershell
pip install -r requirements.txt
```

### 3. Iniciar servidor
```powershell
cd C:\Users\User\Documents\bi_prueba_dataset\dashboard_web
uvicorn app_complete:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Abrir en navegador
```
http://127.0.0.1:8000
```

## 📁 Estructura de Archivos

```
dashboard_web/
├── app_complete.py          # Backend FastAPI con 8 endpoints
├── .env                     # Configuración de SQL Server
├── requirements.txt         # Dependencias Python
└── static/
    ├── index.html          # UI del dashboard (2 páginas)
    ├── script.js           # Lógica frontend + filtros
    └── style.css           # Estilos con tema azul claro
```

## 🔌 Endpoints API

### GET /api/filters
Retorna opciones para los filtros (ciudades, canales, categorías, fechas)

### GET /api/kpis
**Query params:** `start_date`, `end_date`, `city`, `channel`  
**Response:** Net Sales MTD/YTD, Gross Margin, Orders, AOV, Units, Return Rate

### GET /api/monthly-trend
**Query params:** `start_date`, `end_date`, `city`, `channel`  
**Response:** Array con gross_sales, discounts, returns, net_sales, pct_change por mes

### GET /api/sales-by-city
**Query params:** `start_date`, `end_date`, `channel`  
**Response:** Net Sales por ciudad

### GET /api/sales-by-channel
**Query params:** `start_date`, `end_date`, `city`  
**Response:** Net Sales por canal

### GET /api/sales-by-category
**Query params:** `start_date`, `end_date`, `city`, `channel`  
**Response:** Net Sales por categoría con % mix

### GET /api/top-products
**Query params:** `start_date`, `end_date`, `city`, `channel`  
**Response:** Top 10 productos por gross margin con %

### GET /api/new-vs-returning
**Query params:** `start_date`, `end_date`, `city`, `channel`  
**Response:** Clientes nuevos vs recurrentes por mes

## 📊 Métricas Calculadas

### Net Sales
```
Net Sales = Gross Sales - Discounts - Returns
```

### Gross Margin
```
Gross Margin = Revenue - COGS (Cost of Goods Sold)
Gross Margin % = (Gross Margin / Net Sales) * 100
```

### AOV (Average Order Value)
```
AOV = Net Sales YTD / Total Orders
```

### Return Rate
```
Return Rate = (Total Returns $ / Gross Sales) * 100
```

### MTD (Month-to-Date)
Suma de ventas netas del mes más reciente con datos

### YTD (Year-to-Date)
Suma total de ventas netas de todos los meses disponibles

### Clientes Nuevos vs Recurrentes
- **Nuevo:** Primera compra (paid) ocurre en ese mes
- **Recurrente:** Ya tenía una compra (paid) en meses anteriores

## 🎨 Diseño Visual

- **Color principal:** Azul claro (#60a5fa → #3b82f6)
- **Gradiente de fondo:** Linear gradient azul
- **KPI Cards:** Glassmorphism con borde superior azul
- **Charts:** Plotly.js con tema personalizado
- **Responsive:** Adaptable a móvil, tablet y desktop

## ✅ Cumplimiento del Examen

| Requerimiento | Estado | Ubicación |
|--------------|--------|-----------|
| Net Sales MTD y YTD | ✅ | Executive Dashboard |
| Gross Margin y % | ✅ | Executive Dashboard |
| Órdenes, AOV, Unidades | ✅ | Executive Dashboard |
| Returns (% y $) | ✅ | Executive Dashboard |
| Tendencia mensual con variación | ✅ | Executive Dashboard |
| Net Sales por city/store | ✅ | Drivers Dashboard (por city) |
| Net Sales por channel | ✅ | Drivers Dashboard |
| Net Sales por category | ✅ | Drivers Dashboard (pie chart) |
| Top productos por margen | ✅ | Drivers Dashboard |
| Clientes nuevos vs recurrentes | ✅ | Drivers Dashboard |
| Visual de "mix" | ✅ | Drivers Dashboard (category mix) |
| Filtro por fechas | ✅ | Filtros globales |
| Filtro por tienda/ciudad | ✅ | Filtros globales |
| Filtro por canal | ✅ | Filtros globales |

## 📝 Datos de Prueba

- **Periodo:** 2025-08-01 a 2026-01-31 (6 meses)
- **Total Orders:** ~17,000 órdenes paid
- **Total Items:** ~63,000 unidades vendidas
- **Net Sales YTD:** ~$4.5M
- **Gross Margin:** ~$1.8M
- **Return Rate:** ~3.5%
- **Ciudades:** 6 ciudades disponibles
- **Canales:** 3 canales (online, store, marketplace)
- **Categorías:** Múltiples categorías de productos

## 🔧 Troubleshooting

### Error: "Could not import module 'app_complete'"
**Solución:** Asegurarse de estar en el directorio `dashboard_web`
```powershell
cd C:\Users\User\Documents\bi_prueba_dataset\dashboard_web
```

### Error: "Directory 'static' does not exist"
**Solución:** Verificar que existe la carpeta `static/` con index.html, script.js, style.css

### Error de conexión a SQL Server
**Solución:** Verificar en `.env` que:
```env
SQL_SERVER=DESKTOP-CCBH45L
SQL_DATABASE=BI_Prueba
SQL_DRIVER=ODBC Driver 17 for SQL Server
```

### Dashboard muestra $0 en todos los KPIs
**Solución:** 
1. Verificar que hay datos en SQL Server: `SELECT COUNT(*) FROM orders WHERE status='paid'`
2. Abrir consola del navegador (F12) y verificar errores
3. Revisar logs de uvicorn para errores SQL

### Filtros no funcionan
**Solución:** Hacer clic en "Aplicar Filtros" después de seleccionar opciones

## 📄 Licencia

Dashboard creado para examen BI - © 2026
