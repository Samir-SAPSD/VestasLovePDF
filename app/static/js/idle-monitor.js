/**
 * Idle Monitor - Vestas Love PDF
 * Monitora inatividade do usuário e envia heartbeat ao servidor
 */

class IdleMonitor {
    constructor(options = {}) {
        // Configurações (em milissegundos)
        this.idleTimeout = options.idleTimeout || 5 * 60 * 1000;      // 5 minutos para mostrar popup
        this.popupTimeout = options.popupTimeout || 5 * 60 * 1000;    // 5 minutos para fechar após popup
        this.heartbeatInterval = options.heartbeatInterval || 1000;   // 1 segundo
        
        // Estado
        this.idleTimer = null;
        this.popupTimer = null;
        this.countdownInterval = null;
        this.heartbeatTimer = null;
        this.isPopupVisible = false;
        
        // Elementos do DOM
        this.modal = null;
        this.countdownElement = null;
        
        // Inicializar
        this._init();
    }
    
    _init() {
        this._createModal();
        this._bindEvents();
        this._startHeartbeat();
        this._resetIdleTimer();
    }
    
    _createModal() {
        // Verificar se já existe
        if (document.getElementById('idleModal')) {
            this.modal = document.getElementById('idleModal');
            this.countdownElement = document.getElementById('countdownTimer');
            return;
        }
        
        // Criar modal
        const modalHtml = `
            <div class="idle-modal-overlay" id="idleModal">
                <div class="idle-modal">
                    <div class="idle-modal-icon">
                        <i class="bi bi-question-circle"></i>
                    </div>
                    <h3>Você ainda está aí?</h3>
                    <p>Detectamos que você está inativo há algum tempo.</p>
                    <div class="countdown">
                        A sessão será encerrada em <span id="countdownTimer">5:00</span>
                    </div>
                    <div class="idle-modal-buttons">
                        <button class="btn btn-idle-yes" id="idleConfirmBtn">
                            <i class="bi bi-check-lg me-2"></i>Sim, estou aqui
                        </button>
                        <button class="btn btn-idle-no" id="idleCloseBtn">
                            <i class="bi bi-x-lg me-2"></i>Não, encerrar
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        this.modal = document.getElementById('idleModal');
        this.countdownElement = document.getElementById('countdownTimer');
        
        // Event listeners dos botões
        document.getElementById('idleConfirmBtn').addEventListener('click', () => this.confirmActive());
        document.getElementById('idleCloseBtn').addEventListener('click', () => this.closeSession());
    }
    
    _bindEvents() {
        const activityEvents = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'];
        activityEvents.forEach(event => {
            document.addEventListener(event, () => this._resetIdleTimer(), { passive: true });
        });
    }
    
    _resetIdleTimer() {
        if (this.isPopupVisible) return;
        
        clearTimeout(this.idleTimer);
        this.idleTimer = setTimeout(() => this._showIdlePopup(), this.idleTimeout);
    }
    
    _showIdlePopup() {
        this.isPopupVisible = true;
        this.modal.classList.add('show');
        this._startCountdown();
    }
    
    _startCountdown() {
        let timeLeft = this.popupTimeout / 1000;
        
        this._updateCountdownDisplay(timeLeft);
        
        this.countdownInterval = setInterval(() => {
            timeLeft--;
            this._updateCountdownDisplay(timeLeft);
            
            if (timeLeft <= 0) {
                this.closeSession();
            }
        }, 1000);
        
        this.popupTimer = setTimeout(() => this.closeSession(), this.popupTimeout);
    }
    
    _updateCountdownDisplay(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        if (this.countdownElement) {
            this.countdownElement.textContent = minutes + ':' + (secs < 10 ? '0' : '') + secs;
        }
    }
    
    _startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            fetch('/heartbeat', { method: 'POST' }).catch(() => {});
        }, this.heartbeatInterval);
    }
    
    confirmActive() {
        this.isPopupVisible = false;
        this.modal.classList.remove('show');
        
        clearTimeout(this.popupTimer);
        clearInterval(this.countdownInterval);
        
        this._resetIdleTimer();
    }
    
    closeSession() {
        clearTimeout(this.idleTimer);
        clearTimeout(this.popupTimer);
        clearInterval(this.countdownInterval);
        clearInterval(this.heartbeatTimer);
        
        // Tenta fechar a aba/janela
        window.close();
        
        // Se não conseguir fechar, mostra mensagem
        setTimeout(() => {
            document.body.innerHTML = `
                <div style="display:flex;justify-content:center;align-items:center;height:100vh;flex-direction:column;font-family:sans-serif;color:#1F3144;">
                    <h1>Sessão Encerrada</h1>
                    <p>Você pode fechar esta aba.</p>
                </div>
            `;
        }, 500);
    }
    
    destroy() {
        clearTimeout(this.idleTimer);
        clearTimeout(this.popupTimer);
        clearInterval(this.countdownInterval);
        clearInterval(this.heartbeatTimer);
        
        if (this.modal) {
            this.modal.remove();
        }
    }
}

// Auto-inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.idleMonitor = new IdleMonitor();
});

// Expor globalmente
window.IdleMonitor = IdleMonitor;
