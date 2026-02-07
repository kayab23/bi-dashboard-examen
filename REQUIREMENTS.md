# 📦 Requirements Configuration

## Para Desarrollo Local (SQL Server)
Usa `requirements.txt` que incluye pyodbc:
```bash
pip install -r requirements.txt
```

## Para Deployment en Render (PostgreSQL)
Usa `requirements_render.txt` que solo incluye psycopg2:
```bash
pip install -r requirements_render.txt
```

## Actualizar Build Command en Render
En la configuración del Web Service, usa:
```bash
pip install -r requirements_render.txt
```

O mantén `requirements.txt` pero asegúrate de que pyodbc sea opcional.
