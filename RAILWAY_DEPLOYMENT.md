# 🚀 Instrucciones de Deployment en Railway

## Pasos para desplegar:

1. **Conectar repositorio a Railway**:
   - Ve a https://railway.app
   - Haz clic en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Conecta este repositorio

2. **Configurar variables de entorno**:
   ```
   FLASK_ENV=production
   SECRET_KEY=tu-clave-secreta-super-segura
   CORS_ORIGINS=https://tu-frontend.vercel.app
   CHROME_DRIVER_PATH=/usr/bin/chromedriver
   CHROME_BINARY_PATH=/usr/bin/google-chrome
   ```

3. **Railway detectará automáticamente**:
   - Python como runtime
   - requirements.txt para dependencias
   - Procfile para comando de inicio

4. **Verificar deployment**:
   - Acceder a la URL generada
   - Verificar endpoint /health
   - Probar endpoints /api/*

## URL del deployment:
https://tu-proyecto.railway.app
