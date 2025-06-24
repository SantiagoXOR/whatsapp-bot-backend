#!/usr/bin/env python3
"""
Interfaz ultra-simple para el bot de WhatsApp usando solo módulos estándar
"""

import os
import sys
import csv
import subprocess
from pathlib import Path


class UltraSimpleInterface:
    """Interfaz ultra-simple para el bot de WhatsApp"""
    
    def __init__(self):
        self.contacts_file = None
        self.contacts_count = 0
        self.limit = 50
        self.delay = 20
    
    def clear_screen(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Muestra el encabezado"""
        print("🤖 BOT DE WHATSAPP - INTERFAZ ULTRA-SIMPLE")
        print("=" * 55)
        print()
    
    def show_menu(self):
        """Muestra el menú principal"""
        self.clear_screen()
        self.show_header()
        
        print("📋 MENÚ PRINCIPAL")
        print("-" * 30)
        print("1. 📁 Seleccionar archivo de contactos")
        print("2. ⚙️  Configurar parámetros")
        print("3. 🚀 Ejecutar bot")
        print("4. 🧪 Probar conexión (solo Chrome)")
        print("5. 📝 Ver archivos de ejemplo")
        print("6. ❓ Ayuda")
        print("7. 🚪 Salir")
        print()
        
        # Mostrar estado actual
        if self.contacts_file:
            print(f"📊 Archivo: {Path(self.contacts_file).name}")
            print(f"📈 Contactos: {self.contacts_count}")
        else:
            print("📊 Sin archivo seleccionado")
        
        print(f"⚙️  Configuración: Límite={self.limit}, Delay={self.delay}s")
        print()
    
    def select_file(self):
        """Selecciona archivo de contactos"""
        self.clear_screen()
        self.show_header()
        
        print("📁 SELECCIONAR ARCHIVO DE CONTACTOS")
        print("-" * 40)
        
        # Buscar archivos CSV en el directorio actual
        current_dir = Path('.')
        csv_files = list(current_dir.glob('*.csv'))
        
        if csv_files:
            print("📄 Archivos CSV encontrados:")
            for i, file in enumerate(csv_files, 1):
                print(f"  {i}. {file.name}")
            print()
            
            try:
                choice = input("Selecciona un archivo (número) o presiona Enter para escribir ruta: ").strip()
                
                if choice.isdigit():
                    file_num = int(choice) - 1
                    if 0 <= file_num < len(csv_files):
                        self.contacts_file = str(csv_files[file_num])
                        self.count_contacts()
                        print(f"✅ Archivo seleccionado: {Path(self.contacts_file).name}")
                    else:
                        print("❌ Número inválido")
                elif choice == "":
                    file_path = input("Escribe la ruta completa del archivo: ").strip()
                    if file_path and Path(file_path).exists():
                        self.contacts_file = file_path
                        self.count_contacts()
                        print(f"✅ Archivo seleccionado: {Path(self.contacts_file).name}")
                    else:
                        print("❌ Archivo no encontrado")
                
            except ValueError:
                print("❌ Entrada inválida")
        else:
            print("❌ No se encontraron archivos CSV en el directorio actual")
            print()
            file_path = input("Escribe la ruta completa del archivo CSV: ").strip()
            if file_path and Path(file_path).exists():
                self.contacts_file = file_path
                self.count_contacts()
                print(f"✅ Archivo seleccionado: {Path(self.contacts_file).name}")
            else:
                print("❌ Archivo no encontrado")
        
        input("\nPresiona Enter para continuar...")
    
    def count_contacts(self):
        """Cuenta los contactos en el archivo"""
        try:
            with open(self.contacts_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.contacts_count = sum(1 for row in reader)
            print(f"📊 Se encontraron {self.contacts_count} contactos")
        except Exception as e:
            print(f"❌ Error leyendo archivo: {e}")
            self.contacts_count = 0
    
    def configure_parameters(self):
        """Configura parámetros"""
        self.clear_screen()
        self.show_header()
        
        print("⚙️ CONFIGURAR PARÁMETROS")
        print("-" * 30)
        
        print(f"Configuración actual:")
        print(f"  Límite de mensajes: {self.limit}")
        print(f"  Delay entre mensajes: {self.delay} segundos")
        print()
        
        try:
            # Límite
            limit_input = input(f"Nuevo límite (1-1000, actual: {self.limit}): ").strip()
            if limit_input:
                new_limit = int(limit_input)
                if 1 <= new_limit <= 1000:
                    self.limit = new_limit
                    print(f"✅ Límite actualizado: {self.limit}")
                else:
                    print("❌ Límite debe estar entre 1 y 1000")
            
            # Delay
            delay_input = input(f"Nuevo delay (5-300s, actual: {self.delay}): ").strip()
            if delay_input:
                new_delay = int(delay_input)
                if 5 <= new_delay <= 300:
                    self.delay = new_delay
                    print(f"✅ Delay actualizado: {self.delay}s")
                else:
                    print("❌ Delay debe estar entre 5 y 300 segundos")
        
        except ValueError:
            print("❌ Ingresa números válidos")
        
        input("\nPresiona Enter para continuar...")
    
    def execute_bot(self):
        """Ejecuta el bot"""
        if not self.contacts_file:
            print("❌ Selecciona un archivo de contactos primero")
            input("Presiona Enter para continuar...")
            return
        
        self.clear_screen()
        self.show_header()
        
        print("🚀 EJECUTAR BOT")
        print("-" * 30)
        
        print(f"📊 Configuración:")
        print(f"  Archivo: {Path(self.contacts_file).name}")
        print(f"  Contactos: {self.contacts_count}")
        print(f"  Límite: {self.limit}")
        print(f"  Delay: {self.delay}s")
        print()
        
        print("⚠️  IMPORTANTE:")
        print("  - Se abrirá Chrome con WhatsApp Web")
        print("  - Escanea el código QR con tu teléfono")
        print("  - El bot enviará mensajes automáticamente")
        print("  - Presiona Ctrl+C para detener")
        print()
        
        confirm = input("¿Continuar? (s/N): ").lower()
        if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
            return
        
        # Ejecutar el bot usando main.py
        try:
            print("\n🚀 Iniciando bot...")
            cmd = [
                sys.executable, "main.py",
                "--input", self.contacts_file,
                "--limit", str(self.limit),
                "--delay", str(self.delay)
            ]
            
            print(f"Ejecutando: {' '.join(cmd)}")
            print("=" * 50)
            
            # Ejecutar el comando
            subprocess.run(cmd)
            
        except KeyboardInterrupt:
            print("\n❌ Ejecución interrumpida por el usuario")
        except Exception as e:
            print(f"\n❌ Error ejecutando bot: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def test_chrome(self):
        """Prueba si Chrome está disponible"""
        self.clear_screen()
        self.show_header()
        
        print("🧪 PROBAR CHROME")
        print("-" * 30)
        
        print("🔍 Verificando si Google Chrome está instalado...")
        
        # Rutas comunes de Chrome
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
        
        chrome_found = False
        for path in chrome_paths:
            if Path(path).exists():
                print(f"✅ Chrome encontrado en: {path}")
                chrome_found = True
                break
        
        if not chrome_found:
            # Intentar ejecutar desde PATH
            try:
                result = subprocess.run(["chrome", "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ Chrome encontrado en PATH: {result.stdout.strip()}")
                    chrome_found = True
            except:
                try:
                    result = subprocess.run(["google-chrome", "--version"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        print(f"✅ Chrome encontrado en PATH: {result.stdout.strip()}")
                        chrome_found = True
                except:
                    pass
        
        if chrome_found:
            print("\n✅ Chrome está disponible")
            print("💡 El bot debería funcionar correctamente")
        else:
            print("\n❌ Chrome no encontrado")
            print("📥 Descarga Chrome desde: https://www.google.com/chrome/")
            print("⚠️  El bot no funcionará sin Chrome")
        
        input("\nPresiona Enter para continuar...")
    
    def show_examples(self):
        """Muestra archivos de ejemplo"""
        self.clear_screen()
        self.show_header()
        
        print("📝 ARCHIVOS DE EJEMPLO")
        print("-" * 30)
        
        # Verificar si existe ejemplo_contactos.csv
        example_file = Path("ejemplo_contactos.csv")
        if example_file.exists():
            print("✅ Archivo de ejemplo encontrado: ejemplo_contactos.csv")
            print()
            
            try:
                print("📋 Contenido del archivo de ejemplo:")
                with open(example_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines[:6], 1):  # Mostrar primeras 6 líneas
                        print(f"  {i:2d}: {line.strip()}")
                    
                    if len(lines) > 6:
                        print(f"  ... y {len(lines) - 6} líneas más")
                
            except Exception as e:
                print(f"❌ Error leyendo archivo: {e}")
        else:
            print("❌ No se encontró ejemplo_contactos.csv")
        
        print()
        print("📖 FORMATO REQUERIDO:")
        print("  - Archivo CSV con columnas: nombre,telefono,mensaje")
        print("  - nombre: Nombre del contacto (obligatorio)")
        print("  - telefono: Número internacional sin '+' (obligatorio)")
        print("  - mensaje: Mensaje personalizado (opcional)")
        print()
        print("📝 Ejemplo de formato:")
        print('  nombre,telefono,mensaje')
        print('  "Juan Pérez",5491123456789,"Hola {nombre}, mensaje de prueba"')
        print('  "María García",5491187654321,')
        
        input("\nPresiona Enter para continuar...")
    
    def show_help(self):
        """Muestra ayuda"""
        self.clear_screen()
        self.show_header()
        
        print("❓ AYUDA")
        print("-" * 30)
        print()
        print("📖 PASOS PARA USAR EL BOT:")
        print()
        print("1. 📁 Seleccionar archivo de contactos")
        print("   - Debe ser un archivo CSV")
        print("   - Columnas: nombre, telefono, mensaje (opcional)")
        print("   - Números en formato internacional: 5491123456789")
        print()
        print("2. ⚙️ Configurar parámetros")
        print("   - Límite: máximo de mensajes a enviar")
        print("   - Delay: segundos entre mensajes (mín. 20 recomendado)")
        print()
        print("3. 🚀 Ejecutar bot")
        print("   - Se abrirá Chrome automáticamente")
        print("   - Escanea el código QR con tu teléfono")
        print("   - El bot enviará mensajes automáticamente")
        print()
        print("⚠️  REQUISITOS:")
        print("   - Google Chrome instalado")
        print("   - Conexión a Internet")
        print("   - Cuenta activa de WhatsApp")
        print()
        print("🔒 RECOMENDACIONES:")
        print("   - Usa delays de al menos 20 segundos")
        print("   - Limita mensajes por sesión (máx. 50)")
        print("   - Prueba con pocos contactos primero")
        print("   - Respeta términos de servicio de WhatsApp")
        
        input("\nPresiona Enter para continuar...")
    
    def run(self):
        """Ejecuta la interfaz"""
        while True:
            self.show_menu()
            
            choice = input("Selecciona una opción (1-7): ").strip()
            
            if choice == "1":
                self.select_file()
            elif choice == "2":
                self.configure_parameters()
            elif choice == "3":
                self.execute_bot()
            elif choice == "4":
                self.test_chrome()
            elif choice == "5":
                self.show_examples()
            elif choice == "6":
                self.show_help()
            elif choice == "7":
                print("\n👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
                input("Presiona Enter para continuar...")


def main():
    """Función principal"""
    try:
        interface = UltraSimpleInterface()
        interface.run()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")


if __name__ == "__main__":
    main()
