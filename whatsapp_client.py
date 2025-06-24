"""
Cliente de WhatsApp usando Selenium para automatizar WhatsApp Web
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementNotInteractableException
)
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional, Dict
import config
import logger
import utils


class WhatsAppClient:
    """
    Cliente para interactuar con WhatsApp Web usando Selenium.
    """
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.is_authenticated = False
    
    def start_browser(self) -> bool:
        """
        Inicia el navegador Chrome y carga WhatsApp Web.
        
        Returns:
            bool: True si el navegador se inició correctamente
        """
        try:
            logger.log_info("Iniciando navegador Chrome...")
            
            # Configurar opciones de Chrome
            chrome_options = Options()
            
            # Agregar opciones de configuración
            for option in config.CHROME_OPTIONS:
                chrome_options.add_argument(option)
            
            # Configurar perfil de usuario si se especifica
            if config.CHROME_USER_DATA_DIR:
                chrome_options.add_argument(f"--user-data-dir={config.CHROME_USER_DATA_DIR}")
            
            if config.CHROME_PROFILE_PATH:
                chrome_options.add_argument(f"--profile-directory={config.CHROME_PROFILE_PATH}")
            
            # Configurar servicio del driver
            if config.CHROME_DRIVER_PATH:
                service = Service(config.CHROME_DRIVER_PATH)
            else:
                service = Service(ChromeDriverManager().install())
            
            # Inicializar driver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, config.TIMEOUT_ELEMENT_WAIT)
            
            # Configurar timeouts
            self.driver.implicitly_wait(config.TIMEOUT_ELEMENT_WAIT)
            self.driver.set_page_load_timeout(config.TIMEOUT_PAGE_LOAD)
            
            # Cargar WhatsApp Web
            logger.log_info("Cargando WhatsApp Web...")
            self.driver.get(config.WHATSAPP_WEB_URL)
            
            return True
            
        except Exception as e:
            logger.log_error("Error al iniciar el navegador", e)
            return False
    
    def wait_for_qr_scan(self) -> bool:
        """
        Espera a que el usuario escanee el código QR.
        
        Returns:
            bool: True si el escaneo fue exitoso
        """
        try:
            logger.log_qr_scan_start()
            print(config.MESSAGES["qr_scan_prompt"])
            
            # Esperar a que aparezca el panel lateral (indica que se escaneó el QR)
            self.wait = WebDriverWait(self.driver, config.TIMEOUT_QR_SCAN)
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS["side_panel"]))
            )
            
            # Esperar un poco más para asegurar que la página cargue completamente
            time.sleep(3)
            
            self.is_authenticated = True
            logger.log_qr_scan_success()
            print(config.MESSAGES["qr_scan_success"])
            
            return True
            
        except TimeoutException:
            logger.log_qr_scan_timeout()
            print(config.MESSAGES["qr_scan_timeout"])
            return False
        except Exception as e:
            logger.log_error("Error durante el escaneo del código QR", e)
            return False
    
    def search_contact(self, phone_number: str) -> bool:
        """
        Busca un contacto por número de teléfono.
        
        Args:
            phone_number (str): Número de teléfono a buscar
            
        Returns:
            bool: True si el contacto fue encontrado
        """
        try:
            # Buscar la caja de búsqueda
            search_box = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS["search_box"]))
            )
            
            # Limpiar la caja de búsqueda
            search_box.clear()
            time.sleep(0.5)
            
            # Escribir el número de teléfono
            search_box.send_keys(phone_number)
            time.sleep(2)
            
            # Presionar Enter para buscar
            search_box.send_keys(Keys.ENTER)
            time.sleep(3)
            
            # Verificar si se encontró el contacto
            try:
                # Buscar el título del chat que indica que se abrió una conversación
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS["chat_header"]))
                )
                return True
                
            except TimeoutException:
                # Verificar si apareció un mensaje de número inválido
                try:
                    invalid_number_popup = self.driver.find_element(
                        By.CSS_SELECTOR, config.SELECTORS["invalid_number"]
                    )
                    if invalid_number_popup.is_displayed():
                        logger.log_warning(f"Número inválido o no registrado en WhatsApp: {phone_number}")
                        return False
                except NoSuchElementException:
                    pass
                
                logger.log_warning(f"No se pudo encontrar el contacto: {phone_number}")
                return False
                
        except Exception as e:
            logger.log_error(f"Error al buscar contacto {phone_number}", e)
            return False
    
    def send_message(self, message: str) -> bool:
        """
        Envía un mensaje al chat actualmente abierto.
        
        Args:
            message (str): Mensaje a enviar
            
        Returns:
            bool: True si el mensaje fue enviado exitosamente
        """
        try:
            # Buscar la caja de mensaje
            message_box = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS["message_box"]))
            )
            
            # Limpiar la caja de mensaje
            message_box.clear()
            time.sleep(0.5)
            
            # Escribir el mensaje
            message_box.send_keys(message)
            time.sleep(1)
            
            # Buscar y hacer clic en el botón de enviar
            send_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS["send_button"]))
            )
            send_button.click()
            
            # Esperar un momento para que se envíe el mensaje
            time.sleep(config.TIMEOUT_MESSAGE_SEND)
            
            return True
            
        except Exception as e:
            logger.log_error(f"Error al enviar mensaje: {message[:50]}...", e)
            return False
    
    def send_message_to_contact(self, phone_number: str, message: str) -> bool:
        """
        Envía un mensaje a un contacto específico.
        
        Args:
            phone_number (str): Número de teléfono del contacto
            message (str): Mensaje a enviar
            
        Returns:
            bool: True si el mensaje fue enviado exitosamente
        """
        try:
            # Buscar el contacto
            if not self.search_contact(phone_number):
                return False
            
            # Enviar el mensaje
            return self.send_message(message)
            
        except Exception as e:
            logger.log_error(f"Error al enviar mensaje a {phone_number}", e)
            return False
    
    def is_browser_running(self) -> bool:
        """
        Verifica si el navegador está funcionando.
        
        Returns:
            bool: True si el navegador está funcionando
        """
        try:
            if self.driver is None:
                return False
            
            # Intentar obtener el título de la página
            self.driver.title
            return True
            
        except WebDriverException:
            return False
    
    def close_browser(self):
        """
        Cierra el navegador y limpia los recursos.
        """
        try:
            if self.driver:
                logger.log_info("Cerrando navegador...")
                self.driver.quit()
                self.driver = None
                self.wait = None
                self.is_authenticated = False
                
        except Exception as e:
            logger.log_error("Error al cerrar el navegador", e)
    
    def get_current_chat_title(self) -> Optional[str]:
        """
        Obtiene el título del chat actual.
        
        Returns:
            Optional[str]: Título del chat o None si no se puede obtener
        """
        try:
            chat_header = self.driver.find_element(
                By.CSS_SELECTOR, config.SELECTORS["chat_header"]
            )
            title_element = chat_header.find_element(By.CSS_SELECTOR, "span[title]")
            return title_element.get_attribute("title")
            
        except Exception:
            return None
    
    def take_screenshot(self, filename: str) -> bool:
        """
        Toma una captura de pantalla del navegador.
        
        Args:
            filename (str): Nombre del archivo para guardar la captura
            
        Returns:
            bool: True si la captura fue exitosa
        """
        try:
            if self.driver:
                screenshot_path = config.LOGS_DIR / f"{filename}_{utils.get_timestamp_filename()}.png"
                self.driver.save_screenshot(str(screenshot_path))
                logger.log_info(f"Captura de pantalla guardada: {screenshot_path}")
                return True
            return False
            
        except Exception as e:
            logger.log_error("Error al tomar captura de pantalla", e)
            return False
