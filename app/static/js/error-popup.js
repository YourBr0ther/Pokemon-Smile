class ServiceErrorPopup {
    constructor() {
        this.popup = null;
        this.timeoutId = null;
        this.checkInterval = null;
        this.lastStatus = null;
        console.log('Initializing ServiceErrorPopup...');
        this.initializePopup();
        this.startHealthCheck();
    }

    initializePopup() {
        // Create popup element if it doesn't exist
        if (!this.popup) {
            console.log('Creating error popup element...');
            this.popup = document.createElement('div');
            this.popup.className = 'service-error-popup';
            this.popup.innerHTML = `
                <div class="service-error-popup-content">
                    <h3 class="service-error-popup-title">Service Status</h3>
                    <p class="service-error-popup-message"></p>
                    <div class="service-error-popup-status">
                        <span class="service-error-popup-dot"></span>
                        <span class="service-error-popup-status-text"></span>
                    </div>
                    <div class="service-error-popup-actions">
                        <button class="service-error-popup-button primary retry-action">Retry</button>
                        <button class="service-error-popup-button dismiss-action">Dismiss</button>
                    </div>
                </div>
                <button class="service-error-popup-close" aria-label="Close">×</button>
            `;
            document.body.appendChild(this.popup);

            // Add event listeners
            this.popup.querySelector('.service-error-popup-close').addEventListener('click', () => this.hide());
            this.popup.querySelector('.dismiss-action').addEventListener('click', () => this.hide());
            this.popup.querySelector('.retry-action').addEventListener('click', () => this.retryConnection());
            console.log('Error popup element created and initialized');
            
            // Debug: Check if styles are applied
            const computedStyle = window.getComputedStyle(this.popup);
            console.log('Popup styles:', {
                position: computedStyle.position,
                bottom: computedStyle.bottom,
                right: computedStyle.right,
                zIndex: computedStyle.zIndex,
                transform: computedStyle.transform
            });
        }
    }

    async checkHealth() {
        try {
            console.log('Checking service health...');
            const response = await fetch('/api/health');
            console.log('Health check response status:', response.status);
            
            // Handle non-200 responses explicitly
            if (response.status === 503) {
                const data = await response.json();
                console.log('Service degraded response:', data);
                this.lastStatus = 'error';
                this.showError(
                    'Service Unavailable',
                    'Database connection lost. Some features may be unavailable.',
                    'error'
                );
                return;
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Health check response data:', data);
            
            // Debug: Log all service statuses
            if (data.services) {
                Object.entries(data.services).forEach(([service, status]) => {
                    console.log(`${service} status:`, status);
                });
            }
            
            // Only show status changes
            if (this.lastStatus !== data.status) {
                console.log('Status changed from', this.lastStatus, 'to', data.status);
                this.lastStatus = data.status;
                
                if (data.status !== 'healthy') {
                    const mongoStatus = data.services?.mongodb?.status || 'error';
                    this.showError(
                        'Service Degraded',
                        'We\'re experiencing some technical difficulties. Some features may be unavailable.',
                        mongoStatus
                    );
                } else if (this.popup.classList.contains('show')) {
                    // If services recovered, show success message briefly
                    this.showSuccess('Services Restored', 'All systems are now operational.');
                    setTimeout(() => this.hide(), 3000);
                }
            }
        } catch (error) {
            console.error('Health check failed:', error);
            this.lastStatus = 'error';
            this.showError(
                'Connection Error',
                'Unable to connect to services. Please check your internet connection.',
                'error'
            );
        }
    }

    startHealthCheck() {
        // Initial check
        console.log('Starting health checks...');
        this.checkHealth();
        
        // Set up periodic checks every 5 seconds (reduced from 10)
        this.checkInterval = setInterval(() => this.checkHealth(), 5000);
    }

    showError(title, message, status) {
        console.log('Showing error:', { title, message, status });
        
        // Debug: Verify popup exists
        if (!this.popup) {
            console.error('Popup element not found!');
            this.initializePopup();
        }
        
        this.popup.querySelector('.service-error-popup-title').textContent = title;
        this.popup.querySelector('.service-error-popup-message').textContent = message;
        
        const dot = this.popup.querySelector('.service-error-popup-dot');
        const statusText = this.popup.querySelector('.service-error-popup-status-text');
        
        dot.className = 'service-error-popup-dot ' + status;
        statusText.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        
        // Debug: Log current classes
        console.log('Current popup classes:', this.popup.className);
        
        this.popup.className = 'service-error-popup show';
        
        // Debug: Verify visibility
        setTimeout(() => {
            const isVisible = window.getComputedStyle(this.popup).transform === 'matrix(1, 0, 0, 1, 0, 0)';
            console.log('Popup visibility check:', {
                classes: this.popup.className,
                transform: window.getComputedStyle(this.popup).transform,
                isVisible
            });
        }, 100);
        
        // Clear any existing timeout
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
            this.timeoutId = null;
        }
    }

    showSuccess(title, message) {
        console.log('Showing success:', { title, message });
        this.popup.querySelector('.service-error-popup-title').textContent = title;
        this.popup.querySelector('.service-error-popup-message').textContent = message;
        
        const dot = this.popup.querySelector('.service-error-popup-dot');
        const statusText = this.popup.querySelector('.service-error-popup-status-text');
        
        dot.className = 'service-error-popup-dot healthy';
        statusText.textContent = 'Healthy';
        
        this.popup.className = 'service-error-popup show info';
        
        // Auto-hide success message after 3 seconds
        this.timeoutId = setTimeout(() => this.hide(), 3000);
    }

    showWarning(title, message) {
        console.log('Showing warning:', { title, message });
        this.popup.querySelector('.service-error-popup-title').textContent = title;
        this.popup.querySelector('.service-error-popup-message').textContent = message;
        
        const dot = this.popup.querySelector('.service-error-popup-dot');
        const statusText = this.popup.querySelector('.service-error-popup-status-text');
        
        dot.className = 'service-error-popup-dot warning';
        statusText.textContent = 'Warning';
        
        this.popup.className = 'service-error-popup show warning';
    }

    hide() {
        console.log('Hiding popup');
        this.popup.classList.remove('show');
    }

    async retryConnection() {
        console.log('Retrying connection...');
        this.showWarning('Retrying Connection', 'Attempting to restore service connection...');
        await this.checkHealth();
    }

    destroy() {
        console.log('Destroying error popup...');
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
        if (this.popup && this.popup.parentNode) {
            this.popup.parentNode.removeChild(this.popup);
        }
    }
}

// Initialize the error popup system
let serviceErrorPopup;
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing ServiceErrorPopup...');
    serviceErrorPopup = new ServiceErrorPopup();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && serviceErrorPopup) {
        console.log('Page became visible, checking health...');
        serviceErrorPopup.checkHealth();
    }
});

// Export for use in other modules
window.ServiceErrorPopup = ServiceErrorPopup; 