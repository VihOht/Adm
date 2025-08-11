// Chart Modal Functionality
// Handles fullscreen chart viewing

document.addEventListener('DOMContentLoaded', function() {
    initializeChartModals();
});

function initializeChartModals() {
    // Add click listeners to all chart images
    const chartImages = document.querySelectorAll('.graph-container img');
    
    chartImages.forEach(function(img) {
        // Make images clickable
        img.style.cursor = 'pointer';
        img.style.transition = 'transform 0.2s ease';
        
        // Add hover effect
        img.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
        });
        
        img.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
        
        // Add click handler
        img.addEventListener('click', function() {
            openChartModal(this);
        });
    });
    
    // Add click listener to placeholder areas
    const placeholders = document.querySelectorAll('.graph-container .text-center');
    placeholders.forEach(function(placeholder) {
        const img = placeholder.closest('.graph-container').querySelector('img');
        if (img) {
            placeholder.style.cursor = 'pointer';
            placeholder.addEventListener('click', function() {
                openChartModal(img);
            });
        }
    });
}

function openChartModal(imgElement) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.id = 'chart-modal';
    modal.className = 'fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4';
    modal.style.animation = 'fadeIn 0.3s ease';
    
    // Create modal content
    const modalContent = document.createElement('div');
    modalContent.className = 'relative max-w-full max-h-full flex flex-col items-center';
    
    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'absolute -top-12 right-0 text-white hover:text-gray-300 transition-colors z-10';
    closeBtn.innerHTML = '<i data-lucide="x" class="w-8 h-8"></i>';
    closeBtn.onclick = closeChartModal;
    
    // Create chart title
    const chartTitle = document.createElement('h3');
    chartTitle.className = 'text-white text-xl font-semibold mb-4 text-center';
    
    // Get title from the card
    const cardElement = imgElement.closest('.card');
    const titleElement = cardElement ? cardElement.querySelector('.card-title') : null;
    if (titleElement) {
        // Extract text content without icons
        const titleText = titleElement.textContent.trim();
        chartTitle.textContent = titleText;
    } else {
        chartTitle.textContent = 'Gráfico Financeiro';
    }
    
    // Create enlarged image
    const enlargedImg = document.createElement('img');
    enlargedImg.src = imgElement.src;
    enlargedImg.alt = imgElement.alt;
    enlargedImg.className = 'max-w-full max-h-[80vh] object-contain rounded-lg shadow-2xl';
    enlargedImg.style.animation = 'zoomIn 0.3s ease';
    
    // Create download button
    const downloadBtn = document.createElement('button');
    downloadBtn.className = 'mt-4 btn btn-primary btn-sm';
    downloadBtn.innerHTML = '<i data-lucide="download" class="w-4 h-4 mr-2"></i>Baixar Gráfico';
    downloadBtn.onclick = function() {
        downloadChart(imgElement);
    };
    
    // Assemble modal
    modalContent.appendChild(closeBtn);
    modalContent.appendChild(chartTitle);
    modalContent.appendChild(enlargedImg);
    modalContent.appendChild(downloadBtn);
    modal.appendChild(modalContent);
    
    // Add to document
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
    
    // Initialize Lucide icons for the new elements
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Close modal on overlay click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeChartModal();
        }
    });
    
    // Close modal on Escape key
    document.addEventListener('keydown', handleEscapeKey);
}

function closeChartModal() {
    const modal = document.getElementById('chart-modal');
    if (modal) {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            modal.remove();
            document.body.style.overflow = '';
            document.removeEventListener('keydown', handleEscapeKey);
        }, 300);
    }
}

function handleEscapeKey(e) {
    if (e.key === 'Escape') {
        closeChartModal();
    }
}

function downloadChart(imgElement) {
    try {
        // Create a temporary link element
        const link = document.createElement('a');
        link.href = imgElement.src;
        
        // Get chart name from title
        const cardElement = imgElement.closest('.card');
        const titleElement = cardElement ? cardElement.querySelector('.card-title') : null;
        let filename = 'grafico-financeiro.png';
        
        if (titleElement) {
            const titleText = titleElement.textContent.trim()
                .replace(/[^a-zA-Z0-9\s]/g, '') // Remove special characters
                .replace(/\s+/g, '-') // Replace spaces with hyphens
                .toLowerCase();
            filename = `${titleText}.png`;
        }
        
        link.download = filename;
        link.target = '_blank';
        
        // Trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Show success message
        if (typeof toastSuccess !== 'undefined') {
            toastSuccess('Gráfico baixado com sucesso!');
        }
    } catch (error) {
        console.error('Error downloading chart:', error);
        if (typeof toastError !== 'undefined') {
            toastError('Erro ao baixar o gráfico.');
        }
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    
    @keyframes zoomIn {
        from { 
            opacity: 0; 
            transform: scale(0.8); 
        }
        to { 
            opacity: 1; 
            transform: scale(1); 
        }
    }
    
    /* Hover effect for clickable charts */
    .graph-container img:hover {
        filter: brightness(1.1);
    }
    
    /* Loading animation for chart modal */
    #chart-modal img {
        transition: opacity 0.3s ease;
    }
    
    /* Responsive modal */
    @media (max-width: 768px) {
        #chart-modal .relative {
            padding: 1rem;
        }
        
        #chart-modal h3 {
            font-size: 1.125rem;
            margin-bottom: 1rem;
        }
        
        #chart-modal img {
            max-height: 70vh;
        }
    }
`;
document.head.appendChild(style);