# 🚀 Guía de Despliegue - The OutWorld Scraper API

## 🎯 Opciones de Despliegue

### **Railway (Recomendado)**
- ✅ Fácil despliegue desde GitHub
- ✅ Variables de entorno automáticas
- ✅ Dominio personalizado gratuito
- ✅ Logs en tiempo real
- ✅ Escalado automático

### **Render**
- ✅ Alternativa confiable
- ✅ SSL automático
- ✅ Integración con GitHub
- ✅ Plan gratuito disponible

## 🔧 Configuración Paso a Paso

### **1. Preparar el Código**

```bash
# Clonar el repositorio
git clone <tu-repo>
cd the-outworld-scraper

# Verificar archivos necesarios
ls -la
# Debe contener:
# - app/
# - requirements.txt
# - Procfile
# - .env (template)
```

### **2. Variables de Entorno**

Configura estas variables en Railway/Render:

```env
# Supabase (OBLIGATORIO)
SUPABASE_URL=https://twxzahdhjnnxvqfxyqvd.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Configuración del servidor
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=info

# Cache configuración
CACHE_TTL=300
CACHE_MAX_SIZE=1000

# Timezone
TZ=America/Denver
```

### **3. Despliegue en Railway**

#### **Opción A: Desde GitHub (Recomendado)**

1. **Conectar Repository:**
   ```bash
   # Subir código a GitHub
   git add .
   git commit -m "Deploy to Railway"
   git push origin main
   ```

2. **Railway Dashboard:**
   - Visita [railway.app](https://railway.app)
   - "New Project" → "Deploy from GitHub repo"
   - Selecciona tu repositorio
   - Railway detectará automáticamente el `Procfile`

3. **Configurar Variables:**
   - En Railway dashboard → "Variables"
   - Añade `SUPABASE_URL` y `SUPABASE_KEY`
   - Otras variables opcionales según necesites

4. **Desplegar:**
   - Railway desplegará automáticamente
   - Obtendrás una URL como: `https://tu-app.railway.app`

#### **Opción B: Railway CLI**

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Inicializar proyecto
railway init

# Configurar variables
railway variables set SUPABASE_URL=https://twxzahdhjnnxvqfxyqvd.supabase.co
railway variables set SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Desplegar
railway up
```

### **4. Despliegue en Render**

1. **Conectar Repository:**
   - Visita [render.com](https://render.com)
   - "New Web Service" → "Connect GitHub"
   - Selecciona tu repositorio

2. **Configurar Build:**
   ```yaml
   # render.yaml (opcional)
   services:
     - type: web
       name: outworld-scraper
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: SUPABASE_URL
           value: https://twxzahdhjnnxvqfxyqvd.supabase.co
         - key: SUPABASE_KEY
           value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

3. **Variables de Entorno:**
   - En Render dashboard → "Environment"
   - Añade todas las variables necesarias

4. **Desplegar:**
   - Render desplegará automáticamente
   - Obtendrás una URL como: `https://tu-app.onrender.com`

## 🗄️ Configuración de Base de Datos

### **Supabase (Ya configurado)**
Tu Supabase ya está configurado con:
- ✅ Tabla `events` creada
- ✅ Conexión establecida
- ✅ 48 eventos de prueba

### **Verificar Conexión**
```bash
# Después del despliegue, probar:
curl https://tu-app.railway.app/health
```

## 🔄 Configuración del Scheduler

### **Horarios Configurados:**
- **Scraping diario:** 6:00 AM (Denver time)
- **Limpieza semanal:** Domingos 2:00 AM (Denver time)

### **Verificar Scheduler:**
```bash
# Verificar estado
curl https://tu-app.railway.app/api/v1/scheduler/status

# Ejecutar manualmente
curl -X POST https://tu-app.railway.app/api/v1/scheduler/run-manual
```

## 🗺️ Endpoints de Mapas

### **Disponibles después del despliegue:**
```bash
# Eventos en mapa
GET /api/v1/maps/events/map?lat=39.7392&lon=-104.9903&radius=10

# Eventos cercanos
GET /api/v1/maps/events/nearby?lat=39.7392&lon=-104.9903&radius=5

# Clusters de ubicaciones
GET /api/v1/maps/locations/clusters?zoom_level=12

# Heatmap
GET /api/v1/maps/locations/heatmap?age_group=kid

# Ubicaciones populares
GET /api/v1/maps/locations/popular?limit=10
```

## 📊 Monitoreo y Logs

### **Health Check:**
```bash
curl https://tu-app.railway.app/health
```

### **Cache Statistics:**
```bash
curl https://tu-app.railway.app/api/v1/cache/stats
```

### **Logs del Scheduler:**
```bash
curl https://tu-app.railway.app/api/v1/logs
```

## 🚨 Troubleshooting

### **Problemas Comunes:**

1. **Error de conexión a Supabase:**
   ```bash
   # Verificar variables de entorno
   railway variables
   
   # Verificar URL de Supabase
   curl -H "apikey: TU_SUPABASE_KEY" https://twxzahdhjnnxvqfxyqvd.supabase.co/rest/v1/events
   ```

2. **Scheduler no funciona:**
   - Verificar timezone: `TZ=America/Denver`
   - Verificar logs: `railway logs`
   - Ejecutar manual: `POST /api/v1/scheduler/run-manual`

3. **Cache no funciona:**
   - Verificar memoria disponible
   - Limpiar cache: `POST /api/v1/cache/clear`

4. **Errores de importación:**
   ```bash
   # Verificar que todas las dependencias estén instaladas
   pip install -r requirements.txt
   ```

## 🔄 Actualización y Mantenimiento

### **Actualizar el código:**
```bash
# Hacer cambios localmente
git add .
git commit -m "Update features"
git push origin main

# Railway/Render desplegará automáticamente
```

### **Rollback si hay problemas:**
```bash
# En Railway
railway rollback

# En Render: usar dashboard para rollback
```

## 🎯 Post-Despliegue

### **Verificar que todo funciona:**
```bash
# 1. Health check
curl https://tu-app.railway.app/health

# 2. Obtener eventos
curl https://tu-app.railway.app/api/v1/events?limit=5

# 3. Probar mapas
curl "https://tu-app.railway.app/api/v1/maps/events/map?lat=39.7392&lon=-104.9903&radius=10"

# 4. Verificar cache
curl https://tu-app.railway.app/api/v1/cache/stats

# 5. Verificar scheduler
curl https://tu-app.railway.app/api/v1/scheduler/status
```

### **URLs de Producción:**
- **API Base:** `https://tu-app.railway.app`
- **Docs:** `https://tu-app.railway.app/docs`
- **Health:** `https://tu-app.railway.app/health`

## 📱 Integración con React Native

### **Configuración del frontend:**
```javascript
// config.js
export const API_BASE_URL = 'https://tu-app.railway.app';

// Ejemplo de uso
const response = await fetch(`${API_BASE_URL}/api/v1/events`);
const events = await response.json();
```

¡Tu API está lista para producción! 🚀 