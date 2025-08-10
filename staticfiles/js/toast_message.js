// Toast Messages System for VihOhtLife
// Auto dismiss toasts after dur milliseconds and handle manual dismissal
const dur = 2000;

document.addEventListener('DOMContentLoaded', function() {
    initializeToastMessages();
});

function initializeToastMessages() {
    const toasts = document.querySelectorAll('[id^="toast-"]');
    
    // Auto dismiss toasts with staggered timing
    toasts.forEach(function(toast, index) {
        setTimeout(function() {
            dismissToast(toast.id);
        }, dur + (index * dur / 10)); // Stagger dismissal for multiple toasts
    });
    
    // Refresh Lucide icons for new toast content
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function dismissToast(toastId) {
    console.log('Dismissing toast:', toastId); // Debug log
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.style.transition = 'all 0.3s ease-out';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        
        setTimeout(function() {
            if (toast.parentNode) {
                toast.remove();
                console.log('Toast removed:', toastId); // Debug log
            }
        }, 300);
    } else {
        console.warn('Toast not found:', toastId); // Debug log
    }
}

// Make dismissToast globally accessible
window.dismissToast = dismissToast;

// Function to manually create toast messages via JavaScript
function createToast(message, type = 'success', dur = 5000) {
    console.log('Creating toast:', { message, type, dur }); // Debug log
    
    const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    console.log('Generated toast ID:', toastId); // Debug log
    
    const alertTypes = {
        'success': 'alert-success',
        'error': 'alert-error', 
        'info': 'alert-info',
        'warning': 'alert-warning'
    };
    
    const alertClass = alertTypes[type] || 'alert-info';
    
    const toastHTML = `
        <div id="${toastId}" class="alert ${alertClass} mb-2 flex items-center justify-between shadow-lg">
            <div class="flex items-center">
                <i data-lucide="${type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : type === 'warning' ? 'alert-triangle' : 'info'}" class="w-5 h-5 mr-2"></i>
                <span>${message}</span>
            </div>
            <button onclick="window.dismissToast('${toastId}')" class="btn btn-sm btn-ghost">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        </div>
    `;
    
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed top-4 right-4 z-50 max-w-md';
        document.body.appendChild(toastContainer);
        console.log('Created toast container'); // Debug log
    }
    
    toastContainer.insertAdjacentHTML('afterbegin', toastHTML);
    console.log('Toast inserted into container'); // Debug log
    
    if (window.lucide) {
        window.lucide.createIcons();
    }
    
    // Auto dismiss after specified duration
    if (dur > 0) {
        setTimeout(function() {
            console.log('Auto-dismissing toast after', dur, 'ms'); // Debug log
            window.dismissToast(toastId);
        }, dur);
    }
    
    return toastId;
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast toast-top toast-end z-50';
    document.body.appendChild(container);
    return container;
}

// Utility functions for common toast types
window.toastSuccess = function(message, duration) {
    createToast(message, 'success', duration);
};

window.toastError = function(message, duration) {
    createToast(message, 'error', duration);
};

window.toastWarning = function(message, duration) {
    createToast(message, 'warning', duration);
};

window.toastInfo = function(message, duration) {
    createToast(message, 'info', duration);
};
