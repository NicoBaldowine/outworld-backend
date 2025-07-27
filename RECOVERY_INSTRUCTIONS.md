# 🔄 Instrucciones de Recuperación - The OutWorld Scraper

## ✅ Respuesta a tu pregunta:
**SÍ, puedes recuperar todo el proyecto en cualquier otro computador siguiendo estos pasos.**

## 🚀 Cómo Recuperar el Proyecto en Otro Computador

### 1. **📥 Clonar el Repositorio**
```bash
git clone https://github.com/NicoBaldowine/outworld-backend.git
cd outworld-backend
```

### 2. **🐍 Configurar Python (Versión 3.8+)**
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. **🗄️ Configurar Base de Datos Supabase**
Crear archivo `.env` con tus credenciales:
```bash
# .env
SUPABASE_URL=tu-supabase-url
SUPABASE_KEY=tu-supabase-key
CLAUDE_API_KEY=tu-claude-api-key
```

### 4. **🏗️ Configurar Base de Datos**
```bash
python3 setup_db.py
```

### 5. **🚀 Ejecutar el Sistema**
```bash
# Ejecutar servidor FastAPI
python3 main.py

# En otra terminal - Ejecutar scraping manual
python3 run_daily_scraping.py
```

### 6. **🌐 Acceder al Frontend**
Abrir en navegador: `http://localhost:8000`
- API: `http://localhost:8000/docs`
- Frontend de prueba: `eventos-test.html`

## 📦 Lo que se Recupera Automáticamente

### ✅ **Sistema Completo Incluido:**
- ✅ 10+ scrapers configurados (Denver Zoo, Children's Museum, etc.)
- ✅ FastAPI backend con endpoints
- ✅ Sistema de scheduling automático  
- ✅ Manejo correcto de zona horaria (Colorado Mountain Time)
- ✅ Frontend HTML de prueba
- ✅ Scripts de utilidad (clear_db.py, etc.)
- ✅ Configuración de Railway para deployment

### ✅ **Scrapers Incluidos:**
1. **Denver Public Library** - Con fechas reales
2. **Denver Zoo** - URLs específicas por evento
3. **Children's Museum** - Eventos interactivos
4. **Cinemark Movies** - Películas familiares
5. **Kids Out and About** - Actividades familiares
6. **AllTrails** - Senderos familiares
7. **Colorado Parent** - Eventos locales
8. **Denver Recreation** - Actividades públicas
9. **Macaroni Kid** - Eventos comunitarios
10. **Denver Events** - Eventos generales

### ✅ **Características Técnicas:**
- Manejo correcto de timezones (siempre Colorado Mountain Time)
- Sistema de caché inteligente
- Scheduling automático (diario a las 6 AM)
- APIs RESTful documentadas
- Frontend responsive
- Error handling robusto

## 🔧 Comandos Útiles Post-Recuperación

```bash
# Limpiar base de datos
python3 clear_db.py

# Ejecutar scraping manual
curl -X POST http://localhost:8000/api/v1/scheduler/run-manual

# Ver eventos en base de datos  
python3 find_library_events.py

# Verificar estado del sistema
curl http://localhost:8000/api/v1/health
```

## 📍 URLs Importantes Post-Recuperación

- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/health` 
- **All Events**: `http://localhost:8000/api/v1/events`
- **Active Events**: `http://localhost:8000/api/v1/events/active`
- **Frontend Test**: `file://eventos-test.html`

## 🆘 Troubleshooting Común

### **❌ Error de dependencias:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### **❌ Error de base de datos:**
```bash
python3 setup_db.py
python3 clear_db.py
```

### **❌ Error de zona horaria:**
```bash
pip install pytz python-dateutil
```

## 📞 URLs del Sistema en Vivo

- **GitHub**: https://github.com/NicoBaldowine/outworld-backend
- **Supabase**: Tu panel de Supabase
- **Railway**: Tu deployment (si configurado)

---

✅ **CONFIRMACIÓN**: Todo tu trabajo está guardado y se puede recuperar completamente en cualquier computador con estos pasos. 