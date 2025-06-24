# WhatsApp Bot - Backend

Backend Flask para el bot de WhatsApp con soporte para WebSockets y Selenium.

## 🚀 Características

- 🔥 Flask + SocketIO para tiempo real
- 🤖 Selenium para automatización de WhatsApp
- 📊 Gestión de contactos desde Excel/CSV
- 🔒 CORS configurado para seguridad
- 📱 API REST para el frontend
- ⚡ Optimizado para Railway

## 🛠️ Tecnologías

- **Flask** - Framework web
- **SocketIO** - Comunicación en tiempo real
- **Selenium** - Automatización del navegador
- **Pandas** - Procesamiento de datos

## 🌐 Despliegue en Railway

Este backend está configurado para desplegarse automáticamente en Railway.

### Variables de Entorno Requeridas

```bash
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-super-segura
CORS_ORIGINS=https://tu-frontend.vercel.app
CHROME_DRIVER_PATH=/usr/bin/chromedriver
CHROME_BINARY_PATH=/usr/bin/google-chrome
```

## 📋 API Endpoints

- `GET /` - Estado del backend
- `GET /health` - Health check
- `POST /api/upload` - Subir archivo de contactos
- `GET /api/files` - Listar archivos disponibles
- `GET /api/contacts/preview/<filename>` - Preview de contactos
- `GET /api/validate-file/<filename>` - Validar archivo
- `WebSocket` - Comunicación en tiempo real para el bot

## 🔧 Configuración de Chrome

Railway incluye Chrome preinstalado. Las rutas se configuran automáticamente:
- Chrome Binary: `/usr/bin/google-chrome`
- ChromeDriver: `/usr/bin/chromedriver`

## 📄 Licencia

MIT License
