# 🔄 Mantener Render Activo 24/7

## Problema

El plan gratuito de Render pone los servicios a **dormir después de 15 minutos de inactividad**. Esto causa:
- Primera carga lenta (30-60 segundos)
- Mala experiencia de usuario
- Dashboard no disponible instantáneamente

## Solución: UptimeRobot (Gratuito)

### Paso 1: Crear Cuenta en UptimeRobot

1. Ve a https://uptimerobot.com
2. Click en **"Free Sign Up"**
3. Registra con tu email
4. Confirma tu cuenta por email

### Paso 2: Crear Monitor

1. En el dashboard, click **"+ Add New Monitor"**
2. Configura:
   ```
   Monitor Type: HTTP(s)
   Friendly Name: BI Dashboard Render
   URL: https://bi-dashboard-examen.onrender.com/health
   Monitoring Interval: 5 minutes (máximo gratuito)
   ```
3. Click **"Create Monitor"**

### Paso 3: Verificar

- UptimeRobot hará ping cada 5 minutos
- Render nunca dormirá
- Dashboard siempre estará activo

---

## Alternativa: Cron-Job.org

Si prefieres otra opción gratuita:

1. Ve a https://cron-job.org
2. Registra cuenta gratuita
3. Crear cron job:
   ```
   URL: https://bi-dashboard-examen.onrender.com/health
   Interval: Every 5 minutes
   ```

---

## Endpoint de Health Check

Ya existe en el backend (`app.py`):

```python
@app.get("/health")
async def health_check():
    """Health check endpoint para keep-alive"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }
```

Pruébalo: https://bi-dashboard-examen.onrender.com/health

---

## ⚠️ Limitaciones del Plan Gratuito

- **750 horas/mes**: Suficiente para ~24/7 con monitor cada 5min
- Si excedes, el servicio se suspende hasta el siguiente mes
- Para producción real, considera plan de pago ($7/mes)

---

## ✅ Validación

Una vez configurado UptimeRobot:

1. Ve al dashboard de UptimeRobot
2. Verifica que el status sea **"Up"** (verde)
3. Espera 20 minutos sin acceder al dashboard
4. Abre https://bi-dashboard-examen.onrender.com/static/index.html
5. Debe cargar **instantáneamente** (no 30-60s)

---

## 📊 Monitoreo

UptimeRobot te enviará:
- **Email alerts** si el servicio cae
- **Uptime reports** (disponibilidad mensual)
- **Response time graphs** (latencia)

¡Dashboard siempre disponible para evaluadores! ✅
