"""
Gestor de datos para cargar contactos desde archivos Excel y CSV
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Union
import config
import utils
import logger


class DataManager:
    """
    Clase para gestionar la carga y procesamiento de datos de contactos.
    """

    def __init__(self):
        self.contacts = []
        self.file_path = None

    def load_contacts(self, file_path: Union[str, Path]) -> List[Dict]:
        """
        Carga contactos desde un archivo Excel o CSV.

        Args:
            file_path (Union[str, Path]): Ruta al archivo de contactos

        Returns:
            List[Dict]: Lista de contactos cargados

        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el archivo no tiene el formato correcto
        """
        self.file_path = Path(file_path)

        # Verificar que el archivo existe
        if not self.file_path.exists():
            error_msg = config.MESSAGES["file_not_found"].format(file=str(self.file_path))
            logger.log_error(error_msg)
            raise FileNotFoundError(error_msg)

        # Determinar el tipo de archivo y cargar
        file_extension = utils.get_file_extension(self.file_path)

        try:
            if file_extension in ['xlsx', 'xls']:
                df = self._load_excel_file()
            elif file_extension == 'csv':
                df = self._load_csv_file()
            else:
                raise ValueError(f"Tipo de archivo no soportado: {file_extension}")

            # Procesar y validar los datos
            self.contacts = self._process_dataframe(df)

            logger.log_info(config.MESSAGES["data_loaded"].format(count=len(self.contacts)))
            return self.contacts

        except Exception as e:
            logger.log_error(f"Error al cargar el archivo {self.file_path}", e)
            raise

    def _load_excel_file(self) -> pd.DataFrame:
        """
        Carga un archivo Excel.

        Returns:
            pd.DataFrame: DataFrame con los datos del archivo
        """
        logger.log_debug(f"Cargando archivo Excel: {self.file_path}")
        return pd.read_excel(self.file_path)

    def _load_csv_file(self) -> pd.DataFrame:
        """
        Carga un archivo CSV.

        Returns:
            pd.DataFrame: DataFrame con los datos del archivo
        """
        logger.log_debug(f"Cargando archivo CSV: {self.file_path}")

        # Intentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                return pd.read_csv(self.file_path, encoding=encoding)
            except UnicodeDecodeError:
                continue

        # Si ningún encoding funciona, usar el por defecto
        return pd.read_csv(self.file_path)

    def _process_dataframe(self, df: pd.DataFrame) -> List[Dict]:
        """
        Procesa el DataFrame y valida los datos.

        Args:
            df (pd.DataFrame): DataFrame con los datos crudos

        Returns:
            List[Dict]: Lista de contactos procesados

        Raises:
            ValueError: Si faltan columnas requeridas
        """
        # Verificar columnas requeridas
        missing_columns = [col for col in config.CSV_REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Faltan columnas requeridas: {missing_columns}")

        # Convertir a lista de diccionarios
        contacts = []

        for index, row in df.iterrows():
            try:
                contact = self._process_contact_row(row, int(index))
                if contact:
                    contacts.append(contact)
            except Exception as e:
                logger.log_warning(f"Error procesando fila {int(index) + 1}: {str(e)}")
                continue

        return contacts

    def _process_contact_row(self, row: pd.Series, index: int) -> Optional[Dict]:
        """
        Procesa una fila individual de contacto.

        Args:
            row (pd.Series): Fila del DataFrame
            index (int): Índice de la fila

        Returns:
            Optional[Dict]: Datos del contacto procesados o None si es inválido
        """
        # Extraer datos básicos
        nombre = str(row.get('nombre', '')).strip()
        telefono = str(row.get('telefono', '')).strip()

        # Validar nombre
        if not nombre or nombre.lower() in ['nan', 'none', '']:
            logger.log_warning(f"Fila {index + 1}: Nombre vacío o inválido")
            return None

        # Validar y formatear teléfono
        telefono_formateado = utils.format_phone_number(telefono)
        if not telefono_formateado:
            error_msg = config.MESSAGES["invalid_phone"].format(phone=telefono) + f" en fila {index + 1}"
            logger.log_warning(error_msg)
            return None

        # Crear objeto contacto
        contact = {
            'nombre': nombre,
            'telefono': telefono_formateado,
            'telefono_original': telefono,
            'fila': index + 1
        }

        # Agregar mensaje personalizado si existe
        mensaje_personalizado = row.get('mensaje', '')
        if pd.notna(mensaje_personalizado) and str(mensaje_personalizado).strip():
            contact['mensaje'] = str(mensaje_personalizado).strip()
        else:
            contact['mensaje'] = config.DEFAULT_MESSAGE_TEMPLATE

        # Agregar otros campos opcionales
        for col in row.index:
            if col not in ['nombre', 'telefono', 'mensaje']:
                value = row.get(col, '')
                if pd.notna(value) and str(value).strip():
                    contact[col] = str(value).strip()

        return contact

    def get_contacts(self) -> List[Dict]:
        """
        Obtiene la lista de contactos cargados.

        Returns:
            List[Dict]: Lista de contactos
        """
        return self.contacts

    def get_contact_count(self) -> int:
        """
        Obtiene el número de contactos cargados.

        Returns:
            int: Número de contactos
        """
        return len(self.contacts)

    def validate_contacts(self) -> Dict[str, int]:
        """
        Valida todos los contactos y retorna estadísticas.

        Returns:
            Dict[str, int]: Estadísticas de validación
        """
        stats = {
            'total': len(self.contacts),
            'valid': 0,
            'invalid_phone': 0,
            'empty_name': 0
        }

        for contact in self.contacts:
            if not contact.get('nombre'):
                stats['empty_name'] += 1
            elif not utils.validate_phone_number(contact.get('telefono', '')):
                stats['invalid_phone'] += 1
            else:
                stats['valid'] += 1

        return stats

    def filter_contacts(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Filtra los contactos aplicando un límite si se especifica.

        Args:
            limit (Optional[int]): Límite de contactos a retornar

        Returns:
            List[Dict]: Lista de contactos filtrados
        """
        if limit is None or limit <= 0:
            return self.contacts

        return self.contacts[:limit]

    def export_contacts(self, output_path: Union[str, Path],
                       format: str = 'csv') -> bool:
        """
        Exporta los contactos a un archivo.

        Args:
            output_path (Union[str, Path]): Ruta del archivo de salida
            format (str): Formato de exportación ('csv' o 'excel')

        Returns:
            bool: True si la exportación fue exitosa
        """
        try:
            df = pd.DataFrame(self.contacts)

            if format.lower() == 'csv':
                df.to_csv(output_path, index=False, encoding='utf-8')
            elif format.lower() in ['excel', 'xlsx']:
                df.to_excel(output_path, index=False)
            else:
                raise ValueError(f"Formato no soportado: {format}")

            logger.log_info(f"Contactos exportados a: {output_path}")
            return True

        except Exception as e:
            logger.log_error(f"Error al exportar contactos", e)
            return False
