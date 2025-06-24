#!/usr/bin/env python3
"""
Launcher para el bot de WhatsApp - permite elegir entre CLI y GUI
"""

import sys
import os
import argparse
from pathlib import Path

def check_gui_dependencies():
    """Verifica si las dependencias de GUI están disponibles"""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def show_mode_selection():
    """Muestra menú para seleccionar modo de ejecución"""
    print("🤖 BOT DE WHATSAPP - SELECTOR DE MODO")
    print("=" * 50)
    print()
    print("Selecciona el modo de ejecución:")
    print()
    print("1. 🖥️  Interfaz Simple (Recomendado)")
    print("2. 🌐 Interfaz Web")
    print("3. 🖥️  Interfaz Gráfica (GUI)")
    print("4. ⌨️  Línea de Comandos (CLI)")
    print("5. 🧪 Ejecutar Tests")
    print("6. ❓ Mostrar Ayuda")
    print("7. 🚪 Salir")
    print()

    while True:
        try:
            choice = input("Ingresa tu opción (1-7): ").strip()

            if choice == "1":
                return "simple"
            elif choice == "2":
                return "web"
            elif choice == "3":
                return "gui"
            elif choice == "4":
                return "cli"
            elif choice == "5":
                return "test"
            elif choice == "6":
                return "help"
            elif choice == "7":
                return "exit"
            else:
                print("❌ Opción inválida. Ingresa un número del 1 al 7.")

        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            return "exit"

def launch_simple():
    """Lanza la interfaz simple"""
    try:
        print("🖥️  Iniciando interfaz simple...")
        import ultra_simple_gui
        ultra_simple_gui.main()
        return True
    except Exception as e:
        print(f"❌ Error iniciando interfaz simple: {e}")
        return False

def launch_web():
    """Lanza la interfaz web"""
    try:
        print("🌐 Iniciando interfaz web...")
        print("📱 Accede desde tu navegador a: http://localhost:5000")
        print("⏹️  Presiona Ctrl+C para detener el servidor")
        print()

        import web_interface
        web_interface.main()
        return True
    except Exception as e:
        print(f"❌ Error iniciando interfaz web: {e}")
        return False

def launch_gui():
    """Lanza la interfaz gráfica"""
    if not check_gui_dependencies():
        print("❌ Error: tkinter no está disponible")
        print("💡 Instala tkinter o usa la interfaz web")
        return False

    try:
        print("🚀 Iniciando interfaz gráfica...")
        import gui_main
        gui_main.main()
        return True
    except Exception as e:
        print(f"❌ Error iniciando GUI: {e}")
        return False

def launch_cli():
    """Lanza la interfaz de línea de comandos"""
    print("⌨️  Modo línea de comandos")
    print("💡 Usa: python main.py --help para ver opciones")
    print()

    # Mostrar ejemplo de uso
    print("📋 Ejemplo de uso:")
    print("python main.py --input contactos.csv --limit 10 --delay 30")
    print()

    # Preguntar si quiere ejecutar con parámetros
    response = input("¿Quieres ejecutar con parámetros personalizados? (s/N): ").lower()

    if response in ['s', 'si', 'sí', 'y', 'yes']:
        get_cli_params()
    else:
        print("💡 Ejecuta manualmente: python main.py --input tu_archivo.csv")

def get_cli_params():
    """Obtiene parámetros para CLI de forma interactiva"""
    try:
        # Archivo de entrada
        while True:
            file_path = input("📁 Archivo de contactos: ").strip()
            if file_path and Path(file_path).exists():
                break
            elif file_path == "":
                print("💡 Usando archivo de ejemplo...")
                file_path = "ejemplo_contactos.csv"
                break
            else:
                print("❌ Archivo no encontrado. Intenta de nuevo.")

        # Límite
        while True:
            try:
                limit = input("📊 Límite de mensajes (default: 50): ").strip()
                limit = int(limit) if limit else 50
                if 1 <= limit <= 1000:
                    break
                else:
                    print("❌ Límite debe estar entre 1 y 1000")
            except ValueError:
                print("❌ Ingresa un número válido")

        # Delay
        while True:
            try:
                delay = input("⏱️  Delay en segundos (default: 20): ").strip()
                delay = int(delay) if delay else 20
                if 5 <= delay <= 300:
                    break
                else:
                    print("❌ Delay debe estar entre 5 y 300 segundos")
            except ValueError:
                print("❌ Ingresa un número válido")

        # Ejecutar
        print(f"\n🚀 Ejecutando: python main.py --input {file_path} --limit {limit} --delay {delay}")

        import subprocess
        cmd = [sys.executable, "main.py", "--input", file_path, "--limit", str(limit), "--delay", str(delay)]
        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n❌ Cancelado por el usuario")

def run_tests():
    """Ejecuta los tests del sistema"""
    print("🧪 Ejecutando tests del sistema...")

    try:
        import subprocess

        # Ejecutar tests unitarios
        print("\n📋 Tests unitarios:")
        result = subprocess.run([sys.executable, "-m", "pytest", "test_whatsapp_bot.py", "-v"],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Tests unitarios: PASARON")
            lines = result.stdout.split('\n')
            summary_line = [line for line in lines if 'passed' in line and '=' in line]
            if summary_line:
                print(f"📊 {summary_line[-1].strip()}")
        else:
            print("❌ Tests unitarios: FALLARON")
            print(result.stderr[:200] + "..." if len(result.stderr) > 200 else result.stderr)

        print("\n💡 Para más tests detallados, revisa los archivos de validación")

    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")

def show_help():
    """Muestra información de ayuda"""
    print("❓ AYUDA - BOT DE WHATSAPP")
    print("=" * 50)
    print()
    print("📖 DESCRIPCIÓN:")
    print("Bot automatizado para enviar mensajes personalizados a través de WhatsApp Web")
    print()
    print("🎯 MODOS DE USO:")
    print()
    print("1. 🖥️  INTERFAZ GRÁFICA (Recomendado)")
    print("   - Interfaz visual fácil de usar")
    print("   - Selección de archivos con explorador")
    print("   - Progreso en tiempo real")
    print("   - Log de actividad integrado")
    print()
    print("2. ⌨️  LÍNEA DE COMANDOS")
    print("   - Para usuarios avanzados")
    print("   - Automatización y scripts")
    print("   - Uso: python main.py --input archivo.csv --limit 50 --delay 20")
    print()
    print("📋 FORMATO DE ARCHIVO:")
    print("   Columnas requeridas: nombre, telefono")
    print("   Columna opcional: mensaje")
    print("   Formatos soportados: CSV, Excel (.xlsx, .xls)")
    print()
    print("⚠️  REQUISITOS:")
    print("   - Google Chrome instalado")
    print("   - Conexión a Internet")
    print("   - Cuenta activa de WhatsApp")
    print()
    print("🔒 SEGURIDAD:")
    print("   - Usa delays apropiados (mín. 20 segundos)")
    print("   - Limita mensajes por sesión (máx. 50)")
    print("   - Respeta términos de servicio de WhatsApp")
    print()
    print("📞 SOPORTE:")
    print("   - Revisa README.md para documentación completa")
    print("   - Ejecuta tests para validar instalación")
    print()

def main():
    """Función principal del launcher"""
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        # Si hay argumentos, ejecutar directamente CLI
        if "--gui" in sys.argv:
            launch_gui()
        elif "--help" in sys.argv or "-h" in sys.argv:
            show_help()
        elif "--test" in sys.argv:
            run_tests()
        else:
            # Ejecutar main.py con los argumentos
            import main
            main.main()
        return

    # Mostrar selector de modo
    while True:
        mode = show_mode_selection()

        if mode == "simple":
            if launch_simple():
                break
            else:
                print("\n💡 Intentando con modo CLI...")
                launch_cli()
                break

        elif mode == "web":
            if launch_web():
                break
            else:
                print("\n💡 Intentando con interfaz simple...")
                if not launch_simple():
                    print("\n💡 Usando modo CLI...")
                    launch_cli()
                break

        elif mode == "gui":
            if launch_gui():
                break
            else:
                print("\n💡 Intentando con interfaz simple...")
                if not launch_simple():
                    print("\n💡 Usando modo CLI...")
                    launch_cli()
                break

        elif mode == "cli":
            launch_cli()
            break

        elif mode == "test":
            run_tests()
            input("\nPresiona Enter para continuar...")

        elif mode == "help":
            show_help()
            input("\nPresiona Enter para continuar...")

        elif mode == "exit":
            print("👋 ¡Hasta luego!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        print("💡 Intenta ejecutar: python main.py --help")
