// Common JavaScript functionality for all pages

// Load CSS file dynamically
function loadCSS(filename) {
    console.log(`Loading CSS file: ${filename}`);
    return new Promise((resolve, reject) => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = `/static/css/${filename}`;
        
        link.onload = () => {
            console.log(`CSS file loaded successfully: ${filename}`);
            resolve();
        };
        
        link.onerror = (error) => {
            console.error(`Failed to load CSS file: ${filename}`, error);
            reject(error);
        };
        
        document.head.appendChild(link);
    });
}

// Load JavaScript file dynamically
function loadScript(filename) {
    console.log(`Loading JavaScript file: ${filename}`);
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = `/static/js/${filename}`;
        
        script.onload = () => {
            console.log(`JavaScript file loaded successfully: ${filename}`);
            resolve();
        };
        
        script.onerror = (error) => {
            console.error(`Failed to load JavaScript file: ${filename}`, error);
            reject(error);
        };
        
        document.body.appendChild(script);
    });
}

// Initialize common functionality
async function initializeCommon() {
    try {
        console.log('Initializing common functionality...');
        
        // Load error popup CSS
        await loadCSS('error-popup.css');
        
        // Load error popup JavaScript
        await loadScript('error-popup.js');
        
        console.log('Common functionality initialized successfully');
    } catch (error) {
        console.error('Failed to initialize common functionality:', error);
        // Show a basic alert if the error popup system fails to load
        setTimeout(() => {
            alert('Failed to initialize error handling system. Some features may not work properly.');
        }, 1000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing common functionality...');
    initializeCommon().catch(error => {
        console.error('Error in common initialization:', error);
    });
}); 