// Mobile Sidebar Navigation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initSidebarNavigation();
    initMobileDrawer();
    initTouchGestures();
    setActiveNavigation();
});

function initSidebarNavigation() {
    // Auto-close mobile drawer when clicking on navigation links
    const navLinks = document.querySelectorAll('.drawer-side a');
    const drawerToggle = document.getElementById('mobile-drawer');
    
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (drawerToggle && window.innerWidth < 1024) {
                drawerToggle.checked = false;
            }
        });
    });
    
    // Handle submenu toggles on mobile
    const submenuToggles = document.querySelectorAll('.submenu-toggle');
    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const submenu = this.nextElementSibling;
            const isOpen = submenu.classList.contains('submenu-open');
            
            // Close all other submenus
            document.querySelectorAll('.submenu-open').forEach(menu => {
                menu.classList.remove('submenu-open');
            });
            
            // Toggle current submenu
            if (!isOpen) {
                submenu.classList.add('submenu-open');
                this.classList.add('submenu-open');
            } else {
                submenu.classList.remove('submenu-open');
                this.classList.remove('submenu-open');
            }
        });
    });
}

function initMobileDrawer() {
    const drawerToggle = document.getElementById('mobile-drawer');
    const drawerOverlay = document.querySelector('.drawer-overlay');
    
    if (!drawerToggle) return;
    
    // Close drawer when clicking overlay
    if (drawerOverlay) {
        drawerOverlay.addEventListener('click', () => {
            drawerToggle.checked = false;
        });
    }
    
    // Close drawer on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && drawerToggle.checked) {
            drawerToggle.checked = false;
        }
    });
    
    // Handle drawer state changes
    drawerToggle.addEventListener('change', function() {
        if (this.checked) {
            document.body.style.overflow = 'hidden';
            document.body.classList.add('drawer-open');
        } else {
            document.body.style.overflow = '';
            document.body.classList.remove('drawer-open');
        }
    });
    
    // Auto-close on window resize if switching to desktop
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (window.innerWidth >= 1024 && drawerToggle.checked) {
                drawerToggle.checked = false;
            }
        }, 250);
    });
}

function initTouchGestures() {
    if (!('ontouchstart' in window)) return;
    
    const drawerToggle = document.getElementById('mobile-drawer');
    const drawer = document.querySelector('.drawer-side');
    
    if (!drawer || !drawerToggle) return;
    
    let startX = 0;
    let currentX = 0;
    let isDragging = false;
    let initialDrawerState = false;
    
    // Touch start
    document.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        initialDrawerState = drawerToggle.checked;
        
        // Only start drag if we're at the edge or drawer is open
        if (startX < 20 || initialDrawerState) {
            isDragging = true;
        }
    }, { passive: true });
    
    // Touch move
    document.addEventListener('touchmove', function(e) {
        if (!isDragging) return;
        
        currentX = e.touches[0].clientX;
        const diffX = currentX - startX;
        
        // Prevent default scroll if we're dragging horizontally
        if (Math.abs(diffX) > 10) {
            e.preventDefault();
        }
        
        // Show visual feedback
        if (!initialDrawerState && diffX > 50) {
            // Swiping right to open
            drawer.style.transform = `translateX(${Math.min(diffX - 256, 0)}px)`;
        } else if (initialDrawerState && diffX < -50) {
            // Swiping left to close
            drawer.style.transform = `translateX(${Math.max(diffX, -256)}px)`;
        }
    }, { passive: false });
    
    // Touch end
    document.addEventListener('touchend', function(e) {
        if (!isDragging) return;
        
        isDragging = false;
        const diffX = currentX - startX;
        
        // Reset transform
        drawer.style.transform = '';
        
        // Determine if we should toggle the drawer
        if (!initialDrawerState && diffX > 100) {
            // Swipe right to open
            drawerToggle.checked = true;
        } else if (initialDrawerState && diffX < -100) {
            // Swipe left to close
            drawerToggle.checked = false;
        }
        
        // Reset values
        startX = 0;
        currentX = 0;
    }, { passive: true });
}

function setActiveNavigation() {
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
    
    // Apply active classes with error checking
    for (let j = 0; j < sideListItems.length; j++) {
        try {
            if (is_active1 && sideListItems[j].children[1] && sideListItems[j].children[1].children[0]) {
                const actual = sideListItems[j].children[1].children[0];
                actual.classList.add("bg-primary", "text-primary-content");
            }
            if (is_active2 && sideListItems[j].children[1] && sideListItems[j].children[1].children[1]) {
                const submenu = sideListItems[j].children[1].children[1];
                if (submenu.children[0] && submenu.children[0].children[0]) {
                    const actual = submenu.children[0].children[0];
                    actual.classList.add("bg-secondary", "text-secondary-content");
                }
            }
            if (is_active3 && sideListItems[j].children[1] && sideListItems[j].children[1].children[1]) {
                const submenu = sideListItems[j].children[1].children[1];
                if (submenu.children[1] && submenu.children[1].children[0]) {
                    const actual = submenu.children[1].children[0];
                    actual.classList.add("bg-secondary", "text-secondary-content");
                }
            }
        } catch (error) {
            console.warn('Error setting active navigation:', error);
        }
    }
}

// Utility functions
window.sidebarUtils = {
    isMobile: function() {
        return window.innerWidth < 1024;
    },
    
    isTouch: function() {
        return 'ontouchstart' in window;
    },
    
    closeDrawer: function() {
        const drawerToggle = document.getElementById('mobile-drawer');
        if (drawerToggle) {
            drawerToggle.checked = false;
        }
    },
    
    openDrawer: function() {
        const drawerToggle = document.getElementById('mobile-drawer');
        if (drawerToggle && this.isMobile()) {
            drawerToggle.checked = true;
        }
    },
    
    toggleDrawer: function() {
        const drawerToggle = document.getElementById('mobile-drawer');
        if (drawerToggle && this.isMobile()) {
            drawerToggle.checked = !drawerToggle.checked;
        }
    }
};

// Handle back button on mobile
window.addEventListener('popstate', function() {
    if (window.sidebarUtils.isMobile()) {
        window.sidebarUtils.closeDrawer();
    }
});

// Performance optimization: debounce resize events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Optimized resize handler
const handleResize = debounce(() => {
    const drawerToggle = document.getElementById('mobile-drawer');
    if (window.innerWidth >= 1024 && drawerToggle && drawerToggle.checked) {
        drawerToggle.checked = false;
    }
}, 250);

window.addEventListener('resize', handleResize);
