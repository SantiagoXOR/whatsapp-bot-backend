#!/usr/bin/env python3
"""
Interfaz web moderna para el bot de WhatsApp
Inspirada en shadcn/ui con Flask + SocketIO
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import json
import threading
import time
from pathlib import Path
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Importar módulos del bot
from data_manager import DataManager
from main import WhatsAppBot
import config
import logger

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'whatsapp_bot_secret_key')
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
CORS(app, origins=["*"])

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Variables globales para el estado del bot
bot_instance = None
bot_running = False
current_stats = {
    'total_contacts': 0,
    'messages_sent': 0,
    'current_contact': '',
    'status': 'idle'
}

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Página principal - Estado del backend"""
    return jsonify({
        'status': 'running',
        'service': 'WhatsApp Bot Backend',
        'version': '3.0.0',
        'endpoints': {
            'upload': '/api/upload',
            'files': '/api/files',
            'validate': '/api/validate-file/<filename>',
            'preview': '/api/contacts/preview/<filename>'
        },
        'websocket': 'Socket.IO enabled',
        'message': 'Backend funcionando correctamente'
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'whatsapp-bot-backend'
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Endpoint para subir archivos de contactos"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Validar el archivo
            try:
                dm = DataManager()
                contacts = dm.load_contacts(filepath)
                
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'filepath': filepath,
                    'contact_count': len(contacts),
                    'preview': contacts[:5]  # Primeros 5 contactos para preview
                })
            except Exception as e:
                return jsonify({'success': False, 'error': f'Error al procesar archivo: {str(e)}'})
        else:
            return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/contacts/preview/<filename>')
def preview_contacts(filename):
    """Obtener preview de contactos de un archivo"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Archivo no encontrado'})
        
        dm = DataManager()
        contacts = dm.load_contacts(filepath)
        
        return jsonify({
            'success': True,
            'total_contacts': len(contacts),
            'preview': contacts[:10]  # Primeros 10 contactos
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/files')
def list_files():
    """Listar archivos disponibles en la carpeta data"""
    try:
        data_dir = Path(app.config['UPLOAD_FOLDER'])
        files = []
        
        for file_path in data_dir.glob('*'):
            if file_path.is_file() and allowed_file(file_path.name):
                try:
                    dm = DataManager()
                    contacts = dm.load_contacts(str(file_path))
                    files.append({
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'contact_count': len(contacts),
                        'modified': file_path.stat().st_mtime
                    })
                except:
                    files.append({
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'contact_count': 0,
                        'modified': file_path.stat().st_mtime,
                        'error': True
                    })
        
        return jsonify({'success': True, 'files': files})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

class BotRunner:
    """Clase para ejecutar el bot con updates en tiempo real"""

    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
        self.bot_instance = None
        self.running = False
        self.stats = {
            'total_contacts': 0,
            'messages_sent': 0,
            'current_contact': '',
            'status': 'idle'
        }

    def emit_update(self, event, data):
        """Emitir actualización via SocketIO"""
        self.socketio.emit(event, data)

    def run_bot(self, filepath, limit, delay, message_template):
        """Ejecutar el bot con monitoreo en tiempo real"""
        try:
            self.running = True
            self.stats['status'] = 'starting'
            self.emit_update('status_update', {'message': 'Iniciando bot...', 'stats': self.stats})

            # Cargar contactos
            self.emit_update('status_update', {'message': 'Cargando contactos...', 'stats': self.stats})
            dm = DataManager()
            contacts = dm.load_contacts(filepath)
            self.stats['total_contacts'] = len(contacts)

            self.emit_update('status_update', {
                'message': f'Contactos cargados: {len(contacts)}',
                'stats': self.stats
            })

            # Actualizar configuración del mensaje
            original_template = config.DEFAULT_MESSAGE_TEMPLATE
            config.DEFAULT_MESSAGE_TEMPLATE = message_template

            try:
                # Crear instancia del bot
                self.bot_instance = WhatsAppBot()

                # Ejecutar bot
                self.emit_update('status_update', {'message': 'Iniciando WhatsApp Web...', 'stats': self.stats})
                success = self.bot_instance.run(filepath, limit, delay)

                self.stats['status'] = 'completed' if success else 'failed'
                self.emit_update('bot_completed', self.stats)

            finally:
                # Restaurar configuración original
                config.DEFAULT_MESSAGE_TEMPLATE = original_template

        except Exception as e:
            self.stats['status'] = 'error'
            self.emit_update('error', {'message': f'Error ejecutando bot: {str(e)}'})
        finally:
            self.running = False

# Instancia global del runner
bot_runner = BotRunner(socketio)

@socketio.on('start_bot')
def handle_start_bot(data):
    """Iniciar el bot de WhatsApp"""
    global bot_runner

    try:
        if bot_runner.running:
            emit('error', {'message': 'El bot ya está ejecutándose'})
            return

        # Validar datos
        filename = data.get('filename')
        limit = int(data.get('limit', 50))
        delay = int(data.get('delay', 20))
        message_template = data.get('message', config.DEFAULT_MESSAGE_TEMPLATE)

        if not filename:
            emit('error', {'message': 'No se especificó archivo de contactos'})
            return

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if not os.path.exists(filepath):
            emit('error', {'message': 'Archivo de contactos no encontrado'})
            return

        emit('bot_started', bot_runner.stats)

        # Ejecutar bot en hilo separado
        def run_bot_thread():
            bot_runner.run_bot(filepath, limit, delay, message_template)

        thread = threading.Thread(target=run_bot_thread)
        thread.daemon = True
        thread.start()

    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('stop_bot')
def handle_stop_bot():
    """Detener el bot"""
    global bot_runner

    try:
        if bot_runner.bot_instance and hasattr(bot_runner.bot_instance, 'stop'):
            bot_runner.bot_instance.stop()
        bot_runner.running = False
        bot_runner.stats['status'] = 'stopped'
        emit('bot_stopped', {'message': 'Bot detenido'})
    except Exception as e:
        emit('error', {'message': f'Error deteniendo bot: {str(e)}'})

@socketio.on('get_status')
def handle_get_status():
    """Obtener estado actual del bot"""
    emit('status_update', {'stats': bot_runner.stats, 'running': bot_runner.running})

@app.route('/api/validate-file/<filename>')
def validate_file(filename):
    """Validar un archivo de contactos"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Archivo no encontrado'})

        dm = DataManager()
        contacts = dm.load_contacts(filepath)

        # Estadísticas de validación
        valid_phones = sum(1 for c in contacts if len(c.get('telefono', '')) >= 10)
        invalid_phones = len(contacts) - valid_phones

        return jsonify({
            'success': True,
            'total_contacts': len(contacts),
            'valid_phones': valid_phones,
            'invalid_phones': invalid_phones,
            'sample_contacts': contacts[:5]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Crear directorio de templates si no existe
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('data', exist_ok=True)

    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'

    print("🚀 Iniciando WhatsApp Bot Backend...")
    print(f"🌐 Servidor corriendo en puerto {port}")
    print(f"🔧 Modo debug: {debug}")
    print("🔄 Arquitectura consolidada v3")
    print("=" * 50)

    # Usar threading para mayor compatibilidad
    print("🔧 Usando modo threading para compatibilidad...")
    socketio.run(app, debug=debug, host='0.0.0.0', port=port,
                 allow_unsafe_werkzeug=True)
