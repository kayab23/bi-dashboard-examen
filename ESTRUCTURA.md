# 📁 Estructura del Proyecto Dashboard BI

## Estructura Limpia y Organizada

```
dashboard_web/                   ← Directorio principal del dashboard
├── app.py                       ← 🟢 Backend principal (FastAPI + SQL Server)
├── app_complete.py              ← 🔵 Versión completa (mismo que app.py)
├── requirements.txt             ← Dependencias Python
├── .env                         ← Variables de entorno (SQL Server local)
├── .env.example                 ← Ejemplo de configuración
├── Procfile                     ← Configuración para Render (usa app.py)
├── runtime.txt                  ← Python 3.11.9
│
├── static/                      ← 🟢 Frontend activo
│   ├── index.html               ← HTML principal (2 páginas)
│   ├── script.js                ← JavaScript con filtros
│   └── style.css                ← Estilos profesionales (tema azul)
│
├── backups/                     ← 🟡 Archivos de respaldo
│   ├── app_old.py               ← Versión antigua PostgreSQL
│   ├── index_complete.html      ← Backups
│   ├── script_complete.js
│   └── style_complete.css
│
└── docs/                        ← 📚 Documentación
    ├── README.md                ← README principal
    ├── README_DASHBOARD.md      ← Documentación técnica completa
    ├── DEPLOYMENT.md            ← Guía de deployment
    └── GUIA_COMPLETA.md         ← Guía completa del proyecto
```

## 🎯 Archivos Activos (Usar estos)

### Backend
- **app.py** - FastAPI backend con SQL Server
  - Conexión: DESKTOP-CCBH45L\BI_Prueba
  - 8 endpoints API funcionales
  - Puerto: 8000

### Frontend
- **static/index.html** - Interfaz de usuario
- **static/script.js** - Lógica frontend con filtros
- **static/style.css** - Estilos profesionales

### Configuración
- **.env** - Variables de entorno (SQL Server)
- **requirements.txt** - Dependencias
- **Procfile** - Config Render

## 🚀 Comandos para Ejecutar

### Opción 1: Desde dashboard_web/ (RECOMENDADO)
```powershell
cd C:\Users\User\Documents\bi_prueba_dataset\dashboard_web
C:/Users/User/Documents/bi_prueba_dataset/.venv/Scripts/python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### Opción 2: Desde raíz del proyecto
```powershell
cd C:\Users\User\Documents\bi_prueba_dataset
.venv/Scripts/python.exe -m uvicorn dashboard_web.app:app --host 127.0.0.1 --port 8000 --reload
```

### Acceso
- Dashboard: http://127.0.0.1:8000
- Archivos estáticos: http://127.0.0.1:8000/static/index.html
- API Docs: http://127.0.0.1:8000/docs

## ✅ Validación de Rutas

### Backend (app.py)
✅ `app.mount("/static", StaticFiles(directory="static"), name="static")`
- Lee archivos desde: `dashboard_web/static/`
- URLs: `/static/index.html`, `/static/script.js`, `/static/style.css`

### Frontend (script.js)
✅ Todas las llamadas API usan rutas relativas:
- `fetch('/api/filters')`
- `fetch('/api/kpis' + queryParams)`
- `fetch('/api/monthly-trend' + queryParams)`
- etc.

### Variables de Entorno (.env)
✅ SQL Server:
- Server: DESKTOP-CCBH45L
- Database: BI_Prueba
- Driver: ODBC Driver 17 for SQL Server
- Autenticación: Trusted_Connection=yes

## 🧹 Archivos Limpiados

### Movidos a backups/
- ❌ app_old.py (PostgreSQL, obsoleto)
- ❌ *_complete.* (versiones de desarrollo)

### Eliminados archivos duplicados
- Solo quedan versiones activas en static/
- Backups preservados en backups/

## 🔍 Troubleshooting

### Error: ModuleNotFoundError
**Solución:** Ejecutar desde dashboard_web/ directamente
```powershell
cd dashboard_web
python -m uvicorn app:app --reload
```

### Error: Static files not found
**Solución:** Verificar que estás en dashboard_web/ al ejecutar
```powershell
Test-Path static/index.html  # Debe retornar True
```

### Error: Database connection failed
**Solución:** Verificar SQL Server está corriendo
```powershell
Get-Service MSSQLSERVER  # Debe estar "Running"
```

## 📊 Entornos del Proyecto

### 1. Entorno Local (ACTUAL)
- **Backend:** app.py + SQL Server local
- **Base de datos:** DESKTOP-CCBH45L\BI_Prueba
- **Puerto:** 8000
- **Status:** ✅ Funcionando

### 2. Entorno Render (PENDIENTE)
- **Backend:** app.py (mismo código)
- **Base de datos:** PostgreSQL en Render
- **Puerto:** $PORT (asignado por Render)
- **Status:** ⏳ Por configurar

## 🎯 Próximos Pasos

1. ✅ Estructura limpia y organizada
2. ⏭️ Probar servidor con rutas corregidas
3. ⏭️ Validar dashboard frontend
4. ⏭️ Continuar con Power BI
