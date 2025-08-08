// Toast Messages System for VihOhtLife
// Auto dismiss toasts after dur miliseconds and handle manual dismissal
dur = 2000

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
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.style.transition = 'all 0.3s ease-out';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        
        setTimeout(function() {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 300);
    }
}

// Function to manually create toast messages via JavaScript
function createToast(message, type = 'info', duration = dur) {
    const toastContainer = document.querySelector('.toast') || createToastContainer();
    const toastId = 'toast-' + Date.now();
    
    // Icon mapping
    const icons = {
        success: 'check-circle',
        error: 'x-circle', 
        warning: 'alert-triangle',
        info: 'info'
    };
    
    const toastHTML = `
        <div class="alert alert-${type} shadow-lg animate-fade-in" id="${toastId}">
            <div class="flex items-center">
                <i data-lucide="${icons[type] || 'info'}" class="w-5 h-5 mr-2"></i>
                <span>${message}</span>
                <button onclick="dismissToast('${toastId}')" class="btn btn-ghost btn-xs ml-2">
                    <i data-lucide="x" class="w-3 h-3"></i>
                </button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // Refresh icons for the new toast
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Auto dismiss
    setTimeout(function() {
        dismissToast(toastId);
    }, duration);
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
