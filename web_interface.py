#!/usr/bin/env python3
"""
Interfaz web para el bot de WhatsApp usando Flask
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import threading
import time
from pathlib import Path
import queue

# Importar módulos del bot
import config
import logger
from data_manager import DataManager
from whatsapp_client import WhatsAppClient
from message_sender import MessageSender

app = Flask(__name__)
app.secret_key = 'whatsapp_bot_secret_key_2024'

# Variables globales para el estado del bot
bot_state = {
    'is_running': False,
    'current_step': 'idle',
    'contacts_loaded': 0,
    'contacts_valid': 0,
    'messages_sent': 0,
    'messages_total': 0,
    'progress': 0,
    'status': 'Listo',
    'log_messages': []
}

# Queue para comunicación entre threads
message_queue = queue.Queue()

# Instancias del bot
data_manager = None
whatsapp_client = None
message_sender = None
bot_thread = None

def log_to_web(message, level="INFO"):
    """Agrega un mensaje al log web"""
    timestamp = time.strftime("%H:%M:%S")
    
    # Agregar emoji según el nivel
    if level == "ERROR":
        icon = "❌"
        css_class = "error"
    elif level == "WARNING":
        icon = "⚠️"
        css_class = "warning"
    elif level == "SUCCESS":
        icon = "✅"
        css_class = "success"
    else:
        icon = "ℹ️"
        css_class = "info"
    
    log_entry = {
        'timestamp': timestamp,
        'icon': icon,
        'message': message,
        'level': level,
        'css_class': css_class
    }
    
    bot_state['log_messages'].append(log_entry)
    
    # Mantener solo los últimos 100 mensajes
    if len(bot_state['log_messages']) > 100:
        bot_state['log_messages'] = bot_state['log_messages'][-100:]

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html', state=bot_state)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Maneja la subida de archivos"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
        
        # Verificar extensión
        allowed_extensions = {'.csv', '.xlsx', '.xls'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': 'Formato no soportado. Use CSV o Excel'})
        
        # Guardar archivo temporalmente
        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        file.save(str(file_path))
        
        # Cargar y validar contactos
        global data_manager
        data_manager = DataManager()
        contacts = data_manager.load_contacts(str(file_path))
        stats = data_manager.validate_contacts()
        
        # Actualizar estado
        bot_state['contacts_loaded'] = stats['total']
        bot_state['contacts_valid'] = stats['valid']
        bot_state['status'] = f"Archivo cargado: {stats['valid']} contactos válidos"
        
        log_to_web(f"Archivo cargado: {file.filename}", "SUCCESS")
        log_to_web(f"Contactos válidos: {stats['valid']}/{stats['total']}", "INFO")
        
        # Limpiar archivo temporal
        os.unlink(file_path)
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'total': stats['total'],
            'valid': stats['valid'],
            'invalid': stats['total'] - stats['valid']
        })
        
    except Exception as e:
        log_to_web(f"Error cargando archivo: {e}", "ERROR")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Inicia el bot"""
    global bot_thread
    
    if bot_state['is_running']:
        return jsonify({'success': False, 'error': 'Bot ya está ejecutándose'})
    
    if not data_manager or bot_state['contacts_valid'] == 0:
        return jsonify({'success': False, 'error': 'Carga contactos válidos primero'})
    
    try:
        # Obtener parámetros
        data = request.get_json()
        limit = int(data.get('limit', 50))
        delay = int(data.get('delay', 20))
        
        # Validar parámetros
        if not (1 <= limit <= 1000):
            return jsonify({'success': False, 'error': 'Límite debe estar entre 1 y 1000'})
        
        if not (5 <= delay <= 300):
            return jsonify({'success': False, 'error': 'Delay debe estar entre 5 y 300 segundos'})
        
        # Iniciar bot en thread separado
        bot_state['is_running'] = True
        bot_state['current_step'] = 'starting'
        bot_state['status'] = 'Iniciando bot...'
        
        bot_thread = threading.Thread(
            target=run_bot_thread,
            args=(limit, delay),
            daemon=True
        )
        bot_thread.start()
        
        log_to_web("Bot iniciado", "SUCCESS")
        
        return jsonify({'success': True})
        
    except Exception as e:
        bot_state['is_running'] = False
        log_to_web(f"Error iniciando bot: {e}", "ERROR")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Detiene el bot"""
    try:
        if not bot_state['is_running']:
            return jsonify({'success': False, 'error': 'Bot no está ejecutándose'})
        
        # Detener message sender si existe
        global message_sender
        if message_sender:
            message_sender.stop_sending()
        
        # Cerrar navegador si existe
        global whatsapp_client
        if whatsapp_client:
            whatsapp_client.close_browser()
        
        bot_state['is_running'] = False
        bot_state['current_step'] = 'stopped'
        bot_state['status'] = 'Detenido por el usuario'
        
        log_to_web("Bot detenido", "WARNING")
        
        return jsonify({'success': True})
        
    except Exception as e:
        log_to_web(f"Error deteniendo bot: {e}", "ERROR")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/status')
def get_status():
    """Obtiene el estado actual del bot"""
    return jsonify(bot_state)

@app.route('/api/clear_log', methods=['POST'])
def clear_log():
    """Limpia el log"""
    bot_state['log_messages'] = []
    return jsonify({'success': True})

def run_bot_thread(limit, delay):
    """Ejecuta el bot en un thread separado"""
    global whatsapp_client, message_sender
    
    try:
        log_to_web("🚀 Iniciando bot de WhatsApp...")
        bot_state['current_step'] = 'browser'
        bot_state['status'] = 'Iniciando navegador...'
        
        # Crear cliente de WhatsApp
        whatsapp_client = WhatsAppClient()
        
        # Iniciar navegador
        log_to_web("🌐 Iniciando navegador...")
        if not whatsapp_client.start_browser():
            raise Exception("Error iniciando navegador")
        
        log_to_web("✅ Navegador iniciado")
        bot_state['current_step'] = 'qr'
        bot_state['status'] = 'Esperando código QR...'
        
        # Esperar escaneo QR
        log_to_web("📱 Esperando escaneo de código QR...")
        if not whatsapp_client.wait_for_qr_scan():
            raise Exception("Timeout esperando código QR")
        
        log_to_web("✅ Código QR escaneado")
        bot_state['current_step'] = 'sending'
        bot_state['status'] = 'Enviando mensajes...'
        
        # Enviar mensajes
        message_sender = MessageSender(whatsapp_client, progress_callback=update_progress)
        contacts_to_send = data_manager.filter_contacts(limit)
        
        bot_state['messages_total'] = len(contacts_to_send)
        
        stats = message_sender.send_messages_to_contacts(
            contacts_to_send, limit, delay
        )
        
        # Mostrar resultados
        bot_state['messages_sent'] = stats.messages_sent
        bot_state['progress'] = 100
        bot_state['current_step'] = 'completed'
        bot_state['status'] = f"Completado: {stats.messages_sent}/{stats.total_contacts} enviados"
        
        log_to_web(f"✅ Envío completado: {stats.messages_sent}/{stats.total_contacts}", "SUCCESS")
        
    except Exception as e:
        bot_state['current_step'] = 'error'
        bot_state['status'] = f"Error: {str(e)}"
        log_to_web(f"❌ Error: {e}", "ERROR")
    
    finally:
        # Limpiar
        if whatsapp_client:
            whatsapp_client.close_browser()
        
        bot_state['is_running'] = False

def update_progress(current, total):
    """Callback para actualizar progreso"""
    if total > 0:
        bot_state['progress'] = (current / total) * 100
        bot_state['messages_sent'] = current
        bot_state['status'] = f"Enviando: {current}/{total} ({bot_state['progress']:.1f}%)"

def create_templates():
    """Crea los templates HTML si no existen"""
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    # Template principal
    index_html = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bot de WhatsApp</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #25D366; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .form-group { margin-bottom: 15px; }
        .form-control { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .progress { width: 100%; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden; }
        .progress-bar { height: 100%; background: #25D366; transition: width 0.3s; }
        .log { height: 300px; overflow-y: auto; background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; }
        .log-entry { margin-bottom: 5px; }
        .log-error { color: #dc3545; }
        .log-success { color: #28a745; }
        .log-warning { color: #ffc107; }
        .status { padding: 10px; border-radius: 4px; margin-bottom: 20px; }
        .status-success { background: #d4edda; color: #155724; }
        .status-error { background: #f8d7da; color: #721c24; }
        .status-warning { background: #fff3cd; color: #856404; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Bot de WhatsApp</h1>
            <p>Envío automatizado de mensajes</p>
        </div>
        
        <div class="status" id="status">
            Estado: {{ state.status }}
        </div>
        
        <div class="grid">
            <div>
                <div class="card">
                    <h3>📁 Archivo de Contactos</h3>
                    <div class="form-group">
                        <input type="file" id="fileInput" class="form-control" accept=".csv,.xlsx,.xls">
                    </div>
                    <div id="fileInfo">
                        {% if state.contacts_loaded > 0 %}
                        <p>Total: {{ state.contacts_loaded }} | Válidos: {{ state.contacts_valid }}</p>
                        {% else %}
                        <p>Selecciona un archivo CSV o Excel</p>
                        {% endif %}
                    </div>
                </div>
                
                <div class="card">
                    <h3>⚙️ Configuración</h3>
                    <div class="form-group">
                        <label>Límite de mensajes:</label>
                        <input type="number" id="limit" class="form-control" value="50" min="1" max="1000">
                    </div>
                    <div class="form-group">
                        <label>Delay (segundos):</label>
                        <input type="number" id="delay" class="form-control" value="20" min="5" max="300">
                    </div>
                </div>
                
                <div class="card">
                    <h3>🎮 Controles</h3>
                    <button id="startBtn" class="btn btn-primary" onclick="startBot()">🚀 Iniciar Bot</button>
                    <button id="stopBtn" class="btn btn-danger" onclick="stopBot()" disabled>⏹️ Detener</button>
                    <button class="btn btn-secondary" onclick="clearLog()">🧹 Limpiar Log</button>
                </div>
            </div>
            
            <div>
                <div class="card">
                    <h3>📊 Progreso</h3>
                    <div class="progress">
                        <div class="progress-bar" id="progressBar" style="width: {{ state.progress }}%"></div>
                    </div>
                    <p id="progressText">{{ state.messages_sent }}/{{ state.messages_total }} ({{ state.progress }}%)</p>
                </div>
                
                <div class="card">
                    <h3>📝 Log de Actividad</h3>
                    <div class="log" id="logContainer">
                        {% for log in state.log_messages %}
                        <div class="log-entry log-{{ log.css_class }}">
                            [{{ log.timestamp }}] {{ log.icon }} {{ log.message }}
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Actualizar estado cada 2 segundos
        setInterval(updateStatus, 2000);
        
        // Manejar subida de archivo
        document.getElementById('fileInput').addEventListener('change', uploadFile);
        
        function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('fileInfo').innerHTML = 
                        `<p>✅ ${data.filename}<br>Total: ${data.total} | Válidos: ${data.valid} | Inválidos: ${data.invalid}</p>`;
                    document.getElementById('startBtn').disabled = data.valid === 0;
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }
        
        function startBot() {
            const limit = document.getElementById('limit').value;
            const delay = document.getElementById('delay').value;
            
            fetch('/api/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({limit: parseInt(limit), delay: parseInt(delay)})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }
        
        function stopBot() {
            fetch('/api/stop', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                }
            });
        }
        
        function clearLog() {
            fetch('/api/clear_log', {method: 'POST'})
            .then(() => updateStatus());
        }
        
        function updateStatus() {
            fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                // Actualizar estado
                document.getElementById('status').textContent = 'Estado: ' + data.status;
                
                // Actualizar progreso
                document.getElementById('progressBar').style.width = data.progress + '%';
                document.getElementById('progressText').textContent = 
                    `${data.messages_sent}/${data.messages_total} (${data.progress.toFixed(1)}%)`;
                
                // Actualizar botones
                document.getElementById('startBtn').disabled = data.is_running || data.contacts_valid === 0;
                document.getElementById('stopBtn').disabled = !data.is_running;
                
                // Actualizar log
                const logContainer = document.getElementById('logContainer');
                logContainer.innerHTML = '';
                data.log_messages.forEach(log => {
                    const div = document.createElement('div');
                    div.className = `log-entry log-${log.css_class}`;
                    div.textContent = `[${log.timestamp}] ${log.icon} ${log.message}`;
                    logContainer.appendChild(div);
                });
                logContainer.scrollTop = logContainer.scrollHeight;
            });
        }
    </script>
</body>
</html>'''
    
    with open(templates_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)

def main():
    """Función principal"""
    print("🌐 Iniciando interfaz web del bot de WhatsApp...")
    
    # Crear templates
    create_templates()
    
    # Crear directorio de uploads
    Path('uploads').mkdir(exist_ok=True)
    
    # Inicializar log
    log_to_web("Interfaz web iniciada", "SUCCESS")
    log_to_web("Accede a: http://localhost:5000", "INFO")
    
    # Iniciar servidor
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()
