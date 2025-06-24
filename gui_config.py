"""
Configuración específica para la interfaz gráfica
"""

# Configuración de la ventana principal
WINDOW_TITLE = "Bot de WhatsApp - Envío Automatizado"
WINDOW_SIZE = "800x700"
WINDOW_MIN_SIZE = (600, 500)

# Colores y estilos
COLORS = {
    'primary': '#25D366',      # Verde WhatsApp
    'secondary': '#128C7E',    # Verde oscuro WhatsApp
    'success': '#4CAF50',      # Verde éxito
    'warning': '#FF9800',      # Naranja advertencia
    'error': '#F44336',        # Rojo error
    'info': '#2196F3',         # Azul información
    'background': '#F5F5F5',   # Gris claro
    'text': '#333333'          # Gris oscuro
}

# Configuración de fuentes
FONTS = {
    'title': ('Arial', 16, 'bold'),
    'subtitle': ('Arial', 12, 'bold'),
    'normal': ('Arial', 10),
    'small': ('Arial', 8)
}

# Iconos y emojis
ICONS = {
    'bot': '🤖',
    'file': '📁',
    'config': '⚙️',
    'contacts': '👥',
    'controls': '🎮',
    'log': '📝',
    'start': '🚀',
    'stop': '⏹️',
    'test': '🧪',
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'phone': '📱',
    'message': '💬',
    'progress': '📊'
}

# Mensajes de la interfaz
MESSAGES = {
    'welcome': "Bienvenido al Bot de WhatsApp",
    'select_file': "Selecciona un archivo CSV o Excel con tus contactos",
    'file_selected': "Archivo seleccionado correctamente",
    'contacts_loaded': "Contactos cargados y validados",
    'bot_starting': "Iniciando bot de WhatsApp...",
    'qr_waiting': "Esperando escaneo de código QR",
    'qr_scanned': "Código QR escaneado exitosamente",
    'sending_messages': "Enviando mensajes...",
    'bot_completed': "Envío completado exitosamente",
    'bot_stopped': "Bot detenido por el usuario",
    'connection_test': "Probando conexión a WhatsApp Web...",
    'connection_success': "Conexión exitosa",
    'connection_failed': "Error de conexión"
}

# Configuración de validación
VALIDATION = {
    'max_limit': 1000,
    'min_limit': 1,
    'max_delay': 300,
    'min_delay': 5,
    'supported_formats': ['.csv', '.xlsx', '.xls'],
    'max_file_size_mb': 50
}

# Configuración de logging para GUI
GUI_LOG_CONFIG = {
    'max_lines': 1000,
    'auto_scroll': True,
    'timestamp_format': "%H:%M:%S",
    'show_level_icons': True
}

# Tooltips y ayuda
TOOLTIPS = {
    'file_browse': "Selecciona un archivo CSV o Excel con columnas: nombre, telefono, mensaje",
    'limit': "Número máximo de mensajes a enviar (1-1000)",
    'delay': "Segundos de espera entre mensajes (5-300)",
    'validate': "Valida los contactos del archivo seleccionado",
    'start': "Inicia el bot de WhatsApp (requiere escanear código QR)",
    'stop': "Detiene el envío de mensajes",
    'test': "Prueba la conexión abriendo WhatsApp Web"
}

# Configuración de progreso
PROGRESS_CONFIG = {
    'update_interval': 100,  # ms
    'show_percentage': True,
    'show_count': True,
    'animate': True
}

# Configuración de threads
THREAD_CONFIG = {
    'daemon': True,
    'timeout': 300,  # 5 minutos
    'queue_check_interval': 100  # ms
}
