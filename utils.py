"""
Funciones auxiliares para el bot de WhatsApp
"""

import re
import os
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
import config


def validate_phone_number(phone: str) -> bool:
    """
    Valida si un número de teléfono tiene el formato correcto.

    Args:
        phone (str): Número de teléfono a validar

    Returns:
        bool: True si el número es válido, False en caso contrario
    """
    if not phone or not isinstance(phone, str):
        return False

    # Remover espacios y caracteres especiales, mantener solo dígitos
    clean_phone = re.sub(r'[^\d]', '', phone)

    # Verificar que el teléfono original contenía al menos algunos dígitos
    if not clean_phone:
        return False

    # Verificar longitud
    if len(clean_phone) < config.PHONE_NUMBER_MIN_LENGTH or len(clean_phone) > config.PHONE_NUMBER_MAX_LENGTH:
        return False

    # Verificar que solo contenga dígitos
    return clean_phone.isdigit()


def format_phone_number(phone: str) -> Optional[str]:
    """
    Formatea un número de teléfono removiendo caracteres especiales.

    Args:
        phone (str): Número de teléfono a formatear

    Returns:
        Optional[str]: Número formateado o None si es inválido
    """
    if not validate_phone_number(phone):
        return None

    # Remover todos los caracteres que no sean dígitos
    clean_phone = re.sub(r'[^\d]', '', phone)
    return clean_phone


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo removiendo caracteres especiales.

    Args:
        filename (str): Nombre de archivo a sanitizar

    Returns:
        str: Nombre de archivo sanitizado
    """
    # Normalizar unicode
    filename = unicodedata.normalize('NFKD', filename)

    # Remover caracteres especiales (mantener letras, números, espacios, guiones y puntos)
    filename = re.sub(r'[^\w\s.\-]', '', filename)

    # Reemplazar espacios múltiples con uno solo
    filename = re.sub(r'\s+', ' ', filename)

    # Remover espacios al inicio y final
    filename = filename.strip()

    return filename


def get_timestamp() -> str:
    """
    Obtiene una marca de tiempo formateada.

    Returns:
        str: Marca de tiempo en formato YYYY-MM-DD HH:MM:SS
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_timestamp_filename() -> str:
    """
    Obtiene una marca de tiempo para nombres de archivo.

    Returns:
        str: Marca de tiempo en formato YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """
    Asegura que un directorio exista, creándolo si es necesario.

    Args:
        directory (Union[str, Path]): Ruta del directorio

    Returns:
        Path: Objeto Path del directorio
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def file_exists(file_path: Union[str, Path]) -> bool:
    """
    Verifica si un archivo existe.

    Args:
        file_path (Union[str, Path]): Ruta del archivo

    Returns:
        bool: True si el archivo existe, False en caso contrario
    """
    return Path(file_path).exists()


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Obtiene la extensión de un archivo.

    Args:
        file_path (Union[str, Path]): Ruta del archivo

    Returns:
        str: Extensión del archivo (sin el punto)
    """
    return Path(file_path).suffix.lower().lstrip('.')


def format_message(template: str, contact_data: dict) -> str:
    """
    Formatea un mensaje usando los datos del contacto.

    Args:
        template (str): Plantilla del mensaje con placeholders
        contact_data (dict): Datos del contacto

    Returns:
        str: Mensaje formateado
    """
    try:
        return template.format(**contact_data)
    except KeyError as e:
        # Si falta algún campo, usar el template original
        return template


def truncate_string(text: str, max_length: int = 100) -> str:
    """
    Trunca una cadena si excede la longitud máxima.

    Args:
        text (str): Texto a truncar
        max_length (int): Longitud máxima

    Returns:
        str: Texto truncado
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def is_valid_file_type(file_path: Union[str, Path], allowed_extensions: list) -> bool:
    """
    Verifica si un archivo tiene una extensión permitida.

    Args:
        file_path (Union[str, Path]): Ruta del archivo
        allowed_extensions (list): Lista de extensiones permitidas

    Returns:
        bool: True si la extensión es válida, False en caso contrario
    """
    extension = get_file_extension(file_path)
    return extension in [ext.lower() for ext in allowed_extensions]


def safe_int(value: str, default: int = 0) -> int:
    """
    Convierte un valor a entero de forma segura.

    Args:
        value (str): Valor a convertir
        default (int): Valor por defecto si la conversión falla

    Returns:
        int: Valor convertido o valor por defecto
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: str, default: float = 0.0) -> float:
    """
    Convierte un valor a float de forma segura.

    Args:
        value (str): Valor a convertir
        default (float): Valor por defecto si la conversión falla

    Returns:
        float: Valor convertido o valor por defecto
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
