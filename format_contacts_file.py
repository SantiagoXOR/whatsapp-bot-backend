#!/usr/bin/env python3
"""
Script para formatear automáticamente archivos de contactos
Detecta y corrige problemas comunes de formato y codificación
"""

import pandas as pd
import re
from pathlib import Path
import sys

def clean_phone_number(phone):
    """Limpia y formatea números de teléfono"""
    if pd.isna(phone):
        return ""
    
    # Convertir a string y limpiar
    phone = str(phone).strip()
    
    # Remover caracteres no numéricos excepto +
    phone = re.sub(r'[^\d+]', '', phone)
    
    # Si no tiene código de país, agregar +57 (Colombia)
    if phone and not phone.startswith('+'):
        if len(phone) == 10:  # Número colombiano sin código
            phone = '+57' + phone
        elif len(phone) == 13 and phone.startswith('57'):  # 57XXXXXXXXXX
            phone = '+' + phone
    
    return phone

def clean_name(name):
    """Limpia nombres"""
    if pd.isna(name):
        return ""
    
    name = str(name).strip()
    # Remover caracteres extraños pero mantener letras, espacios y acentos
    name = re.sub(r'[^\w\sáéíóúñÁÉÍÓÚÑ]', '', name)
    return name.title()  # Capitalizar

def detect_columns(df):
    """Detecta automáticamente las columnas de nombre y teléfono"""
    columns = df.columns.tolist()
    
    # Buscar columna de nombre
    name_col = None
    for col in columns:
        col_lower = str(col).lower()
        if any(word in col_lower for word in ['nombre', 'name', 'client', 'contact']):
            name_col = col
            break
    
    # Buscar columna de teléfono
    phone_col = None
    for col in columns:
        col_lower = str(col).lower()
        if any(word in col_lower for word in ['telefono', 'phone', 'tel', 'celular', 'movil']):
            phone_col = col
            break
    
    # Si no encuentra por nombre, usar las primeras columnas
    if not name_col and len(columns) > 0:
        name_col = columns[0]
    if not phone_col and len(columns) > 1:
        phone_col = columns[1]
    
    return name_col, phone_col

def format_contacts_file(input_file, output_file=None):
    """Formatea un archivo de contactos"""
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ Error: El archivo {input_file} no existe")
        return False
    
    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_formateado.xlsx"
    
    print(f"📁 Procesando archivo: {input_file}")
    
    try:
        # Intentar leer el archivo con diferentes métodos
        df = None
        
        # Método 1: Leer Excel directamente
        try:
            df = pd.read_excel(input_file)
            print("✅ Archivo leído como Excel")
        except Exception as e:
            print(f"⚠️  Error leyendo como Excel: {e}")
        
        # Método 2: Intentar diferentes encodings si es CSV
        if df is None:
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    df = pd.read_csv(input_file, encoding=encoding)
                    print(f"✅ Archivo leído como CSV con encoding {encoding}")
                    break
                except:
                    continue
        
        if df is None:
            print("❌ No se pudo leer el archivo con ningún método")
            return False
        
        print(f"📊 Datos originales: {len(df)} filas, {len(df.columns)} columnas")
        print(f"📋 Columnas encontradas: {list(df.columns)}")
        
        # Detectar columnas
        name_col, phone_col = detect_columns(df)
        print(f"🔍 Columna de nombre detectada: {name_col}")
        print(f"🔍 Columna de teléfono detectada: {phone_col}")
        
        if not name_col or not phone_col:
            print("❌ No se pudieron detectar las columnas necesarias")
            return False
        
        # Crear DataFrame limpio
        clean_data = []
        
        for index, row in df.iterrows():
            name = clean_name(row[name_col])
            phone = clean_phone_number(row[phone_col])
            
            # Solo agregar si tiene nombre y teléfono válidos
            if name and phone and len(phone) >= 10:
                clean_data.append({
                    'nombre': name,
                    'telefono': phone,
                    'mensaje': ''  # Columna vacía para mensajes personalizados
                })
        
        if not clean_data:
            print("❌ No se encontraron datos válidos después de la limpieza")
            return False
        
        # Crear nuevo DataFrame
        clean_df = pd.DataFrame(clean_data)
        
        # Guardar archivo formateado
        clean_df.to_excel(output_file, index=False)
        
        print(f"✅ Archivo formateado guardado: {output_file}")
        print(f"📊 Contactos válidos: {len(clean_data)}")
        print("\n📋 Primeros 3 contactos:")
        for i, contact in enumerate(clean_data[:3]):
            print(f"  {i+1}. {contact['nombre']} - {contact['telefono']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python format_contacts_file.py <archivo_entrada> [archivo_salida]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = format_contacts_file(input_file, output_file)
    sys.exit(0 if success else 1)
