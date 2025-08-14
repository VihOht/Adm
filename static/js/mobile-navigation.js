// Mobile Navigation and Responsive Behaviors

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile navigation
    initMobileNavigation();
    
    // Initialize responsive behaviors
    initResponsiveBehaviors();
    
    // Initialize touch gestures
    initTouchGestures();
});

function initMobileNavigation() {
    // Set active navigation items based on current URL
    const sideListItems = document.getElementsByClassName("s_items");
    const currentUrl = window.location.pathname;
    
    const transacoes_ref = ["/finance/", "/finance/statistics/calendar/", "/finance/statistics/", "/finance/transactions/"];
    const ver_transacoes_ref = ["/finance/statistics/calendar/", "/finance/transactions/"];
    const relatorios_ref = ["/finance/statistics/"];
    
    let is_active1 = false;
    let is_active2 = false;
    let is_active3 = false;
    
    // Check which section is active
    for (let k = 0; k < transacoes_ref.length; k++) {
        if (transacoes_ref[k] === currentUrl) {
            is_active1 = true;
        }
    }
    for (let k = 0; k < ver_transacoes_ref.length; k++) {
        if (ver_transacoes_ref[k] === currentUrl) {
            is_active2 = true;
        }
    }
    for (let k = 0; k < relatorios_ref.length; k++) {
        if (relatorios_ref[k] === currentUrl) {
            is_active3 = true;
        }
    }
    
    // Apply active classes
    for (let j = 0; j < sideListItems.length; j++) {
        if (is_active1 && sideListItems[j].children[1] && sideListItems[j].children[1].children[0]) {
            const actual = sideListItems[j].children[1].children[0];
            actual.classList.add("bg-primary", "text-primary-content");
        }
        if (is_active2 && sideListItems[j].children[1] && sideListItems[j].children[1].children[1]) {
            const actual = sideListItems[j].children[1].children[1].children[0].children[0];
            actual.classList.add("bg-secondary", "text-secondary-content");
        }
        if (is_active3 && sideListItems[j].children[1] && sideListItems[j].children[1].children[1]) {
            const actual = sideListItems[j].children[1].children[1].children[1].children[0];
            actual.classList.add("bg-secondary", "text-secondary-content");
        }
    }
    
    // Auto-close mobile drawer when navigating
    const drawerToggle = document.getElementById('mobile-drawer');
    const navLinks = document.querySelectorAll('.drawer-side a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (drawerToggle) {
                drawerToggle.checked = false;
            }
        });
    });
}

function initResponsiveBehaviors() {
    // Handle viewport changes
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            handleViewportChange();
        }, 250);
    });
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(handleViewportChange, 100);
    });
    
    // Initial viewport setup
    handleViewportChange();
}

function handleViewportChange() {
    const viewport = window.innerWidth;
    const isMobile = viewport < 768;
    const isTablet = viewport >= 768 && viewport < 1024;
    const isDesktop = viewport >= 1024;
    
    // Adjust modal sizes
    const modals = document.querySelectorAll('.modal-box');
    modals.forEach(modal => {
        if (isMobile) {
            modal.style.maxWidth = 'calc(100vw - 1rem)';
            modal.style.margin = '0.5rem';
        } else {
            modal.style.maxWidth = '';
            modal.style.margin = '';
        }
    });
    
    // Adjust table responsiveness
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        const container = table.closest('.overflow-x-auto');
        if (container) {
            if (isMobile) {
                container.style.overflowX = 'auto';
                container.style.webkitOverflowScrolling = 'touch';
            }
        }
    });
    
    // Adjust card layouts
    const cardGrids = document.querySelectorAll('.grid');
    cardGrids.forEach(grid => {
        if (isMobile) {
            grid.classList.remove('md:grid-cols-2', 'lg:grid-cols-3', 'lg:grid-cols-4');
            grid.classList.add('grid-cols-1');
        }
    });
}

function initTouchGestures() {
    if (!('ontouchstart' in window)) return;
    
    // Swipe to close modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        let startY = 0;
        let currentY = 0;
        
        modal.addEventListener('touchstart', function(e) {
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        modal.addEventListener('touchmove', function(e) {
            currentY = e.touches[0].clientY;
        }, { passive: true });
        
        modal.addEventListener('touchend', function() {
            const diffY = startY - currentY;
            
            // Swipe down to close
            if (diffY < -100) {
                const closeButton = modal.querySelector('[onclick*="close"]');
                if (closeButton) {
                    closeButton.click();
                }
            }
        }, { passive: true });
    });
    
    // Improve touch feedback for buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
        }, { passive: true });
        
        button.addEventListener('touchend', function() {
            this.style.transform = '';
        }, { passive: true });
    });
    
    // Prevent double-tap zoom on buttons
    buttons.forEach(button => {
        button.addEventListener('touchend', function(e) {
            e.preventDefault();
            e.target.click();
        });
    });
}

// Utility functions for mobile optimization
window.mobileUtils = {
    isMobile: function() {
        return window.innerWidth < 768;
    },
    
    isTouch: function() {
        return 'ontouchstart' in window;
    },
    
    disableHover: function() {
        if (this.isTouch()) {
            document.body.classList.add('touch-device');
        }
    },
    
    optimizeImages: function() {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            if (this.isMobile()) {
                img.loading = 'lazy';
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
            }
        });
    },
    
    preventZoom: function() {
        // Prevent zoom on input focus for iOS
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.type !== 'file') {
                input.style.fontSize = '16px';
            }
        });
    }
};

// Initialize mobile utilities
window.addEventListener('load', function() {
    window.mobileUtils.disableHover();
    window.mobileUtils.optimizeImages();
    window.mobileUtils.preventZoom();
});

// Handle back button on mobile
window.addEventListener('popstate', function() {
    // Close any open modals when using back button
    const openModals = document.querySelectorAll('.modal.modal-open, .modal-open');
    openModals.forEach(modal => {
        const closeButton = modal.querySelector('[onclick*="close"]');
        if (closeButton) {
            closeButton.click();
        }
    });
});
