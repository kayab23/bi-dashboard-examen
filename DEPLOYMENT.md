# Dashboard BI - Deployment Guide

## 📦 Archivos del Proyecto

### Backend Completo
- ✅ `app_complete.py` - FastAPI con 8 endpoints (598 líneas)
- ✅ `requirements.txt` - Dependencias Python
- ✅ `.env` - Configuración (SQL Server local, PostgreSQL para Render)
- ✅ `Procfile` - Configuración de Render
- ✅ `runtime.txt` - Python 3.11.9

### Frontend Completo
- ✅ `static/index.html` - UI con 2 páginas (150 líneas)
- ✅ `static/script.js` - JavaScript con filtros (358 líneas)
- ✅ `static/style.css` - Estilos profesionales (500+ líneas)

### Documentación
- ✅ `README_DASHBOARD.md` - Documentación completa

## 🚀 Deployment a Render

### Opción 1: Solo Frontend (GitHub Pages) - RECOMENDADO para examen
Ya que el evaluador necesita ver el dashboard funcionando rápidamente:

1. **Usar GitHub Pages con datos mockeados** para demostración rápida
2. **Incluir screenshots del dashboard con datos reales** en el README
3. **Entregar el código completo** en el repositorio

### Opción 2: Full Stack en Render (Requiere PostgreSQL)

#### Paso 1: Exportar datos de SQL Server
```powershell
# Desde SQL Server Management Studio o PowerShell
bcp BI_Prueba.dbo.customers out customers.csv -c -t, -S DESKTOP-CCBH45L -T
bcp BI_Prueba.dbo.stores out stores.csv -c -t, -S DESKTOP-CCBH45L -T
bcp BI_Prueba.dbo.products out products.csv -c -t, -S DESKTOP-CCBH45L -T
bcp BI_Prueba.dbo.orders out orders.csv -c -t, -S DESKTOP-CCBH45L -T
bcp BI_Prueba.dbo.order_items out order_items.csv -c -t, -S DESKTOP-CCBH45L -T
bcp BI_Prueba.dbo.returns out returns.csv -c -t, -S DESKTOP-CCBH45L -T
```

#### Paso 2: Crear PostgreSQL en Render
1. Login a [render.com](https://render.com)
2. New → PostgreSQL (Free tier)
3. Copiar External Database URL

#### Paso 3: Cargar datos a PostgreSQL
```bash
psql $DATABASE_URL < schema_postgres.sql
psql $DATABASE_URL -c "\copy customers FROM 'customers.csv' CSV HEADER"
# Repetir para todas las tablas
```

#### Paso 4: Desplegar Web Service
1. New → Web Service
2. Conectar repo: kayab23/bi-dashboard-examen
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app_complete:app --host 0.0.0.0 --port $PORT`
5. Agregar variable de entorno: `DATABASE_URL` = [Internal Database URL]

## 📊 Power BI Dashboard (Siguiente Paso)

### Pasos para crear Power BI:
1. Abrir Power BI Desktop
2. Get Data → SQL Server
3. Server: DESKTOP-CCBH45L, Database: BI_Prueba
4. Import Mode (no DirectQuery)
5. Crear relaciones en Model View
6. Crear medidas DAX:
   - Net Sales = SUM(order_items[qty] * order_items[unit_price]) - SUM(orders[discount_amount]) - SUM(returns[amount_returned])
   - Gross Margin = [Net Sales] - SUM(order_items[qty] * order_items[unit_cost])
   - AOV = DIVIDE([Net Sales], DISTINCTCOUNT(orders[order_id]))
   - Return Rate = DIVIDE(SUM(returns[amount_returned]), SUM(order_items[qty] * order_items[unit_price]))

### Visualizaciones Power BI:
**Página 1: Executive**
- 6 KPI Cards
- Line Chart (tendencia mensual)
- Slicers (fecha, ciudad, canal)

**Página 2: Drivers**
- Map (ventas por ciudad)
- Bar Chart (top productos)
- Stacked Column (nuevos vs recurrentes)
- Pie Chart (mix de categorías)

### Exportar:
- File → Export → Export to PDF
- Guardar como: `respuestas_examen_bi/bi_dashboard_examen.pdf`

## ✅ Checklist Final del Examen

### Parte A (SQL y Fundamentos)
- [x] answers.sql - 5 queries completos
- [x] answers_ejecutable.sql - Versión SSMS
- [x] respuestas_seccion2.md - Preguntas de negocio
- [x] star_schema_design.sql - Modelo dimensional
- [x] insights.md - KPIs y recomendaciones

### Parte B (Dashboard)
- [x] Dashboard web funcional (localhost:8000)
- [x] Código en GitHub (commit 7c8e238)
- [ ] Power BI Desktop (.pbix)
- [ ] Power BI PDF export
- [ ] (Opcional) Deployment a Render

## 🎯 Recomendación

**Para entregar el examen AHORA:**

1. ✅ Código completo en GitHub ← YA HECHO
2. ✅ Dashboard funcionando localmente ← YA HECHO
3. ⏭️ Crear Power BI con los mismos datos
4. ⏭️ Exportar Power BI a PDF
5. ⏭️ Crear documento final de entrega

**El deployment a Render es OPCIONAL** - Lo importante es que:
- El código está completo y documentado
- El dashboard funciona con datos reales
- Tienes screenshots/evidencia de funcionamiento
- Cumples TODOS los requerimientos del examen
