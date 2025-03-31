// Online/Offline status handling
let isOnline = navigator.onLine;

function updateOnlineStatus(event) {
    isOnline = navigator.onLine;
    checkFeatureAvailability();
}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

// Check if features should be enabled/disabled
function checkFeatureAvailability() {
    const offlineDisabledElements = document.querySelectorAll('[data-requires-connection]');
    
    offlineDisabledElements.forEach(element => {
        if (!isOnline) {
            element.classList.add('offline-disabled');
            element.setAttribute('disabled', 'disabled');
            element.setAttribute('title', 'This feature requires an internet connection');
        } else {
            element.classList.remove('offline-disabled');
            element.removeAttribute('disabled');
            element.removeAttribute('title');
        }
    });
}

// Add health check before certain operations
async function checkServerHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        return data.status === 'healthy';
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}

// Modify existing functions to check health before proceeding
async function saveProfile() {
    if (!isOnline) {
        showMessage('This feature requires an internet connection');
        return;
    }
    
    if (!await checkServerHealth()) {
        showMessage('Service is currently unavailable. Please try again later.');
        return;
    }
    
    // ... existing saveProfile code ...
}

async function resetPokedex() {
    if (!isOnline) {
        showMessage('This feature requires an internet connection');
        return;
    }
    
    if (!await checkServerHealth()) {
        showMessage('Service is currently unavailable. Please try again later.');
        return;
    }
    
    // ... existing resetPokedex code ...
}

async function startBrushing() {
    if (!isOnline) {
        showMessage('Brushing sessions require an internet connection to save progress');
        return;
    }
    
    if (!await checkServerHealth()) {
        showMessage('Service is currently unavailable. Please try again later.');
        return;
    }
    
    // ... existing startBrushing code ...
}

// Helper function to show messages
function showMessage(message) {
    const messageElement = document.getElementById('messagePopup') || createMessagePopup();
    messageElement.textContent = message;
    messageElement.style.display = 'block';
    setTimeout(() => {
        messageElement.style.display = 'none';
    }, 3000);
}

// Create message popup if it doesn't exist
function createMessagePopup() {
    const popup = document.createElement('div');
    popup.id = 'messagePopup';
    popup.className = 'message-popup';
    document.body.appendChild(popup);
    return popup;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateOnlineStatus();
    checkFeatureAvailability();
}); 