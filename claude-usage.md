# Claude Usage Documentation

## 🚀 Quick Start

### Prerequisites
- Claude API Key from Anthropic
- Node.js 18+ installed
- TypeScript support

### Installation
```bash
npm install
```

### Configuration
Tu API key está en `.env`:
```
CLAUDE_API_KEY=your-api-key-here
```

## 🎯 Integración con tu Workflow

### Uso Básico

```bash
npm run claude-ts queries
```
**Uso**: Genera 10 consultas realistas que familias buscarían en Denver.

### 2. **💡 Ayuda de Programación**
```bash
npm run claude-ts help "tu pregunta aquí"
```
**Ejemplos**:
```bash
npm run claude-ts help "How to improve web scraping performance?"
npm run claude-ts help "Best practices for FastAPI endpoints?"
npm run claude-ts help "How to handle JavaScript-rendered content?"
```

### 3. **🔍 Analizar Eventos Scrapeados**
```bash
npm run claude-ts analyze "Event data here"
```
**Uso**: Claude analizará la calidad de los eventos y sugerirá mejoras.

### 4. **🛠️ Mejorar Scrapers**
```bash
npm run claude-ts improve "scraper_name"
```
**Uso**: Claude revisará código de scrapers y sugerirá optimizaciones.

### 5. **📝 Mejorar Descripciones**
```bash
npm run claude-ts enhance
```
**Uso**: Claude mejorará las descripciones de eventos para ser más atractivas.

## 📋 Casos de Uso Específicos

### Para Debugging de Scrapers:
```bash
npm run claude-ts help "My scraper is getting 403 errors. How can I fix this?"
npm run claude-ts help "How to parse dynamic content with BeautifulSoup?"
```

### Para Optimización:
```bash
npm run claude-ts help "How to make my FastAPI app faster?"
npm run claude-ts help "Best database query patterns for Supabase?"
```

### Para Nuevas Funcionalidades:
```bash
npm run claude-ts help "How to add email notifications to my scraper?"
npm run claude-ts help "How to implement caching in Python?"
```

## 💰 Modelo Usado

**Claude 3 Haiku**: Rápido y económico para consultas frecuentes
- ⚡ Respuestas rápidas
- 💰 Costo bajo por token
- 🎯 Perfecto para advice y análisis

## 🔄 Próximas Mejoras

1. **Integración con la base de datos**: Análisis automático de eventos
2. **Scraper auto-improvement**: Claude sugiere mejoras basadas en errores
3. **Content generation**: Descriptions automáticas con Claude
4. **Quality scoring**: Claude evalúa la calidad de eventos scrapeados

## 🎉 ¡Ya puedes usar Claude!

**Comando más útil para empezar**:
```bash
npm run claude-ts help "What are the best practices for web scraping in 2024?"
``` 