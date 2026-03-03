/**
 * Utility Functions - Vestas Love PDF
 * Funções utilitárias compartilhadas
 */

const Utils = {
    /**
     * Formata tamanho em bytes para formato legível
     * @param {number} bytes - Tamanho em bytes
     * @returns {string} Tamanho formatado
     */
    formatSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const units = ['B', 'KB', 'MB', 'GB'];
        const k = 1024;
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i];
    },

    /**
     * Converte tamanho para bytes
     * @param {number} size - Tamanho
     * @param {string} unit - Unidade (B, KB, MB, GB)
     * @returns {number} Tamanho em bytes
     */
    toBytes(size, unit) {
        const units = { 'B': 1, 'KB': 1024, 'MB': 1024 * 1024, 'GB': 1024 * 1024 * 1024 };
        return size * (units[unit] || 1);
    },

    /**
     * Obtém extensão do arquivo
     * @param {string} filename - Nome do arquivo
     * @returns {string} Extensão (com ponto)
     */
    getExtension(filename) {
        return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 1).toLowerCase();
    },

    /**
     * Remove extensão do arquivo
     * @param {string} filename - Nome do arquivo
     * @returns {string} Nome sem extensão
     */
    removeExtension(filename) {
        return filename.replace(/\.[^/.]+$/, '');
    },

    /**
     * Converte arquivo para Base64
     * @param {File} file - Arquivo
     * @returns {Promise<string>} String Base64
     */
    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = error => reject(error);
        });
    },

    /**
     * Converte ArrayBuffer para Base64
     * @param {ArrayBuffer} buffer - ArrayBuffer
     * @returns {string} String Base64
     */
    arrayBufferToBase64(buffer) {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    },

    /**
     * Faz download de um Blob
     * @param {Blob} blob - Blob a baixar
     * @param {string} filename - Nome do arquivo
     */
    downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },

    /**
     * Debounce function
     * @param {Function} func - Função a executar
     * @param {number} wait - Tempo de espera em ms
     * @returns {Function}
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function
     * @param {Function} func - Função a executar
     * @param {number} limit - Intervalo mínimo em ms
     * @returns {Function}
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Mostra notificação toast
     * @param {string} message - Mensagem
     * @param {string} type - Tipo (success, error, warning, info)
     */
    showToast(message, type = 'info') {
        // Criar container se não existir
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:10000;';
            document.body.appendChild(container);
        }

        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };

        const toast = document.createElement('div');
        toast.style.cssText = `
            background: ${colors[type] || colors.info};
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease;
            max-width: 350px;
        `;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    /**
     * Escapa HTML para prevenir XSS
     * @param {string} text - Texto a escapar
     * @returns {string} Texto escapado
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Valida se arquivo tem extensão permitida
     * @param {string} filename - Nome do arquivo
     * @param {string[]} allowedExtensions - Extensões permitidas
     * @returns {boolean}
     */
    isValidExtension(filename, allowedExtensions) {
        const ext = this.getExtension(filename);
        return allowedExtensions.includes(ext);
    },

    /**
     * Obtém o tamanho de um arquivo em formato legível
     * @param {File} file - Arquivo
     * @returns {string}
     */
    getFileSize(file) {
        return this.formatSize(file.size);
    }
};

// Adicionar estilos de animação
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Expor globalmente
window.Utils = Utils;
