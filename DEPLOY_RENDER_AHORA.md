# 🚀 Deploy Web Service a Render - AHORA

## ✅ Ya Completado
- ✅ PostgreSQL creado en Render
- ✅ Credenciales obtenidas
- ✅ Backend compatible con PostgreSQL
- ✅ Código en GitHub actualizado

---

## 📍 PASO ACTUAL: Crear Web Service

### 1. Abrir Render Dashboard
Ve a: https://dashboard.render.com/

### 2. Crear Nuevo Web Service
1. Click **"New +"** (botón azul arriba a la derecha)
2. Selecciona **"Web Service"**

### 3. Conectar Repositorio
1. Si no aparece tu repo, click **"Configure account"**
2. Autoriza acceso a GitHub
3. Busca: **kayab23/bi-dashboard-examen**
4. Click **"Connect"**

### 4. Configuración del Web Service

Llena estos campos:

```
Name: bi-dashboard-examen

Region: Oregon (US West)

Branch: main

Root Directory: dashboard_web

Runtime: Python 3

Build Command:
pip install -r requirements_render.txt

Start Command:
uvicorn app:app --host 0.0.0.0 --port $PORT

Instance Type: Free
```

### 5. Variables de Entorno (Environment)

Click en **"Advanced"** → **"Add Environment Variable"**

Agrega estas 2 variables:

```
DATABASE_URL = postgresql://bi_prueba_user:85BgxjeqGd6TGB1ogDR7UUGwcuskFyqk@dpg-d63pn0er433s73dtmhkg-a/bi_prueba

DB_TYPE = postgresql
```

**⚠️ IMPORTANTE:** Usa el **Internal Database URL** (el corto sin .oregon-postgres.render.com)

### 6. Crear y Deploy

1. Revisa que todo esté correcto
2. Click **"Create Web Service"** (botón azul abajo)
3. **Espera 5-10 minutos** mientras hace el build

---

## 📊 Observar el Build

Verás logs en tiempo real como:

```
==> Cloning from https://github.com/kayab23/bi-dashboard-examen...
==> Checking out commit 36bddac...
==> Running build command 'pip install -r requirements_render.txt'...
    Collecting fastapi==0.104.1
    Collecting uvicorn==0.24.0
    Collecting psycopg2-binary==2.9.9
    ...
==> Build successful 🎉
==> Starting service...
    INFO: Uvicorn running on http://0.0.0.0:10000
    INFO: Application startup complete
==> Live ✅
```

---

## ✅ Cuando Termine el Build

Obtendrás una URL como:
```
https://bi-dashboard-examen-XXXX.onrender.com
```

### Probar el Servicio

1. **API Root:**
   ```
   https://bi-dashboard-examen-XXXX.onrender.com/
   ```

2. **API Docs:**
   ```
   https://bi-dashboard-examen-XXXX.onrender.com/docs
   ```

3. **Dashboard (sin datos aún):**
   ```
   https://bi-dashboard-examen-XXXX.onrender.com/static/index.html
   ```

**NOTA:** El dashboard cargará pero mostrará errores porque PostgreSQL está vacío. Eso es normal.

---

## ⏭️ Siguiente Paso

Después de que el servicio esté **Live**, cargaremos los datos de 2 formas:

### Opción A: Desde Shell de Render (Más fácil)
1. En Render Dashboard → tu database
2. Click **"Connect"** → **"Shell"**
3. Ejecutar comandos SQL directamente

### Opción B: Cargar solo tablas pequeñas
Solo cargar customers, stores, products manualmente
Generar orders y order_items sintéticos desde el dashboard

---

## 🎯 Objetivo

```
✅ Web Service desplegado y funcionando
✅ URL pública accesible
⏳ PostgreSQL vacío (cargar después)
⏭️ Dashboard renderiza la UI (sin datos aún)
```

---

**⏰ TIEMPO ESTIMADO:** 10-15 minutos

**🔗 LINK:** https://dashboard.render.com/
