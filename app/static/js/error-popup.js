class ServiceErrorPopup {
    constructor() {
        this.lastStatus = 'unknown';
        this.retryCount = 0;
        this.maxRetries = 3;
        this.retryDelay = 5000; // 5 seconds
        this.setupPopup();
        this.startHealthCheck();
    }

    setupPopup() {
        // Create popup container if it doesn't exist
        if (!document.getElementById('service-error-popup')) {
            const popup = document.createElement('div');
            popup.id = 'service-error-popup';
            popup.className = 'service-error-popup';
            popup.innerHTML = `
                <div class="popup-content">
                    <span class="close-button">&times;</span>
                    <div class="status-indicator">
                        <span class="status-dot"></span>
                        <h3 class="popup-title"></h3>
                    </div>
                    <p class="popup-message"></p>
                    <div class="popup-actions">
                        <button class="retry-button">Retry Connection</button>
                        <button class="dismiss-button">Dismiss</button>
                    </div>
                </div>
            `;
            document.body.appendChild(popup);
            
            // Set up event listeners
            popup.querySelector('.close-button').addEventListener('click', () => this.hide());
            popup.querySelector('.retry-button').addEventListener('click', () => this.retryConnection());
            popup.querySelector('.dismiss-button').addEventListener('click', () => this.hide());
        }
        this.popup = document.getElementById('service-error-popup');
    }

    async checkHealth() {
        try {
            console.log('Checking service health...');
            const response = await fetch('/api/health');
            console.log('Health check response status:', response.status);
            
            const data = await response.json();
            console.log('Health check response data:', data);
            
            // Reset retry count on successful response
            this.retryCount = 0;
            
            // Handle different status codes
            if (response.status === 503) {
                this.lastStatus = 'error';
                const message = data.services?.mongodb?.error || 
                              'Database connection lost. Some features may be unavailable.';
                this.showError('Service Unavailable', message, 'error');
                return;
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Debug: Log all service statuses
            if (data.services) {
                Object.entries(data.services).forEach(([service, status]) => {
                    console.log(`${service} status:`, status);
                });
            }
            
            const mongoStatus = data.services?.mongodb?.status || 'unknown';
            
            // Only show status changes
            if (this.lastStatus !== mongoStatus) {
                console.log('Status changed from', this.lastStatus, 'to', mongoStatus);
                this.lastStatus = mongoStatus;
                
                if (mongoStatus !== 'healthy') {
                    const errorMessage = data.services?.mongodb?.error || 
                                      'We\'re experiencing some technical difficulties. Some features may be unavailable.';
                    this.showError(
                        'Service Degraded',
                        errorMessage,
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
            
            // Implement exponential backoff for retries
            this.retryCount++;
            if (this.retryCount <= this.maxRetries) {
                const delay = this.retryDelay * Math.pow(2, this.retryCount - 1);
                console.log(`Scheduling retry ${this.retryCount} in ${delay}ms`);
                setTimeout(() => this.checkHealth(), delay);
            }
            
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
        
        // Set up periodic checks every 5 seconds
        this.checkInterval = setInterval(() => {
            // Only check if we haven't exceeded retry attempts
            if (this.retryCount <= this.maxRetries) {
                this.checkHealth();
            }
        }, 5000);
    }

    showError(title, message, status = 'error') {
        const statusDot = this.popup.querySelector('.status-dot');
        statusDot.className = `status-dot ${status}`;
        
        this.popup.querySelector('.popup-title').textContent = title;
        this.popup.querySelector('.popup-message').textContent = message;
        this.popup.classList.add('show');
    }

    showSuccess(title, message) {
        const statusDot = this.popup.querySelector('.status-dot');
        statusDot.className = 'status-dot healthy';
        
        this.popup.querySelector('.popup-title').textContent = title;
        this.popup.querySelector('.popup-message').textContent = message;
        this.popup.classList.add('show');
    }

    hide() {
        this.popup.classList.remove('show');
    }

    async retryConnection() {
        console.log('Retrying connection...');
        this.showWarning('Retrying Connection', 'Attempting to restore service connection...');
        
        // Reset retry count when manually retrying
        this.retryCount = 0;
        await this.checkHealth();
    }

    showWarning(title, message) {
        const statusDot = this.popup.querySelector('.status-dot');
        statusDot.className = 'status-dot unknown';
        
        this.popup.querySelector('.popup-title').textContent = title;
        this.popup.querySelector('.popup-message').textContent = message;
        this.popup.classList.add('show');
    }
}

// Initialize the error popup
const serviceErrorPopup = new ServiceErrorPopup();

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && serviceErrorPopup) {
        console.log('Page became visible, checking health...');
        // Reset retry count when page becomes visible
        serviceErrorPopup.retryCount = 0;
        serviceErrorPopup.checkHealth();
    }
});

// Export for use in other modules
window.ServiceErrorPopup = ServiceErrorPopup; 