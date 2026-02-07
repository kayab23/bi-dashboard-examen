# 🚀 Instrucciones para Deployment en Render

## PASO 1: Crear Cuenta en Render (si no tienes)
1. Ve a https://render.com
2. Haz clic en "Get Started"
3. Registrate con GitHub (recomendado)
4. Autoriza acceso a tu repositorio `kayab23/bi-dashboard-examen`

---

## PASO 2: Crear Base de Datos PostgreSQL

### 2.1 Crear PostgreSQL Instance
1. En dashboard de Render, haz clic en **"New +"**
2. Selecciona **"PostgreSQL"**
3. Configuración:
   ```
   Name: bi-prueba-db
   Database: bi_prueba
   User: (auto-generado)
   Region: Oregon (US West)
   PostgreSQL Version: 16
   Plan: Free
   ```
4. Haz clic en **"Create Database"**
5. Espera ~2 minutos a que se cree

### 2.2 Copiar Credenciales
Una vez creada, copia estas URLs (las necesitarás):

```bash
# Internal Database URL (para el web service)
postgresql://user:password@hostname/bi_prueba

# External Database URL (para conectar desde tu máquina)
postgresql://user:password@external-hostname/bi_prueba
```

**⚠️ IMPORTANTE:** Guarda estas URLs en un lugar seguro.

---

## PASO 3: Cargar Datos a PostgreSQL

### Opción A: Desde tu Máquina Local (Recomendado)

#### 3.1 Instalar psql (si no lo tienes)
```powershell
# Windows: Descargar PostgreSQL desde
https://www.postgresql.org/download/windows/
# O usar Chocolatey
choco install postgresql
```

#### 3.2 Conectar a Render PostgreSQL
```bash
psql [pegar External Database URL aquí]
```

#### 3.3 Crear Schema
```sql
\i schema_postgres.sql
```

#### 3.4 Cargar CSVs
Primero, navega al directorio donde están los CSVs:
```powershell
cd C:\Users\User\Documents\bi_prueba_dataset\dashboard_web\data
```

Luego, desde psql conectado a Render:
```sql
\COPY customers FROM 'customers.csv' WITH CSV HEADER DELIMITER ',';
\COPY stores FROM 'stores.csv' WITH CSV HEADER DELIMITER ',';
\COPY products FROM 'products.csv' WITH CSV HEADER DELIMITER ',';
\COPY orders FROM 'orders.csv' WITH CSV HEADER DELIMITER ',';
\COPY order_items FROM 'order_items.csv' WITH CSV HEADER DELIMITER ',';
\COPY returns FROM 'returns.csv' WITH CSV HEADER DELIMITER ',';
```

#### 3.5 Verificar Carga
```sql
SELECT COUNT(*) FROM orders;
-- Debe retornar ~18,000

SELECT COUNT(*) FROM order_items;
-- Debe retornar ~40,000

SELECT SUM(qty * unit_price) FROM order_items;
-- Debe retornar ~$5M
```

### Opción B: Usando Render Shell (Alternativa)

Si la Opción A no funciona, puedes subir los CSVs a GitHub y cargarlos desde Render:

1. **Commit CSVs a GitHub:**
```powershell
cd C:\Users\User\Documents\bi_prueba_dataset\dashboard_web
git add data/*.csv
git commit -m "Add CSV data for PostgreSQL"
git push origin main
```

2. **Desde Render Dashboard:**
   - Ve a tu PostgreSQL database
   - Click en "Connect" → "External Connection"
   - Usa un cliente PostgreSQL GUI como DBeaver o pgAdmin
   - Importa los CSVs manualmente

---

## PASO 4: Crear Web Service

### 4.1 Nuevo Web Service
1. En dashboard de Render, haz clic en **"New +"**
2. Selecciona **"Web Service"**
3. Conecta tu repositorio: **kayab23/bi-dashboard-examen**
4. Click en **"Connect"**

### 4.2 Configuración del Service
```
Name: bi-dashboard-examen
Region: Oregon (US West)
Branch: main
Root Directory: dashboard_web
Runtime: Python 3

Build Command:
pip install -r requirements.txt

Start Command:
uvicorn app:app --host 0.0.0.0 --port $PORT
```

### 4.3 Variables de Entorno
Click en "Advanced" → "Add Environment Variable"

Agrega estas variables:

```bash
DATABASE_URL = [Internal Database URL copiada en Paso 2.2]
DB_TYPE = postgresql
PYTHON_VERSION = 3.11.9
```

**⚠️ IMPORTANTE:** Usa el **Internal Database URL**, NO el External.

### 4.4 Plan
```
Instance Type: Free
```

### 4.5 Deploy
1. Click en **"Create Web Service"**
2. Espera ~5-10 minutos mientras hace el build
3. Observa los logs en tiempo real

---

## PASO 5: Validar Deployment

### 5.1 Obtener URL
Una vez completado el deploy, verás tu URL:
```
https://bi-dashboard-examen-XXXX.onrender.com
```

### 5.2 Probar Endpoints

#### Health Check
```bash
curl https://bi-dashboard-examen-XXXX.onrender.com/
```

#### API Docs (Swagger)
Abre en navegador:
```
https://bi-dashboard-examen-XXXX.onrender.com/docs
```

#### Filtros
```bash
curl https://bi-dashboard-examen-XXXX.onrender.com/api/filters
```

#### KPIs
```bash
curl https://bi-dashboard-examen-XXXX.onrender.com/api/kpis
```

### 5.3 Abrir Dashboard
En tu navegador, ve a:
```
https://bi-dashboard-examen-XXXX.onrender.com/static/index.html
```

### 5.4 Checklist de Validación
- [ ] Dashboard carga sin errores (200 OK)
- [ ] KPIs muestran valores correctos
- [ ] Net Sales YTD ~$4.5M
- [ ] Total Orders ~17,000
- [ ] Gráfico de tendencia mensual carga
- [ ] Filtro por ciudad funciona
- [ ] Filtro por canal funciona
- [ ] Filtro por fechas funciona
- [ ] Página Drivers carga con 5 gráficos
- [ ] Todos los gráficos muestran datos
- [ ] Responsive design funciona en móvil

---

## PASO 6: Troubleshooting

### Error: Build Failed
**Síntoma:** El build falla con error de dependencias

**Solución:**
```bash
# Verifica que requirements.txt esté correcto
cat requirements.txt

# Asegúrate de que pyodbc NO esté en requirements.txt para Render
# PostgreSQL solo necesita psycopg2-binary
```

### Error: Connection Timeout
**Síntoma:** API retorna 500, logs muestran timeout de conexión

**Solución:**
1. Verifica que `DATABASE_URL` tenga el **Internal URL**
2. Verifica que el PostgreSQL database esté "Available"
3. Restart el web service

### Error: Table Does Not Exist
**Síntoma:** 500 error, logs muestran "relation 'orders' does not exist"

**Solución:**
1. Conecta a PostgreSQL con `psql`
2. Lista tablas: `\dt`
3. Si no hay tablas, ejecuta: `\i schema_postgres.sql`

### Error: Service Sleeping
**Síntoma:** Primera request tarda 30-60 segundos

**Explicación:** Free tier de Render pone el service a dormir después de 15 min de inactividad.

**Solución:** Esto es normal. Espera a que despierte. Requests subsecuentes serán rápidas.

---

## PASO 7: Actualizar Documentación

Una vez funcionando, actualiza el README:

```markdown
## 🌐 Demo en Vivo

Dashboard desplegado en Render:
https://bi-dashboard-examen-XXXX.onrender.com/static/index.html

API Documentation:
https://bi-dashboard-examen-XXXX.onrender.com/docs

⚠️ Nota: Si es la primera request después de inactividad, puede tardar 30-60s en despertar (Free tier).
```

---

## ✅ Checklist Final

- [ ] PostgreSQL creado en Render
- [ ] Schema cargado (6 tablas)
- [ ] Datos cargados (~60K registros)
- [ ] Datos verificados (SELECT COUNT(*))
- [ ] Web Service creado
- [ ] Variables de entorno configuradas
- [ ] Build exitoso
- [ ] Deploy completo
- [ ] URL pública obtenida
- [ ] Dashboard accesible
- [ ] Todos los endpoints funcionando
- [ ] Filtros probados
- [ ] README actualizado con URL
- [ ] Screenshot incluido en repo

---

## 🎯 Resultado Final

```
✅ URL Dashboard: https://bi-dashboard-examen-XXXX.onrender.com/static/index.html
✅ API Docs: https://bi-dashboard-examen-XXXX.onrender.com/docs
✅ Accesible 24/7 para evaluadores
✅ Mismos datos que versión local
✅ Todos los filtros funcionando
✅ Listo para entregar
```

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa logs en Render Dashboard
2. Verifica variables de entorno
3. Confirma que PostgreSQL está "Available"
4. Restart el service desde Render Dashboard
