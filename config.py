"""
Configuración centralizada para el bot de WhatsApp
"""

import os
from pathlib import Path

# Configuración del navegador
CHROME_DRIVER_PATH = None  # None para usar webdriver-manager
CHROME_PROFILE_PATH = None  # None para usar perfil temporal
CHROME_USER_DATA_DIR = None  # None para usar directorio temporal

# URLs
WHATSAPP_WEB_URL = "https://web.whatsapp.com"

# Tiempos de espera (en segundos)
TIMEOUT_QR_SCAN = 60  # Tiempo para escanear código QR
TIMEOUT_PAGE_LOAD = 30  # Tiempo para cargar páginas
TIMEOUT_ELEMENT_WAIT = 10  # Tiempo para encontrar elementos
TIMEOUT_MESSAGE_SEND = 5  # Tiempo para enviar mensaje

# Límites
DEFAULT_MESSAGE_LIMIT = 50  # Número máximo de mensajes por sesión
DEFAULT_DELAY_BETWEEN_MESSAGES = 20  # Segundos entre mensajes

# Mensajes
DEFAULT_MESSAGE_TEMPLATE = "Hola {nombre}, este es un mensaje automático."

# Configuración de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Directorios
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

# Crear directorios si no existen
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Archivos de log
LOG_FILE = LOGS_DIR / "whatsapp_bot.log"
MESSAGES_LOG_FILE = LOGS_DIR / "messages_sent.csv"

# Configuración de archivos CSV
CSV_REQUIRED_COLUMNS = ["nombre", "telefono"]
CSV_OPTIONAL_COLUMNS = ["mensaje"]

# Selectores CSS para WhatsApp Web (pueden cambiar con actualizaciones)
SELECTORS = {
    "search_box": 'div[contenteditable="true"][data-tab="3"]',
    "contact_title": 'span[title]',
    "message_box": 'div[contenteditable="true"][data-tab="10"]',
    "send_button": 'span[data-icon="send"]',
    "qr_code": 'canvas[aria-label="Scan me!"]',
    "side_panel": 'div[data-testid="chatlist-header"]',
    "chat_header": 'header[data-testid="conversation-header"]',
    "invalid_number": 'div[data-animate-modal-popup="true"]'
}

# Configuración de Chrome
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",
    "--disable-javascript",
    "--disable-web-security",
    "--allow-running-insecure-content",
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Configuración de validación de números
PHONE_NUMBER_MIN_LENGTH = 8
PHONE_NUMBER_MAX_LENGTH = 15

# Mensajes del sistema
MESSAGES = {
    "qr_scan_prompt": "Por favor, escanea el código QR con tu teléfono para iniciar sesión en WhatsApp Web.",
    "qr_scan_success": "Código QR escaneado exitosamente. Iniciando envío de mensajes...",
    "qr_scan_timeout": "Tiempo agotado esperando el escaneo del código QR.",
    "contact_not_found": "No se pudo encontrar el contacto: {contact}",
    "message_sent": "Mensaje enviado a {contact}",
    "message_failed": "Error al enviar mensaje a {contact}: {error}",
    "session_complete": "Sesión completada. {sent}/{total} mensajes enviados.",
    "invalid_phone": "Número de teléfono inválido: {phone}",
    "file_not_found": "Archivo no encontrado: {file}",
    "data_loaded": "Datos cargados: {count} contactos encontrados."
}
