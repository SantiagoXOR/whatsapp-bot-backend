"""
Módulo para gestionar el envío de mensajes a múltiples contactos
"""

import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
import config
import logger
import utils
from whatsapp_client import WhatsAppClient


@dataclass
class SendingStats:
    """
    Clase para almacenar estadísticas de envío.
    """
    total_contacts: int = 0
    messages_sent: int = 0
    messages_failed: int = 0
    messages_skipped: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    @property
    def success_rate(self) -> float:
        """Calcula la tasa de éxito."""
        if self.total_contacts == 0:
            return 0.0
        return (self.messages_sent / self.total_contacts) * 100

    @property
    def duration_minutes(self) -> float:
        """Calcula la duración en minutos."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) / 60
        return 0.0


class MessageSender:
    """
    Clase para gestionar el envío de mensajes a múltiples contactos.
    """

    def __init__(self, whatsapp_client: WhatsAppClient, progress_callback=None):
        self.client = whatsapp_client
        self.stats = SendingStats()
        self.is_sending = False
        self.should_stop = False
        self.progress_callback = progress_callback

    def send_messages_to_contacts(self, contacts: List[Dict],
                                 limit: Optional[int] = None,
                                 delay: int = config.DEFAULT_DELAY_BETWEEN_MESSAGES) -> SendingStats:
        """
        Envía mensajes a una lista de contactos.

        Args:
            contacts (List[Dict]): Lista de contactos
            limit (Optional[int]): Límite de mensajes a enviar
            delay (int): Segundos de espera entre mensajes

        Returns:
            SendingStats: Estadísticas del envío
        """
        # Inicializar estadísticas
        self.stats = SendingStats()
        self.stats.total_contacts = min(len(contacts), limit) if limit else len(contacts)
        self.stats.start_time = time.time()
        self.is_sending = True
        self.should_stop = False

        # Filtrar contactos según el límite
        contacts_to_process = contacts[:limit] if limit else contacts

        logger.log_session_start(len(contacts), self.stats.total_contacts)

        try:
            for i, contact in enumerate(contacts_to_process, 1):
                if self.should_stop:
                    logger.log_info("Envío detenido por el usuario")
                    break

                # Verificar que el navegador siga funcionando
                if not self.client.is_browser_running():
                    logger.log_error("El navegador se cerró inesperadamente")
                    break

                # Procesar contacto
                self._process_contact(contact, i, self.stats.total_contacts)

                # Aplicar delay entre mensajes (excepto en el último)
                if i < self.stats.total_contacts and not self.should_stop:
                    self._apply_delay(delay, i, self.stats.total_contacts)

        except KeyboardInterrupt:
            logger.log_info("Envío interrumpido por el usuario (Ctrl+C)")
            self.should_stop = True

        except Exception as e:
            logger.log_error("Error durante el envío de mensajes", e)

        finally:
            self.stats.end_time = time.time()
            self.is_sending = False
            self._log_session_summary()

        return self.stats

    def _process_contact(self, contact: Dict, current: int, total: int):
        """
        Procesa un contacto individual.

        Args:
            contact (Dict): Datos del contacto
            current (int): Número actual
            total (int): Total de contactos
        """
        nombre = contact.get('nombre', 'Sin nombre')
        telefono = contact.get('telefono', '')
        mensaje = contact.get('mensaje', config.DEFAULT_MESSAGE_TEMPLATE)

        logger.log_contact_processing(current, total, nombre)

        # Validar teléfono
        if not utils.validate_phone_number(telefono):
            error_msg = f"Número de teléfono inválido: {telefono}"
            logger.log_warning(error_msg)
            logger.log_message_sent(nombre, telefono, mensaje, "SALTADO", error_msg)
            self.stats.messages_skipped += 1
            return

        # Formatear mensaje
        mensaje_formateado = utils.format_message(mensaje, contact)

        # Mostrar progreso en consola
        self._show_progress(current, total, nombre, telefono)

        # Notificar progreso a la GUI si hay callback
        if self.progress_callback:
            self.progress_callback(current, total)

        # Intentar enviar mensaje
        try:
            success = self.client.send_message_to_contact(telefono, mensaje_formateado)

            if success:
                logger.log_info(config.MESSAGES["message_sent"].format(contact=nombre))
                logger.log_message_sent(nombre, telefono, mensaje_formateado, "ENVIADO")
                self.stats.messages_sent += 1
            else:
                error_msg = "No se pudo enviar el mensaje"
                logger.log_warning(config.MESSAGES["message_failed"].format(contact=nombre, error=error_msg))
                logger.log_message_sent(nombre, telefono, mensaje_formateado, "ERROR", error_msg)
                self.stats.messages_failed += 1

        except Exception as e:
            error_msg = str(e)
            logger.log_error(f"Error al enviar mensaje a {nombre}", e)
            logger.log_message_sent(nombre, telefono, mensaje_formateado, "ERROR", error_msg)
            self.stats.messages_failed += 1

    def _apply_delay(self, base_delay: int, current: int, total: int):
        """
        Aplica un delay entre mensajes con variación aleatoria.

        Args:
            base_delay (int): Delay base en segundos
            current (int): Mensaje actual
            total (int): Total de mensajes
        """
        # Agregar variación aleatoria del ±20%
        variation = random.uniform(0.8, 1.2)
        actual_delay = int(base_delay * variation)

        logger.log_debug(f"Esperando {actual_delay} segundos antes del siguiente mensaje...")

        # Mostrar countdown
        for remaining in range(actual_delay, 0, -1):
            if self.should_stop:
                break

            print(f"\rEsperando {remaining} segundos... (Mensaje {current}/{total})", end="", flush=True)
            time.sleep(1)

        print()  # Nueva línea después del countdown

    def _show_progress(self, current: int, total: int, nombre: str, telefono: str):
        """
        Muestra el progreso actual en la consola.

        Args:
            current (int): Número actual
            total (int): Total de contactos
            nombre (str): Nombre del contacto
            telefono (str): Teléfono del contacto
        """
        percentage = (current / total) * 100
        progress_bar = self._create_progress_bar(percentage)

        print(f"\n{'='*60}")
        print(f"PROGRESO: {current}/{total} ({percentage:.1f}%)")
        print(f"{progress_bar}")
        print(f"CONTACTO: {nombre}")
        print(f"TELÉFONO: {telefono}")
        print(f"ENVIADOS: {self.stats.messages_sent} | ERRORES: {self.stats.messages_failed} | SALTADOS: {self.stats.messages_skipped}")
        print(f"{'='*60}")

    def _create_progress_bar(self, percentage: float, width: int = 40) -> str:
        """
        Crea una barra de progreso visual.

        Args:
            percentage (float): Porcentaje completado
            width (int): Ancho de la barra

        Returns:
            str: Barra de progreso
        """
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percentage:.1f}%"

    def _log_session_summary(self):
        """
        Registra un resumen de la sesión completada.
        """
        logger.log_session_end(
            self.stats.messages_sent,
            self.stats.total_contacts,
            self.stats.messages_failed
        )

        # Mostrar resumen detallado en consola
        print(f"\n{'='*60}")
        print("RESUMEN DE LA SESIÓN")
        print(f"{'='*60}")
        print(f"Total de contactos procesados: {self.stats.total_contacts}")
        print(f"Mensajes enviados exitosamente: {self.stats.messages_sent}")
        print(f"Mensajes con error: {self.stats.messages_failed}")
        print(f"Mensajes saltados: {self.stats.messages_skipped}")
        print(f"Tasa de éxito: {self.stats.success_rate:.1f}%")

        if self.stats.duration_minutes > 0:
            print(f"Duración total: {self.stats.duration_minutes:.1f} minutos")
            messages_per_minute = self.stats.messages_sent / self.stats.duration_minutes
            print(f"Velocidad promedio: {messages_per_minute:.1f} mensajes/minuto")

        print(f"{'='*60}")

        # Mostrar mensaje final
        if self.stats.messages_sent > 0:
            print(f"\n✅ Sesión completada exitosamente!")
            print(f"Se enviaron {self.stats.messages_sent} mensajes.")
        else:
            print(f"\n❌ No se pudo enviar ningún mensaje.")

        if self.stats.messages_failed > 0:
            print(f"⚠️  {self.stats.messages_failed} mensajes fallaron.")
            print("Revisa el archivo de log para más detalles.")

    def stop_sending(self):
        """
        Detiene el envío de mensajes.
        """
        self.should_stop = True
        logger.log_info("Solicitando detener el envío de mensajes...")

    def get_stats(self) -> SendingStats:
        """
        Obtiene las estadísticas actuales.

        Returns:
            SendingStats: Estadísticas del envío
        """
        return self.stats

    def is_sending_active(self) -> bool:
        """
        Verifica si el envío está activo.

        Returns:
            bool: True si el envío está activo
        """
        return self.is_sending
