"""
Sistema de logging para el bot de WhatsApp
"""

import logging
import csv
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
import config
import utils


class WhatsAppBotLogger:
    """
    Clase para gestionar el sistema de logging del bot.
    """
    
    def __init__(self):
        self.app_logger = None
        self.messages_logger = None
        self._setup_app_logger()
        self._setup_messages_logger()
    
    def _setup_app_logger(self):
        """
        Configura el logger principal de la aplicación.
        """
        # Crear logger principal
        self.app_logger = logging.getLogger('whatsapp_bot')
        self.app_logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # Evitar duplicar handlers si ya existen
        if self.app_logger.handlers:
            return
        
        # Formatter
        formatter = logging.Formatter(
            config.LOG_FORMAT,
            datefmt=config.LOG_DATE_FORMAT
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.app_logger.addHandler(console_handler)
        
        # Handler para archivo con rotación
        file_handler = RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.app_logger.addHandler(file_handler)
    
    def _setup_messages_logger(self):
        """
        Configura el logger para mensajes enviados (CSV).
        """
        self.messages_logger = logging.getLogger('messages_sent')
        self.messages_logger.setLevel(logging.INFO)
        
        # Evitar duplicar handlers si ya existen
        if self.messages_logger.handlers:
            return
        
        # Crear archivo CSV si no existe
        self._initialize_messages_csv()
    
    def _initialize_messages_csv(self):
        """
        Inicializa el archivo CSV para el registro de mensajes.
        """
        if not config.MESSAGES_LOG_FILE.exists():
            with open(config.MESSAGES_LOG_FILE, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'timestamp',
                    'nombre',
                    'telefono',
                    'mensaje',
                    'estado',
                    'error'
                ])
    
    def log_info(self, message: str):
        """
        Registra un mensaje informativo.
        
        Args:
            message (str): Mensaje a registrar
        """
        self.app_logger.info(message)
    
    def log_warning(self, message: str):
        """
        Registra una advertencia.
        
        Args:
            message (str): Mensaje de advertencia
        """
        self.app_logger.warning(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """
        Registra un error.
        
        Args:
            message (str): Mensaje de error
            exception (Optional[Exception]): Excepción asociada
        """
        if exception:
            self.app_logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.app_logger.error(message)
    
    def log_debug(self, message: str):
        """
        Registra un mensaje de debug.
        
        Args:
            message (str): Mensaje de debug
        """
        self.app_logger.debug(message)
    
    def log_message_sent(self, nombre: str, telefono: str, mensaje: str, 
                        estado: str, error: str = ""):
        """
        Registra un intento de envío de mensaje en el CSV.
        
        Args:
            nombre (str): Nombre del contacto
            telefono (str): Teléfono del contacto
            mensaje (str): Mensaje enviado
            estado (str): Estado del envío (ENVIADO, ERROR, SALTADO)
            error (str): Descripción del error si aplica
        """
        timestamp = utils.get_timestamp()
        
        # Truncar mensaje para el CSV
        mensaje_truncado = utils.truncate_string(mensaje, 200)
        
        try:
            with open(config.MESSAGES_LOG_FILE, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    timestamp,
                    nombre,
                    telefono,
                    mensaje_truncado,
                    estado,
                    error
                ])
        except Exception as e:
            self.log_error(f"Error al escribir en el CSV de mensajes", e)
    
    def log_session_start(self, total_contacts: int, limit: int):
        """
        Registra el inicio de una sesión.
        
        Args:
            total_contacts (int): Total de contactos cargados
            limit (int): Límite de mensajes a enviar
        """
        message = f"Iniciando sesión: {total_contacts} contactos cargados, límite: {limit}"
        self.log_info(message)
    
    def log_session_end(self, sent: int, total: int, errors: int):
        """
        Registra el final de una sesión.
        
        Args:
            sent (int): Mensajes enviados exitosamente
            total (int): Total de mensajes intentados
            errors (int): Número de errores
        """
        message = f"Sesión completada: {sent}/{total} mensajes enviados, {errors} errores"
        self.log_info(message)
    
    def log_qr_scan_start(self):
        """
        Registra el inicio del proceso de escaneo QR.
        """
        self.log_info("Esperando escaneo del código QR...")
    
    def log_qr_scan_success(self):
        """
        Registra el éxito del escaneo QR.
        """
        self.log_info("Código QR escaneado exitosamente")
    
    def log_qr_scan_timeout(self):
        """
        Registra el timeout del escaneo QR.
        """
        self.log_error("Tiempo agotado esperando el escaneo del código QR")
    
    def log_contact_processing(self, current: int, total: int, nombre: str):
        """
        Registra el procesamiento de un contacto.
        
        Args:
            current (int): Número actual
            total (int): Total de contactos
            nombre (str): Nombre del contacto
        """
        self.log_info(f"Procesando contacto {current}/{total}: {nombre}")


# Instancia global del logger
logger_instance = WhatsAppBotLogger()

# Funciones de conveniencia para usar el logger
def log_info(message: str):
    logger_instance.log_info(message)

def log_warning(message: str):
    logger_instance.log_warning(message)

def log_error(message: str, exception: Optional[Exception] = None):
    logger_instance.log_error(message, exception)

def log_debug(message: str):
    logger_instance.log_debug(message)

def log_message_sent(nombre: str, telefono: str, mensaje: str, estado: str, error: str = ""):
    logger_instance.log_message_sent(nombre, telefono, mensaje, estado, error)

def log_session_start(total_contacts: int, limit: int):
    logger_instance.log_session_start(total_contacts, limit)

def log_session_end(sent: int, total: int, errors: int):
    logger_instance.log_session_end(sent, total, errors)

def log_qr_scan_start():
    logger_instance.log_qr_scan_start()

def log_qr_scan_success():
    logger_instance.log_qr_scan_success()

def log_qr_scan_timeout():
    logger_instance.log_qr_scan_timeout()

def log_contact_processing(current: int, total: int, nombre: str):
    logger_instance.log_contact_processing(current, total, nombre)
