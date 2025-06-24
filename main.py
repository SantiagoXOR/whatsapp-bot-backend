"""
Punto de entrada principal para el bot de WhatsApp
"""

import sys
import argparse
import signal
from pathlib import Path
from typing import Optional

import config
import logger
import utils
from data_manager import DataManager
from whatsapp_client import WhatsAppClient
from message_sender import MessageSender


class WhatsAppBot:
    """
    Clase principal del bot de WhatsApp.
    """
    
    def __init__(self):
        self.data_manager = DataManager()
        self.whatsapp_client = WhatsAppClient()
        self.message_sender = MessageSender(self.whatsapp_client)
        self.contacts = []
    
    def run(self, input_file: str, limit: Optional[int] = None, 
            delay: int = config.DEFAULT_DELAY_BETWEEN_MESSAGES) -> bool:
        """
        Ejecuta el bot de WhatsApp.
        
        Args:
            input_file (str): Ruta al archivo de contactos
            limit (Optional[int]): Límite de mensajes a enviar
            delay (int): Segundos de espera entre mensajes
            
        Returns:
            bool: True si la ejecución fue exitosa
        """
        try:
            logger.log_info("Iniciando bot de WhatsApp...")
            
            # Paso 1: Cargar contactos
            if not self._load_contacts(input_file):
                return False
            
            # Paso 2: Validar contactos
            if not self._validate_contacts():
                return False
            
            # Paso 3: Iniciar navegador
            if not self._start_browser():
                return False
            
            # Paso 4: Autenticar en WhatsApp
            if not self._authenticate():
                return False
            
            # Paso 5: Enviar mensajes
            stats = self._send_messages(limit, delay)
            
            # Paso 6: Mostrar resultados
            return stats.messages_sent > 0
            
        except KeyboardInterrupt:
            logger.log_info("Ejecución interrumpida por el usuario")
            return False
        except Exception as e:
            logger.log_error("Error durante la ejecución del bot", e)
            return False
        finally:
            self._cleanup()
    
    def _load_contacts(self, input_file: str) -> bool:
        """
        Carga los contactos desde el archivo especificado.
        
        Args:
            input_file (str): Ruta al archivo de contactos
            
        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            logger.log_info(f"Cargando contactos desde: {input_file}")
            self.contacts = self.data_manager.load_contacts(input_file)
            
            if not self.contacts:
                logger.log_error("No se encontraron contactos válidos en el archivo")
                return False
            
            return True
            
        except Exception as e:
            logger.log_error("Error al cargar contactos", e)
            return False
    
    def _validate_contacts(self) -> bool:
        """
        Valida los contactos cargados.
        
        Returns:
            bool: True si hay contactos válidos
        """
        stats = self.data_manager.validate_contacts()
        
        logger.log_info(f"Estadísticas de contactos:")
        logger.log_info(f"  Total: {stats['total']}")
        logger.log_info(f"  Válidos: {stats['valid']}")
        logger.log_info(f"  Teléfonos inválidos: {stats['invalid_phone']}")
        logger.log_info(f"  Nombres vacíos: {stats['empty_name']}")
        
        if stats['valid'] == 0:
            logger.log_error("No hay contactos válidos para procesar")
            return False
        
        return True
    
    def _start_browser(self) -> bool:
        """
        Inicia el navegador Chrome.
        
        Returns:
            bool: True si el navegador se inició correctamente
        """
        try:
            return self.whatsapp_client.start_browser()
        except Exception as e:
            logger.log_error("Error al iniciar el navegador", e)
            return False
    
    def _authenticate(self) -> bool:
        """
        Autentica en WhatsApp Web.
        
        Returns:
            bool: True si la autenticación fue exitosa
        """
        try:
            return self.whatsapp_client.wait_for_qr_scan()
        except Exception as e:
            logger.log_error("Error durante la autenticación", e)
            return False
    
    def _send_messages(self, limit: Optional[int], delay: int):
        """
        Envía mensajes a los contactos.
        
        Args:
            limit (Optional[int]): Límite de mensajes
            delay (int): Delay entre mensajes
            
        Returns:
            SendingStats: Estadísticas del envío
        """
        # Filtrar contactos según el límite
        contacts_to_send = self.data_manager.filter_contacts(limit)
        
        logger.log_info(f"Iniciando envío de mensajes a {len(contacts_to_send)} contactos")
        logger.log_info(f"Delay entre mensajes: {delay} segundos")
        
        return self.message_sender.send_messages_to_contacts(
            contacts_to_send, limit, delay
        )
    
    def _cleanup(self):
        """
        Limpia recursos y cierra el navegador.
        """
        try:
            logger.log_info("Limpiando recursos...")
            self.whatsapp_client.close_browser()
        except Exception as e:
            logger.log_error("Error durante la limpieza", e)


def setup_signal_handlers(bot: WhatsAppBot):
    """
    Configura manejadores de señales para una salida limpia.
    
    Args:
        bot (WhatsAppBot): Instancia del bot
    """
    def signal_handler(signum, frame):
        logger.log_info("Recibida señal de interrupción, cerrando...")
        bot.message_sender.stop_sending()
        bot._cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.
    
    Returns:
        argparse.Namespace: Argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description="Bot automatizado para enviar mensajes de WhatsApp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py -i contactos.xlsx
  python main.py -i contactos.csv -l 30 -d 25
  python main.py --input datos.xlsx --limit 50 --delay 15

Formato del archivo de contactos:
  - Columnas requeridas: nombre, telefono
  - Columna opcional: mensaje
  - Formatos soportados: .xlsx, .xls, .csv
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Ruta al archivo de contactos (Excel o CSV)'
    )
    
    parser.add_argument(
        '-l', '--limit',
        type=int,
        default=config.DEFAULT_MESSAGE_LIMIT,
        help=f'Límite de mensajes a enviar (default: {config.DEFAULT_MESSAGE_LIMIT})'
    )
    
    parser.add_argument(
        '-d', '--delay',
        type=int,
        default=config.DEFAULT_DELAY_BETWEEN_MESSAGES,
        help=f'Segundos de espera entre mensajes (default: {config.DEFAULT_DELAY_BETWEEN_MESSAGES})'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='WhatsApp Bot 1.0.0'
    )
    
    return parser.parse_args()


def validate_arguments(args):
    """
    Valida los argumentos de línea de comandos.
    
    Args:
        args: Argumentos parseados
        
    Returns:
        bool: True si los argumentos son válidos
    """
    # Validar archivo de entrada
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: El archivo '{args.input}' no existe.")
        return False
    
    if not utils.is_valid_file_type(input_path, ['xlsx', 'xls', 'csv']):
        print(f"Error: Tipo de archivo no soportado. Use .xlsx, .xls o .csv")
        return False
    
    # Validar límite
    if args.limit <= 0:
        print(f"Error: El límite debe ser mayor a 0.")
        return False
    
    # Validar delay
    if args.delay < 5:
        print(f"Error: El delay debe ser al menos 5 segundos para evitar bloqueos.")
        return False
    
    return True


def main():
    """
    Función principal del programa.
    """
    try:
        # Parsear argumentos
        args = parse_arguments()
        
        # Validar argumentos
        if not validate_arguments(args):
            sys.exit(1)
        
        # Mostrar información inicial
        print("="*60)
        print("BOT DE WHATSAPP - ENVÍO AUTOMATIZADO DE MENSAJES")
        print("="*60)
        print(f"Archivo de contactos: {args.input}")
        print(f"Límite de mensajes: {args.limit}")
        print(f"Delay entre mensajes: {args.delay} segundos")
        print("="*60)
        
        # Crear instancia del bot
        bot = WhatsAppBot()
        
        # Configurar manejadores de señales
        setup_signal_handlers(bot)
        
        # Ejecutar bot
        success = bot.run(args.input, args.limit, args.delay)
        
        # Salir con código apropiado
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nEjecución interrumpida por el usuario.")
        sys.exit(1)
    except Exception as e:
        logger.log_error("Error fatal en la aplicación", e)
        print(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
