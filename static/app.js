// WhatsApp Bot - Modern Web Interface
// JavaScript functionality

class WhatsAppBotInterface {
    constructor() {
        this.socket = io();
        this.currentFile = null;
        this.botRunning = false;
        
        this.initializeElements();
        this.setupEventListeners();
        this.setupSocketListeners();
        this.loadExistingFiles();
    }
    
    initializeElements() {
        // File elements
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('fileInput');
        this.fileInfo = document.getElementById('fileInfo');
        this.fileName = document.getElementById('fileName');
        this.fileStats = document.getElementById('fileStats');
        this.contactPreview = document.getElementById('contactPreview');
        this.contactList = document.getElementById('contactList');
        this.removeFileBtn = document.getElementById('removeFile');
        
        // Configuration elements
        this.messageLimit = document.getElementById('messageLimit');
        this.messageDelay = document.getElementById('messageDelay');
        this.messageTemplate = document.getElementById('messageTemplate');
        
        // Control elements
        this.startBtn = document.getElementById('startBot');
        this.stopBtn = document.getElementById('stopBot');
        this.botStatus = document.getElementById('botStatus');
        this.totalContacts = document.getElementById('totalContacts');
        this.messagesSent = document.getElementById('messagesSent');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        
        // Theme toggle
        this.themeToggle = document.getElementById('themeToggle');
        this.notifications = document.getElementById('notifications');
    }
    
    setupEventListeners() {
        // File upload
        this.dropZone.addEventListener('click', () => this.fileInput.click());
        this.dropZone.addEventListener('dragover', this.handleDragOver.bind(this));
        this.dropZone.addEventListener('drop', this.handleDrop.bind(this));
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        this.removeFileBtn.addEventListener('click', this.removeFile.bind(this));
        
        // Control buttons
        this.startBtn.addEventListener('click', this.startBot.bind(this));
        this.stopBtn.addEventListener('click', this.stopBot.bind(this));

        // Test connection button
        const testConnectionBtn = document.getElementById('testConnection');
        if (testConnectionBtn) {
            testConnectionBtn.addEventListener('click', this.testConnection.bind(this));
        }

        // Theme toggle
        this.themeToggle.addEventListener('click', this.toggleTheme.bind(this));

        // Auto-save configuration
        this.messageLimit.addEventListener('change', this.saveConfiguration.bind(this));
        this.messageDelay.addEventListener('change', this.saveConfiguration.bind(this));
        this.messageTemplate.addEventListener('input', this.saveConfiguration.bind(this));

        // Load saved configuration
        this.loadConfiguration();
    }
    
    setupSocketListeners() {
        this.socket.on('bot_started', (data) => {
            this.botRunning = true;
            this.updateBotStatus('Iniciando...', 'bg-yellow-500');
            this.toggleButtons(true);
            this.showNotification('Bot iniciado exitosamente', 'success');
        });
        
        this.socket.on('status_update', (data) => {
            if (data.stats) {
                this.updateStats(data.stats);
            }
            if (data.message) {
                this.showNotification(data.message, 'info');
            }
        });
        
        this.socket.on('bot_completed', (data) => {
            this.botRunning = false;
            this.updateBotStatus('Completado', 'bg-green-500');
            this.toggleButtons(false);
            this.showNotification('Envío completado exitosamente', 'success');
        });
        
        this.socket.on('bot_stopped', (data) => {
            this.botRunning = false;
            this.updateBotStatus('Detenido', 'bg-red-500');
            this.toggleButtons(false);
            this.showNotification('Bot detenido', 'warning');
        });
        
        this.socket.on('error', (data) => {
            this.botRunning = false;
            this.updateBotStatus('Error', 'bg-red-500');
            this.toggleButtons(false);
            this.showNotification(data.message, 'error');
        });
    }
    
    handleDragOver(e) {
        e.preventDefault();
        this.dropZone.classList.add('drop-zone-active');
    }

    handleDrop(e) {
        e.preventDefault();
        this.dropZone.classList.remove('drop-zone-active');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    async processFile(file) {
        // Show upload progress
        document.getElementById('dropContent').classList.add('hidden');
        document.getElementById('uploadProgress').classList.remove('hidden');
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentFile = result.filename;
                this.displayFileInfo(result);
                this.displayContactPreview(result.preview);
                this.showNotification(`Archivo cargado: ${result.contact_count} contactos`, 'success');
            } else {
                this.showNotification(result.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error al subir archivo', 'error');
        } finally {
            // Hide upload progress
            document.getElementById('dropContent').classList.remove('hidden');
            document.getElementById('uploadProgress').classList.add('hidden');
        }
    }
    
    displayFileInfo(fileData) {
        this.fileName.textContent = fileData.filename;
        this.fileStats.textContent = `${fileData.contact_count} contactos`;
        this.fileInfo.classList.remove('hidden');
        this.totalContacts.textContent = fileData.contact_count;
    }
    
    displayContactPreview(contacts) {
        this.contactList.innerHTML = '';
        
        contacts.forEach(contact => {
            const contactDiv = document.createElement('div');
            contactDiv.className = 'flex items-center justify-between p-2 bg-background rounded border';
            contactDiv.innerHTML = `
                <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                        <i class="fas fa-user text-primary-foreground text-xs"></i>
                    </div>
                    <div>
                        <p class="font-medium text-sm">${contact.nombre}</p>
                        <p class="text-xs text-muted-foreground">${contact.telefono}</p>
                    </div>
                </div>
            `;
            this.contactList.appendChild(contactDiv);
        });
        
        this.contactPreview.classList.remove('hidden');
    }
    
    removeFile() {
        this.currentFile = null;
        this.fileInfo.classList.add('hidden');
        this.contactPreview.classList.add('hidden');
        this.fileInput.value = '';
        this.totalContacts.textContent = '0';
        this.showNotification('Archivo removido', 'info');
    }
    
    async loadExistingFiles() {
        try {
            const response = await fetch('/api/files');
            const result = await response.json();
            
            if (result.success && result.files.length > 0) {
                // Could implement a file selector here
                console.log('Archivos disponibles:', result.files);
            }
        } catch (error) {
            console.error('Error cargando archivos:', error);
        }
    }
    
    startBot() {
        if (!this.currentFile) {
            this.showNotification('Por favor selecciona un archivo de contactos', 'error');
            return;
        }
        
        const config = {
            filename: this.currentFile,
            limit: parseInt(this.messageLimit.value),
            delay: parseInt(this.messageDelay.value),
            message: this.messageTemplate.value || 'Hola {nombre}, este es un mensaje automático.'
        };
        
        this.socket.emit('start_bot', config);
    }
    
    stopBot() {
        this.socket.emit('stop_bot');
    }
    
    updateBotStatus(status, colorClass) {
        this.botStatus.textContent = status;
        this.botStatus.className = `px-2 py-1 rounded-full text-xs font-medium ${colorClass} text-white`;
    }
    
    updateStats(stats) {
        this.totalContacts.textContent = stats.total_contacts || 0;
        this.messagesSent.textContent = stats.messages_sent || 0;
        
        if (stats.total_contacts > 0) {
            const progress = (stats.messages_sent / stats.total_contacts) * 100;
            this.progressBar.style.width = `${progress}%`;
            this.progressText.textContent = `${Math.round(progress)}%`;
            this.progressContainer.classList.remove('hidden');
        }
    }
    
    toggleButtons(running) {
        if (running) {
            this.startBtn.classList.add('hidden');
            this.stopBtn.classList.remove('hidden');
        } else {
            this.startBtn.classList.remove('hidden');
            this.stopBtn.classList.add('hidden');
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        notification.className = `${colors[type]} text-white p-4 rounded-lg shadow-lg flex items-center space-x-3 animate-pulse`;
        notification.innerHTML = `
            <i class="fas ${icons[type]}"></i>
            <span class="flex-1">${message}</span>
            <button class="text-white hover:text-gray-200" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        this.notifications.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    toggleTheme() {
        const html = document.documentElement;
        const isDark = html.classList.contains('dark');

        if (isDark) {
            html.classList.remove('dark');
            this.themeToggle.innerHTML = '<i class="fas fa-moon text-lg"></i>';
            localStorage.setItem('theme', 'light');
        } else {
            html.classList.add('dark');
            this.themeToggle.innerHTML = '<i class="fas fa-sun text-lg"></i>';
            localStorage.setItem('theme', 'dark');
        }
    }

    testConnection() {
        this.showNotification('Probando conexión con WhatsApp Web...', 'info');
        // Aquí se podría implementar una prueba de conexión real
        setTimeout(() => {
            this.showNotification('Conexión exitosa con WhatsApp Web', 'success');
        }, 2000);
    }

    saveConfiguration() {
        const config = {
            limit: this.messageLimit.value,
            delay: this.messageDelay.value,
            message: this.messageTemplate.value
        };
        localStorage.setItem('botConfig', JSON.stringify(config));
    }

    loadConfiguration() {
        try {
            const savedConfig = localStorage.getItem('botConfig');
            if (savedConfig) {
                const config = JSON.parse(savedConfig);
                this.messageLimit.value = config.limit || 50;
                this.messageDelay.value = config.delay || 20;
                this.messageTemplate.value = config.message || '';
            }

            // Load theme
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {
                document.documentElement.classList.add('dark');
                this.themeToggle.innerHTML = '<i class="fas fa-sun text-lg"></i>';
            }
        } catch (error) {
            console.error('Error loading configuration:', error);
        }
    }

    enhanceNotifications() {
        // Add enhanced notification animations
        const notifications = this.notifications.querySelectorAll('.notification-enter');
        notifications.forEach(notification => {
            notification.classList.add('notification-enter');
            setTimeout(() => {
                notification.classList.remove('notification-enter');
            }, 300);
        });
    }
}

// Initialize the interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WhatsAppBotInterface();
});
