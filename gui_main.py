#!/usr/bin/env python3
"""
Interfaz gráfica principal para el bot de WhatsApp
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import sys
from pathlib import Path
import time

# Importar módulos del bot
import config
import logger
from data_manager import DataManager
from whatsapp_client import WhatsAppClient
from message_sender import MessageSender


class WhatsAppBotGUI:
    """Interfaz gráfica para el bot de WhatsApp"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Bot de WhatsApp - Envío Automatizado")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.file_path = tk.StringVar()
        self.limit_var = tk.StringVar(value="50")
        self.delay_var = tk.StringVar(value="20")
        self.is_running = False
        self.bot_thread = None
        
        # Queue para comunicación entre threads
        self.message_queue = queue.Queue()
        
        # Componentes del bot
        self.data_manager = None
        self.whatsapp_client = None
        self.message_sender = None
        self.contacts = []
        
        # Crear interfaz
        self.create_widgets()
        self.setup_styles()
        
        # Iniciar procesamiento de mensajes
        self.process_queue()
    
    def setup_styles(self):
        """Configura los estilos de la interfaz"""
        style = ttk.Style()
        
        # Configurar tema
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Estilos personalizados
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="🤖 Bot de WhatsApp", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sección 1: Selección de archivo
        self.create_file_section(main_frame, 1)
        
        # Sección 2: Configuración
        self.create_config_section(main_frame, 2)
        
        # Sección 3: Información de contactos
        self.create_contacts_section(main_frame, 3)
        
        # Sección 4: Controles
        self.create_controls_section(main_frame, 4)
        
        # Sección 5: Log de actividad
        self.create_log_section(main_frame, 5)
        
        # Sección 6: Barra de progreso
        self.create_progress_section(main_frame, 6)
    
    def create_file_section(self, parent, row):
        """Crea la sección de selección de archivo"""
        # Frame para archivo
        file_frame = ttk.LabelFrame(parent, text="📁 Archivo de Contactos", padding="10")
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # Entrada de archivo
        ttk.Label(file_frame, text="Archivo:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=50)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Botón examinar
        ttk.Button(file_frame, text="Examinar", command=self.browse_file).grid(row=0, column=2)
        
        # Información del archivo
        self.file_info_label = ttk.Label(file_frame, text="Selecciona un archivo CSV o Excel")
        self.file_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
    
    def create_config_section(self, parent, row):
        """Crea la sección de configuración"""
        # Frame para configuración
        config_frame = ttk.LabelFrame(parent, text="⚙️ Configuración", padding="10")
        config_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Límite de mensajes
        ttk.Label(config_frame, text="Límite de mensajes:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        limit_spinbox = ttk.Spinbox(config_frame, from_=1, to=1000, textvariable=self.limit_var, width=10)
        limit_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Delay entre mensajes
        ttk.Label(config_frame, text="Delay (segundos):").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        delay_spinbox = ttk.Spinbox(config_frame, from_=5, to=120, textvariable=self.delay_var, width=10)
        delay_spinbox.grid(row=0, column=3, sticky=tk.W)
    
    def create_contacts_section(self, parent, row):
        """Crea la sección de información de contactos"""
        # Frame para contactos
        contacts_frame = ttk.LabelFrame(parent, text="👥 Información de Contactos", padding="10")
        contacts_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        contacts_frame.columnconfigure(1, weight=1)
        
        # Labels de información
        self.contacts_total_label = ttk.Label(contacts_frame, text="Total: 0")
        self.contacts_total_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.contacts_valid_label = ttk.Label(contacts_frame, text="Válidos: 0")
        self.contacts_valid_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        self.contacts_invalid_label = ttk.Label(contacts_frame, text="Inválidos: 0")
        self.contacts_invalid_label.grid(row=0, column=2, sticky=tk.W)
        
        # Botón para validar contactos
        self.validate_button = ttk.Button(contacts_frame, text="Validar Contactos", 
                                        command=self.validate_contacts, state='disabled')
        self.validate_button.grid(row=1, column=0, columnspan=3, pady=(10, 0))
    
    def create_controls_section(self, parent, row):
        """Crea la sección de controles"""
        # Frame para controles
        controls_frame = ttk.LabelFrame(parent, text="🎮 Controles", padding="10")
        controls_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botones principales
        self.start_button = ttk.Button(controls_frame, text="🚀 Iniciar Bot", 
                                     command=self.start_bot, state='disabled')
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(controls_frame, text="⏹️ Detener", 
                                    command=self.stop_bot, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.test_button = ttk.Button(controls_frame, text="🧪 Probar Conexión", 
                                    command=self.test_connection)
        self.test_button.grid(row=0, column=2)
        
        # Estado del bot
        self.status_label = ttk.Label(controls_frame, text="Estado: Listo", style='Success.TLabel')
        self.status_label.grid(row=1, column=0, columnspan=3, pady=(10, 0))
    
    def create_log_section(self, parent, row):
        """Crea la sección de log"""
        # Frame para log
        log_frame = ttk.LabelFrame(parent, text="📝 Log de Actividad", padding="10")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Área de texto para log
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights para que el log se expanda
        parent.rowconfigure(row, weight=1)
        
        # Botón para limpiar log
        ttk.Button(log_frame, text="Limpiar Log", command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
    
    def create_progress_section(self, parent, row):
        """Crea la sección de progreso"""
        # Frame para progreso
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Label de progreso
        self.progress_label = ttk.Label(progress_frame, text="0/0 (0%)")
        self.progress_label.grid(row=0, column=1)
    
    def browse_file(self):
        """Abre el diálogo para seleccionar archivo"""
        filetypes = [
            ('Archivos de contactos', '*.csv *.xlsx *.xls'),
            ('Archivos CSV', '*.csv'),
            ('Archivos Excel', '*.xlsx *.xls'),
            ('Todos los archivos', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de contactos",
            filetypes=filetypes
        )
        
        if filename:
            self.file_path.set(filename)
            self.load_file_info()
    
    def load_file_info(self):
        """Carga información del archivo seleccionado"""
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            return
        
        try:
            # Obtener información del archivo
            file_size = os.path.getsize(file_path) / 1024  # KB
            file_ext = Path(file_path).suffix.lower()
            
            info_text = f"📄 {Path(file_path).name} ({file_size:.1f} KB, {file_ext})"
            self.file_info_label.config(text=info_text)
            
            # Habilitar botón de validación
            self.validate_button.config(state='normal')
            
            self.log_message(f"Archivo seleccionado: {Path(file_path).name}")
            
        except Exception as e:
            self.log_message(f"Error al leer archivo: {e}", "ERROR")
    
    def validate_contacts(self):
        """Valida los contactos del archivo"""
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Selecciona un archivo primero")
            return
        
        try:
            self.log_message("Validando contactos...")
            
            # Cargar contactos
            self.data_manager = DataManager()
            self.contacts = self.data_manager.load_contacts(file_path)
            
            # Obtener estadísticas
            stats = self.data_manager.validate_contacts()
            
            # Actualizar labels
            self.contacts_total_label.config(text=f"Total: {stats['total']}")
            self.contacts_valid_label.config(text=f"Válidos: {stats['valid']}")
            self.contacts_invalid_label.config(text=f"Inválidos: {stats['total'] - stats['valid']}")
            
            # Habilitar botón de inicio si hay contactos válidos
            if stats['valid'] > 0:
                self.start_button.config(state='normal')
                self.log_message(f"✅ Validación exitosa: {stats['valid']} contactos válidos")
            else:
                self.log_message("❌ No se encontraron contactos válidos", "ERROR")
            
        except Exception as e:
            self.log_message(f"Error validando contactos: {e}", "ERROR")
            messagebox.showerror("Error", f"Error al validar contactos:\n{e}")
    
    def test_connection(self):
        """Prueba la conexión a WhatsApp Web"""
        def test_thread():
            try:
                self.log_message("🔍 Probando conexión a WhatsApp Web...")
                
                # Crear cliente temporal
                test_client = WhatsAppClient()
                
                # Intentar iniciar navegador
                if test_client.start_browser():
                    self.message_queue.put(("log", "✅ Chrome iniciado correctamente"))
                    self.message_queue.put(("log", "✅ WhatsApp Web cargado"))
                    self.message_queue.put(("status", "Conexión exitosa", "success"))
                    
                    # Esperar un poco y cerrar
                    time.sleep(3)
                    test_client.close_browser()
                    self.message_queue.put(("log", "🔒 Navegador cerrado"))
                else:
                    self.message_queue.put(("log", "❌ Error iniciando Chrome", "ERROR"))
                    self.message_queue.put(("status", "Error de conexión", "error"))
                    
            except Exception as e:
                self.message_queue.put(("log", f"❌ Error en prueba: {e}", "ERROR"))
                self.message_queue.put(("status", "Error de conexión", "error"))
        
        # Ejecutar en thread separado
        threading.Thread(target=test_thread, daemon=True).start()
    
    def start_bot(self):
        """Inicia el bot de WhatsApp"""
        if self.is_running:
            return
        
        # Validar configuración
        if not self.contacts:
            messagebox.showerror("Error", "Valida los contactos primero")
            return
        
        try:
            limit = int(self.limit_var.get())
            delay = int(self.delay_var.get())
        except ValueError:
            messagebox.showerror("Error", "Límite y delay deben ser números")
            return
        
        # Confirmar inicio
        result = messagebox.askyesno(
            "Confirmar",
            f"¿Iniciar bot con {limit} mensajes y {delay}s de delay?\n\n"
            "Asegúrate de tener tu teléfono listo para escanear el código QR."
        )
        
        if not result:
            return
        
        # Iniciar bot en thread separado
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.validate_button.config(state='disabled')
        
        self.bot_thread = threading.Thread(
            target=self.run_bot_thread,
            args=(limit, delay),
            daemon=True
        )
        self.bot_thread.start()
    
    def run_bot_thread(self, limit, delay):
        """Ejecuta el bot en un thread separado"""
        try:
            self.message_queue.put(("status", "Iniciando bot...", "info"))
            self.message_queue.put(("log", "🚀 Iniciando bot de WhatsApp..."))
            
            # Crear cliente de WhatsApp
            self.whatsapp_client = WhatsAppClient()
            
            # Iniciar navegador
            self.message_queue.put(("log", "🌐 Iniciando navegador..."))
            if not self.whatsapp_client.start_browser():
                raise Exception("Error iniciando navegador")
            
            self.message_queue.put(("log", "✅ Navegador iniciado"))
            
            # Esperar escaneo QR
            self.message_queue.put(("log", "📱 Esperando escaneo de código QR..."))
            self.message_queue.put(("status", "Esperando código QR", "info"))
            
            if not self.whatsapp_client.wait_for_qr_scan():
                raise Exception("Timeout esperando código QR")
            
            self.message_queue.put(("log", "✅ Código QR escaneado"))
            self.message_queue.put(("status", "Enviando mensajes...", "info"))
            
            # Enviar mensajes
            self.message_sender = MessageSender(self.whatsapp_client)
            contacts_to_send = self.data_manager.filter_contacts(limit)
            
            # Configurar callback para progreso
            self.setup_progress_callback()
            
            stats = self.message_sender.send_messages_to_contacts(
                contacts_to_send, limit, delay
            )
            
            # Mostrar resultados
            self.message_queue.put(("log", f"✅ Envío completado: {stats.messages_sent}/{stats.total_contacts}"))
            self.message_queue.put(("status", f"Completado: {stats.messages_sent} enviados", "success"))
            
        except Exception as e:
            self.message_queue.put(("log", f"❌ Error: {e}", "ERROR"))
            self.message_queue.put(("status", "Error en ejecución", "error"))
        
        finally:
            # Limpiar
            if hasattr(self, 'whatsapp_client') and self.whatsapp_client:
                self.whatsapp_client.close_browser()
            
            self.message_queue.put(("bot_finished", None))
    
    def setup_progress_callback(self):
        """Configura callback para actualizar progreso"""
        # Esta función se llamaría desde message_sender para actualizar progreso
        # Por simplicidad, usaremos el queue para comunicación
        pass
    
    def stop_bot(self):
        """Detiene el bot"""
        if not self.is_running:
            return
        
        self.log_message("⏹️ Deteniendo bot...")
        
        # Detener message sender si existe
        if hasattr(self, 'message_sender') and self.message_sender:
            self.message_sender.stop_sending()
        
        # Cerrar navegador si existe
        if hasattr(self, 'whatsapp_client') and self.whatsapp_client:
            self.whatsapp_client.close_browser()
        
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.validate_button.config(state='normal')
        
        self.update_status("Detenido", "warning")
    
    def log_message(self, message, level="INFO"):
        """Agrega un mensaje al log"""
        timestamp = time.strftime("%H:%M:%S")
        
        # Agregar emoji según el nivel
        if level == "ERROR":
            prefix = "❌"
        elif level == "WARNING":
            prefix = "⚠️"
        elif level == "SUCCESS":
            prefix = "✅"
        else:
            prefix = "ℹ️"
        
        formatted_message = f"[{timestamp}] {prefix} {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Limpia el log"""
        self.log_text.delete(1.0, tk.END)
    
    def update_status(self, message, level="info"):
        """Actualiza el estado del bot"""
        if level == "success":
            style = 'Success.TLabel'
        elif level == "error":
            style = 'Error.TLabel'
        elif level == "warning":
            style = 'Warning.TLabel'
        else:
            style = 'TLabel'
        
        self.status_label.config(text=f"Estado: {message}", style=style)
    
    def update_progress(self, current, total):
        """Actualiza la barra de progreso"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            self.progress_label.config(text=f"{current}/{total} ({percentage:.1f}%)")
        else:
            self.progress_var.set(0)
            self.progress_label.config(text="0/0 (0%)")
    
    def process_queue(self):
        """Procesa mensajes del queue"""
        try:
            while True:
                message_type, data, *args = self.message_queue.get_nowait()
                
                if message_type == "log":
                    level = args[0] if args else "INFO"
                    self.log_message(data, level)
                
                elif message_type == "status":
                    level = args[0] if args else "info"
                    self.update_status(data, level)
                
                elif message_type == "progress":
                    current, total = data
                    self.update_progress(current, total)
                
                elif message_type == "bot_finished":
                    self.is_running = False
                    self.start_button.config(state='normal')
                    self.stop_button.config(state='disabled')
                    self.validate_button.config(state='normal')
                
        except queue.Empty:
            pass
        
        # Programar siguiente verificación
        self.root.after(100, self.process_queue)


def main():
    """Función principal"""
    root = tk.Tk()
    app = WhatsAppBotGUI(root)
    
    # Configurar cierre de ventana
    def on_closing():
        if app.is_running:
            if messagebox.askokcancel("Salir", "El bot está ejecutándose. ¿Detener y salir?"):
                app.stop_bot()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Iniciar aplicación
    root.mainloop()


if __name__ == "__main__":
    main()
