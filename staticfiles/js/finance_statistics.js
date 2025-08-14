document.addEventListener('DOMContentLoaded', function() {
    // Function to load a single graph
    async function loadGraph(config) {
        const container = document.getElementById(config.id);
        if (!container) return;

        try {
            const response = await fetch(config.url, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (data.success && data.has_data && data.graph) {
                // Show the graph with click functionality
                container.innerHTML = `
                    <img src="data:image/png;base64,${data.graph}" 
                         alt="Gráfico ${config.type}" 
                         class="w-full h-auto max-h-[380px] object-contain chart-image"
                         onclick="openZoomModal(this.src, this.alt)">
                `;
            } else {
                // Show no data message
                container.innerHTML = `
                    <div class="no-data-placeholder" onclick="refreshGraph('${config.id}')">
                        <i data-lucide="image" class="w-16 h-16 mx-auto mb-4 opacity-30"></i>
                        <p>Gráfico não disponível</p>
                        <p class="text-sm">Dados insuficientes para gerar o gráfico</p>
                        <p class="text-xs mt-2 opacity-60">Clique para tentar novamente</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error(`Error loading graph ${config.type}:`, error);
            container.innerHTML = `
                <div class="error-placeholder" onclick="refreshGraph('${config.id}')">
                    <i data-lucide="alert-circle" class="w-16 h-16 mx-auto mb-4"></i>
                    <p>Erro ao carregar gráfico</p>
                    <p class="text-sm">Clique para tentar novamente</p>
                    <div class="mt-3">
                        <button class="btn btn-sm btn-outline" onclick="event.stopPropagation(); refreshGraph('${config.id}')">
                            <i data-lucide="refresh-cw" class="w-4 h-4 mr-1"></i>
                            Tentar Novamente
                        </button>
                    </div>
                </div>
            `;
        }

        // Re-initialize Lucide icons for new content
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    // Function to refresh a specific graph
    window.refreshGraph = function(containerId) {
        const config = graphConfigs.find(g => g.id === containerId);
        if (config) {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = `
                    <div class="loading-placeholder text-center">
                        <div class="loading loading-spinner loading-lg text-primary mb-4"></div>
                        <p class="text-base-content/70">Recarregando gráfico...</p>
                    </div>
                `;
            }
            setTimeout(() => loadGraph(config), 300);
        }
    };

    // Function to open zoom modal
    window.openZoomModal = function(imageSrc, imageAlt) {
        const modal = document.getElementById('zoomModal');
        const image = document.getElementById('zoomedImage');
        
        if (modal && image) {
            image.src = imageSrc;
            image.alt = imageAlt;
            modal.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }
    };

    // Function to close zoom modal
    window.closeZoomModal = function() {
        const modal = document.getElementById('zoomModal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = ''; // Restore scrolling
        }
    };

    // Close modal when clicking outside the image
    document.getElementById('zoomModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeZoomModal();
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeZoomModal();
        }
    });

    // Load graphs with staggered timing to prevent server overload
    graphConfigs.forEach((config, index) => {
        setTimeout(() => {
            loadGraph(config);
        }, index * 500); // 500ms delay between each graph load
    });

    // Add refresh functionality for all graphs
    window.refreshAllGraphs = function() {
        graphConfigs.forEach((config, index) => {
            const container = document.getElementById(config.id);
            if (container) {
                container.innerHTML = `
                    <div class="loading-placeholder text-center">
                        <div class="loading loading-spinner loading-lg text-primary mb-4"></div>
                        <p class="text-base-content/70">Recarregando gráfico...</p>
                    </div>
                `;
            }
            
            setTimeout(() => {
                loadGraph(config);
            }, index * 300);
        });
    };
});