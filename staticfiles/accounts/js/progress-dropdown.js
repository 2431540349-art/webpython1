document.addEventListener('DOMContentLoaded', function() {
    // Initialize progress menu
    function initProgressMenu() {
        const menu = document.querySelector('.progress-menu');
        const link = menu.querySelector('.progress-label-link');
        const dropdown = menu.querySelector('.progress-dropdown');
        const viewToggles = menu.querySelectorAll('.progress-view-toggle button');
        const chart = menu.querySelector('.progress-chart');
        const list = menu.querySelector('.progress-dropdown-list');

        // Toggle dropdown
        link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
            
            if (dropdown.style.display === 'block') {
                initializeProgressBars();
                if (chart) initializeChart();
            }
        });

        // Close on outside click
        document.addEventListener('click', function(e) {
            if (!menu.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });

        // View toggle
        if (viewToggles) {
            viewToggles.forEach(btn => {
                btn.addEventListener('click', function() {
                    viewToggles.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    
                    if (btn.dataset.view === 'chart') {
                        list.style.display = 'none';
                        chart.style.display = 'block';
                        initializeChart();
                    } else {
                        chart.style.display = 'none';
                        list.style.display = 'flex';
                    }
                });
            });
        }
    }

    // Initialize progress bars
    function initializeProgressBars() {
        document.querySelectorAll('.progress-item-fill').forEach(fill => {
            const width = fill.style.width;
            fill.style.width = '0%';
            setTimeout(() => {
                fill.style.width = width;
            }, 50);
        });
    }

    // Initialize chart if Chart.js is available
    function initializeChart() {
        if (!window.Chart || !document.getElementById('progressChart')) return;

        const items = document.querySelectorAll('.progress-item');
        const titles = Array.from(items).map(item => 
            item.querySelector('.progress-item-title').textContent
        );
        const percentages = Array.from(items).map(item => 
            parseInt(item.querySelector('.progress-item-percent').textContent)
        );

        const ctx = document.getElementById('progressChart').getContext('2d');
        
        if (window.progressChart) {
            window.progressChart.destroy();
        }

        window.progressChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: titles,
                datasets: [{
                    label: 'Tiến độ hoàn thành',
                    data: percentages,
                    backgroundColor: 'rgba(29, 185, 84, 0.6)',
                    borderColor: '#1db954',
                    borderWidth: 1,
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: value => `${value}%`
                        }
                    }
                }
            }
        });
    }

    // Start initialization
    initProgressMenu();
});