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
- **Gunicorn** - Servidor WSGI para producción

## 🏃‍♂️ Desarrollo Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar en desarrollo
python app.py
```

## 🌐 Despliegue en Railway

1. Conecta este repositorio a Railway
2. Railway detectará automáticamente Python
3. Configura las variables de entorno:
   - `FLASK_ENV=production`
   - `SECRET_KEY=tu-clave-secreta`
4. Despliega automáticamente

## 📝 Variables de Entorno

```bash
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-aqui
PORT=5000
CORS_ORIGINS=https://tu-frontend.vercel.app
```

## 🔗 Frontend

Este backend se conecta con el frontend Next.js desplegado en Vercel.
Repositorio del frontend: [whatsapp-bot-frontend](../whatsapp-bot-frontend)

## 📋 API Endpoints

- `POST /api/upload` - Subir archivo de contactos
- `GET /api/files` - Listar archivos disponibles
- `GET /api/contacts/preview/<filename>` - Preview de contactos
- `WebSocket` - Comunicación en tiempo real para el bot

## 🔧 Configuración de Chrome

Railway incluye Chrome preinstalado. Las rutas se configuran automáticamente:
- Chrome Binary: `/usr/bin/google-chrome`
- ChromeDriver: `/usr/bin/chromedriver`

## 📄 Licencia

MIT License
