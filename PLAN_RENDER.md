# 🚀 Plan de Deployment a Render

## 📋 Objetivo
Desplegar el dashboard BI a Render con base de datos PostgreSQL para que evaluadores accedan vía URL pública.

---

## 🎯 FASE 1: Exportar Datos de SQL Server

### Paso 1.1: Crear Script de Exportación
```powershell
# export_to_csv.ps1
# Exportar las 6 tablas a archivos CSV
```

### Paso 1.2: Ejecutar Exportación
```powershell
.\export_to_csv.ps1
```

### Archivos Generados:
- `data/customers.csv` (7 registros)
- `data/stores.csv` (7 registros)
- `data/products.csv` (~30 registros)
- `data/orders.csv` (~17,000 registros)
- `data/order_items.csv` (~40,000 registros)
- `data/returns.csv` (~600 registros)

**Estimado:** 10 minutos

---

## 🎯 FASE 2: Crear Backend PostgreSQL

### Paso 2.1: Crear app_postgres.py
Backend compatible con PostgreSQL usando `psycopg2` o `asyncpg`.

### Paso 2.2: Actualizar requirements.txt
```txt
fastapi==0.104.1
uvicorn==0.24.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

### Paso 2.3: Configurar Detección Automática
Modificar app.py para detectar SQL Server (local) vs PostgreSQL (Render).

**Estimado:** 15 minutos

---

## 🎯 FASE 3: Crear PostgreSQL en Render

### Paso 3.1: Login a Render
1. Ir a https://dashboard.render.com
2. Login con GitHub

### Paso 3.2: Crear PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Configuración:
   - **Name:** `bi-prueba-db`
   - **Database:** `bi_prueba`
   - **User:** (auto-generado)
   - **Region:** Oregon (US West)
   - **Plan:** Free (100 MB)
3. Click "Create Database"

### Paso 3.3: Copiar Credenciales
```
Internal Database URL: postgresql://user:pass@host:5432/bi_prueba
External Database URL: postgresql://user:pass@host:5432/bi_prueba
PSQL Command: psql -h host -U user bi_prueba
```

**Estimado:** 5 minutos

---

## 🎯 FASE 4: Cargar Datos a PostgreSQL

### Paso 4.1: Conectar a PostgreSQL Render
```bash
psql [External Database URL]
```

### Paso 4.2: Crear Esquema
```sql
-- Ejecutar schema_postgres.sql
\i schema_postgres.sql
```

### Paso 4.3: Cargar CSVs
Opción A: Desde local usando psql
```bash
psql [External Database URL] -c "\COPY customers FROM 'data/customers.csv' CSV HEADER"
psql [External Database URL] -c "\COPY stores FROM 'data/stores.csv' CSV HEADER"
# ... para todas las tablas
```

Opción B: Subir CSVs a GitHub y cargar desde Render Shell

### Paso 4.4: Validar Datos
```sql
SELECT COUNT(*) FROM orders;  -- Debe ser ~17,000
SELECT COUNT(*) FROM order_items;  -- Debe ser ~40,000
SELECT SUM(qty * unit_price) FROM order_items;  -- Verificar totales
```

**Estimado:** 20 minutos

---

## 🎯 FASE 5: Deploy Web Service a Render

### Paso 5.1: Crear Web Service
1. Click "New +" → "Web Service"
2. Conectar repositorio GitHub: `kayab23/bi-dashboard-examen`

### Paso 5.2: Configuración del Web Service
```
Name: bi-dashboard-examen
Region: Oregon (US West)
Branch: main
Root Directory: dashboard_web
Runtime: Python 3

Build Command: pip install -r requirements.txt
Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT

Plan: Free
```

### Paso 5.3: Variables de Entorno
```
DATABASE_URL = [Internal Database URL from PostgreSQL]
DB_TYPE = postgresql
PYTHON_VERSION = 3.11.9
```

### Paso 5.4: Deploy
1. Click "Create Web Service"
2. Esperar build (~5 minutos)
3. Ver logs en tiempo real

**Estimado:** 30 minutos (incluyendo build)

---

## 🎯 FASE 6: Validar Dashboard en Producción

### Paso 6.1: Obtener URL Pública
```
https://bi-dashboard-examen-XXXX.onrender.com
```

### Paso 6.2: Probar Endpoints
```bash
# Health check
curl https://bi-dashboard-examen-XXXX.onrender.com/

# API Filters
curl https://bi-dashboard-examen-XXXX.onrender.com/api/filters

# KPIs
curl https://bi-dashboard-examen-XXXX.onrender.com/api/kpis
```

### Paso 6.3: Validar Dashboard Completo
1. Abrir: `https://bi-dashboard-examen-XXXX.onrender.com/static/index.html`
2. Verificar que carguen los KPIs
3. Probar filtros (fecha, ciudad, canal)
4. Verificar gráficos (Executive + Drivers pages)

### Paso 6.4: Casos de Prueba
✅ Dashboard carga sin errores
✅ KPIs muestran valores correctos (Net Sales YTD ~$4.5M)
✅ Gráfico de tendencia mensual funciona
✅ Filtro por ciudad funciona
✅ Filtro por canal funciona
✅ Filtro por fechas funciona
✅ Página Drivers muestra 5 visualizaciones
✅ Responsive design funciona en móvil

**Estimado:** 15 minutos

---

## 📊 Timeline Total

| Fase | Duración | Acumulado |
|------|----------|-----------|
| 1. Exportar datos | 10 min | 10 min |
| 2. Backend PostgreSQL | 15 min | 25 min |
| 3. Crear DB Render | 5 min | 30 min |
| 4. Cargar datos | 20 min | 50 min |
| 5. Deploy service | 30 min | 80 min |
| 6. Validación | 15 min | 95 min |

**Total: ~1.5 horas**

---

## ⚠️ Consideraciones Importantes

### Limitaciones Free Tier Render
- ✅ PostgreSQL: 100 MB (suficiente para ~60K registros)
- ✅ Web Service: 750 horas/mes (suficiente)
- ⚠️ Sleep después de 15 min inactividad (primer request tarda 30-60s)
- ⚠️ Build time: ~5-10 minutos

### Alternativas si Free Tier no es Suficiente
1. **Railway.app**: Similar a Render, 500 horas gratis
2. **Fly.io**: 3 apps gratis, PostgreSQL incluido
3. **Heroku**: $5/mes (no tiene free tier ahora)

### Rollback Plan
Si algo falla en Render:
1. Mantener dashboard local funcionando (ya validado)
2. Crear video demo del dashboard funcionando
3. Incluir screenshots en README
4. Entregar código completo en GitHub

---

## ✅ Checklist Pre-Deployment

### Archivos Necesarios
- [x] app.py con rutas absolutas
- [x] requirements.txt actualizado
- [x] Procfile configurado
- [x] runtime.txt con Python 3.11.9
- [x] .env.example con variables documentadas
- [x] schema_postgres.sql para crear tablas
- [ ] app_postgres.py o detección automática DB
- [ ] CSVs exportados en data/

### Configuración Local Validada
- [x] Dashboard funcionando en localhost:8000
- [x] API endpoints respondiendo 200 OK
- [x] Filtros interactivos funcionando
- [x] Datos reales de SQL Server
- [x] Código en GitHub actualizado

### Cuenta Render
- [ ] Cuenta creada en render.com
- [ ] GitHub conectado
- [ ] Repositorio autorizado

---

## 🚀 Comando Rápido de Inicio

```powershell
# Desde dashboard_web/
cd C:\Users\User\Documents\bi_prueba_dataset\dashboard_web

# 1. Exportar datos
.\export_to_csv.ps1

# 2. Verificar CSVs
Get-ChildItem data\*.csv | ForEach-Object { 
    Write-Host "$($_.Name): $((Get-Content $_ | Measure-Object -Line).Lines) lines"
}

# 3. Commit y push a GitHub
git add data/*.csv
git commit -m "Add exported CSV data for PostgreSQL"
git push origin main

# 4. Ir a render.com y seguir pasos de FASE 3-5
```

---

## 📝 Próximos Pasos

1. ⏭️ **AHORA:** Crear script de exportación CSV
2. ⏭️ Crear/modificar backend para PostgreSQL
3. ⏭️ Ir a Render y crear PostgreSQL
4. ⏭️ Cargar datos a PostgreSQL
5. ⏭️ Deploy web service
6. ⏭️ Validar y compartir URL pública
7. ⏭️ Continuar con Power BI Desktop

---

## 🎯 Resultado Final Esperado

```
✅ URL Pública: https://bi-dashboard-examen-XXXX.onrender.com/static/index.html
✅ Dashboard funcionando con datos reales
✅ Accesible para evaluadores 24/7
✅ Mismo diseño y funcionalidad que local
✅ Listo para entregar en examen
```
