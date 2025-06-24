#!/usr/bin/env python3
"""
Tests unitarios para el bot de WhatsApp
"""

import pytest
import tempfile
import os
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Agregar el directorio actual al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import utils
import logger
from data_manager import DataManager


class TestUtils:
    """Tests para el módulo utils.py"""

    def test_validate_phone_number_valid(self):
        """Test validación de números válidos"""
        assert utils.validate_phone_number("5491123456789") == True
        assert utils.validate_phone_number("1234567890") == True
        assert utils.validate_phone_number("123456789012345") == True

    def test_validate_phone_number_invalid(self):
        """Test validación de números inválidos"""
        assert utils.validate_phone_number("") == False
        assert utils.validate_phone_number(None) == False
        assert utils.validate_phone_number("123") == False  # Muy corto
        assert utils.validate_phone_number("1234567890123456") == False  # Muy largo
        assert utils.validate_phone_number("abcdefghijk") == False  # Solo letras
        assert utils.validate_phone_number("   ") == False  # Solo espacios

    def test_format_phone_number(self):
        """Test formateo de números de teléfono"""
        assert utils.format_phone_number("549-11-2345-6789") == "5491123456789"
        assert utils.format_phone_number("+54 9 11 2345 6789") == "5491123456789"
        assert utils.format_phone_number("(549) 11-2345-6789") == "5491123456789"
        assert utils.format_phone_number("invalid") == None

    def test_sanitize_filename(self):
        """Test sanitización de nombres de archivo"""
        assert utils.sanitize_filename("archivo normal.txt") == "archivo normal.txt"
        assert utils.sanitize_filename("archivo/con\\caracteres:especiales") == "archivoconcaracteresespeciales"
        assert utils.sanitize_filename("  espacios  múltiples  ") == "espacios multiples"  # Los acentos se normalizan

    def test_format_message(self):
        """Test formateo de mensajes"""
        template = "Hola {nombre}, tu teléfono es {telefono}"
        data = {"nombre": "Juan", "telefono": "123456789"}
        result = utils.format_message(template, data)
        assert result == "Hola Juan, tu teléfono es 123456789"

        # Test con campo faltante
        template_missing = "Hola {nombre}, tu email es {email}"
        result_missing = utils.format_message(template_missing, data)
        assert result_missing == template_missing  # Debe retornar el template original

    def test_get_file_extension(self):
        """Test obtención de extensión de archivo"""
        assert utils.get_file_extension("archivo.csv") == "csv"
        assert utils.get_file_extension("archivo.xlsx") == "xlsx"
        assert utils.get_file_extension("archivo.TXT") == "txt"
        assert utils.get_file_extension("archivo") == ""

    def test_is_valid_file_type(self):
        """Test validación de tipos de archivo"""
        assert utils.is_valid_file_type("archivo.csv", ["csv", "xlsx"]) == True
        assert utils.is_valid_file_type("archivo.xlsx", ["csv", "xlsx"]) == True
        assert utils.is_valid_file_type("archivo.txt", ["csv", "xlsx"]) == False

    def test_safe_int(self):
        """Test conversión segura a entero"""
        assert utils.safe_int("123") == 123
        assert utils.safe_int("abc", 0) == 0
        assert utils.safe_int("", 10) == 10
        assert utils.safe_int(None, 5) == 5


class TestConfig:
    """Tests para el módulo config.py"""

    def test_config_constants(self):
        """Test que las constantes de configuración existan"""
        assert hasattr(config, 'WHATSAPP_WEB_URL')
        assert hasattr(config, 'DEFAULT_MESSAGE_LIMIT')
        assert hasattr(config, 'DEFAULT_DELAY_BETWEEN_MESSAGES')
        assert hasattr(config, 'CSV_REQUIRED_COLUMNS')
        assert hasattr(config, 'SELECTORS')

    def test_config_values(self):
        """Test valores de configuración"""
        assert config.WHATSAPP_WEB_URL == "https://web.whatsapp.com"
        assert config.DEFAULT_MESSAGE_LIMIT == 50
        assert config.DEFAULT_DELAY_BETWEEN_MESSAGES == 20
        assert "nombre" in config.CSV_REQUIRED_COLUMNS
        assert "telefono" in config.CSV_REQUIRED_COLUMNS

    def test_selectors_exist(self):
        """Test que los selectores CSS existan"""
        required_selectors = ["search_box", "message_box", "send_button", "qr_code"]
        for selector in required_selectors:
            assert selector in config.SELECTORS


class TestLogger:
    """Tests para el módulo logger.py"""

    def test_logger_functions_exist(self):
        """Test que las funciones de logging existan"""
        assert hasattr(logger, 'log_info')
        assert hasattr(logger, 'log_warning')
        assert hasattr(logger, 'log_error')
        assert hasattr(logger, 'log_debug')

    @patch('logger.logger_instance')
    def test_log_info(self, mock_logger):
        """Test función log_info"""
        logger.log_info("Test message")
        mock_logger.log_info.assert_called_once_with("Test message")

    @patch('logger.logger_instance')
    def test_log_error(self, mock_logger):
        """Test función log_error"""
        test_exception = Exception("Test error")
        logger.log_error("Error message", test_exception)
        mock_logger.log_error.assert_called_once_with("Error message", test_exception)

    @patch('logger.logger_instance')
    def test_log_message_sent(self, mock_logger):
        """Test función log_message_sent"""
        logger.log_message_sent("Juan", "123456789", "Hola", "ENVIADO")
        mock_logger.log_message_sent.assert_called_once_with("Juan", "123456789", "Hola", "ENVIADO", "")


class TestDataManager:
    """Tests para el módulo data_manager.py"""

    def setup_method(self):
        """Setup para cada test"""
        self.data_manager = DataManager()

    def create_test_csv(self, content):
        """Crea un archivo CSV temporal para testing"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    def test_load_valid_csv(self):
        """Test carga de CSV válido"""
        csv_content = '''nombre,telefono,mensaje
"Juan Pérez",5491123456789,"Hola {nombre}"
"María García",5491187654321,
'''
        csv_file = self.create_test_csv(csv_content)

        try:
            contacts = self.data_manager.load_contacts(csv_file)
            assert len(contacts) == 2
            assert contacts[0]['nombre'] == "Juan Pérez"
            assert contacts[0]['telefono'] == "5491123456789"
            assert contacts[1]['nombre'] == "María García"
        finally:
            os.unlink(csv_file)

    def test_load_nonexistent_file(self):
        """Test carga de archivo inexistente"""
        with pytest.raises(FileNotFoundError):
            self.data_manager.load_contacts("archivo_inexistente.csv")

    def test_load_invalid_csv_missing_columns(self):
        """Test carga de CSV con columnas faltantes"""
        csv_content = '''nombre
"Juan Pérez"
'''
        csv_file = self.create_test_csv(csv_content)

        try:
            with pytest.raises(ValueError, match="Faltan columnas requeridas"):
                self.data_manager.load_contacts(csv_file)
        finally:
            os.unlink(csv_file)

    def test_validate_contacts(self):
        """Test validación de contactos"""
        # Simular contactos cargados
        self.data_manager.contacts = [
            {"nombre": "Juan", "telefono": "5491123456789"},
            {"nombre": "", "telefono": "5491123456789"},  # Nombre vacío
            {"nombre": "María", "telefono": "123"},  # Teléfono inválido
        ]

        stats = self.data_manager.validate_contacts()
        assert stats['total'] == 3
        assert stats['valid'] == 1
        assert stats['empty_name'] == 1
        assert stats['invalid_phone'] == 1

    def test_filter_contacts(self):
        """Test filtrado de contactos"""
        self.data_manager.contacts = [
            {"nombre": "Juan", "telefono": "5491123456789"},
            {"nombre": "María", "telefono": "5491187654321"},
            {"nombre": "Carlos", "telefono": "5491156789012"},
        ]

        # Sin límite
        filtered = self.data_manager.filter_contacts()
        assert len(filtered) == 3

        # Con límite
        filtered = self.data_manager.filter_contacts(2)
        assert len(filtered) == 2
        assert filtered[0]['nombre'] == "Juan"
        assert filtered[1]['nombre'] == "María"

    def test_get_contact_count(self):
        """Test obtención del número de contactos"""
        assert self.data_manager.get_contact_count() == 0

        self.data_manager.contacts = [{"nombre": "Juan", "telefono": "123456789"}]
        assert self.data_manager.get_contact_count() == 1


class TestIntegration:
    """Tests de integración"""

    def test_full_data_loading_workflow(self):
        """Test del flujo completo de carga de datos"""
        csv_content = '''nombre,telefono,mensaje
"Juan Pérez",5491123456789,"Hola {nombre}, bienvenido"
"María García",5491187654321,
"Carlos López",123,"Mensaje para {nombre}"
"Ana Martínez",5491134567890,"¡Hola {nombre}!"
'''
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        csv_file.write(csv_content)
        csv_file.close()

        try:
            dm = DataManager()
            contacts = dm.load_contacts(csv_file.name)

            # Debe cargar 3 contactos válidos (Carlos tiene teléfono muy corto)
            assert len(contacts) == 3

            # Validar estadísticas
            stats = dm.validate_contacts()
            assert stats['valid'] == 3

            # Filtrar contactos
            filtered = dm.filter_contacts(2)
            assert len(filtered) == 2

        finally:
            os.unlink(csv_file.name)


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"])
