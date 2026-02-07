# Dashboard BI - Deployment Guide

## 🚀 Despliegue en Render

### Paso 1: Crear Base de Datos PostgreSQL en Render

1. Ir a https://render.com (crear cuenta gratis)
2. Click en "New" → "PostgreSQL"
3. Configuración:
   - Name: `bi-dashboard-db`
   - Database: `bi_prueba`
   - User: (auto-generado)
   - Region: Oregon (US West)
   - Plan: Free
4. Click "Create Database"
5. **Copiar la "Internal Database URL"** (formato: `postgresql://user:password@host/database`)

### Paso 2: Cargar Datos a PostgreSQL

```bash
# Desde tu computadora local
psql "postgresql://user:password@host/database" < schema_postgres.sql

# Cargar cada CSV
\copy customers FROM 'c:/temp/customers.csv' DELIMITER ',' CSV HEADER;
\copy stores FROM 'c:/temp/stores.csv' DELIMITER ',' CSV HEADER;
\copy products FROM 'c:/temp/products.csv' DELIMITER ',' CSV HEADER;
\copy orders FROM 'c:/temp/orders.csv' DELIMITER ',' CSV HEADER;
\copy order_items FROM 'c:/temp/order_items.csv' DELIMITER ',' CSV HEADER;
\copy returns FROM 'c:/temp/returns.csv' DELIMITER ',' CSV HEADER;
```

### Paso 3: Crear Repositorio GitHub

```bash
cd dashboard_web
git init
git add .
git commit -m "Initial commit - BI Dashboard"
git remote add origin https://github.com/TU_USUARIO/bi-dashboard.git
git push -u origin main
```

### Paso 4: Deploy Web Service en Render

1. En Render, click "New" → "Web Service"
2. Conectar tu repositorio GitHub
3. Configuración:
   - Name: `bi-dashboard`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Variables de entorno:
   - `DATABASE_URL`: (pegar la Internal Database URL de PostgreSQL)
5. Click "Create Web Service"

### Paso 5: Acceder al Dashboard

URL: `https://bi-dashboard-XXXX.onrender.com`

---

## 🖥️ Desarrollo Local

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env con tu DATABASE_URL local

# Ejecutar
python app.py

# Abrir navegador
http://localhost:8000
```

---

## 📦 Estructura del Proyecto

```
dashboard_web/
├── app.py                 # FastAPI backend
├── requirements.txt       # Dependencias Python
├── schema_postgres.sql    # Schema PostgreSQL
├── .env.example          # Variables de entorno template
├── static/
│   ├── index.html        # Frontend HTML
│   ├── style.css         # Estilos CSS
│   └── script.js         # JavaScript (Plotly)
└── README.md             # Esta guía
```

---

## ✅ Checklist Pre-Deploy

- [ ] Exportar datos SQL Server a CSV
- [ ] Crear base de datos PostgreSQL en Render
- [ ] Cargar schema y datos
- [ ] Crear repositorio GitHub
- [ ] Push del código
- [ ] Crear Web Service en Render
- [ ] Configurar DATABASE_URL
- [ ] Verificar que el dashboard carga correctamente
