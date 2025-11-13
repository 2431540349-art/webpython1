document.addEventListener('DOMContentLoaded', function() {
    // Set current nav link as active
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Progress dropdown functionality (guarded)
    const progressMenu = document.querySelector('.progress-menu');
    if (progressMenu) {
        const progressLink = progressMenu.querySelector('.progress-label-link');
        const progressDropdown = progressMenu.querySelector('.progress-dropdown');

        // If there is no dropdown element (we simplified nav), do nothing further
        if (!progressDropdown || !progressLink) {
            // keep simple link behavior (no dropdown)
        } else {
            // Toggle dropdown
            progressLink.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const isOpen = progressDropdown.style.display === 'block';
                progressMenu.classList.toggle('active', !isOpen);
                progressDropdown.style.display = isOpen ? 'none' : 'block';

                if (!isOpen) {
                    initializeProgress();
                }
            });

            // Close on outside click
            document.addEventListener('click', function(e) {
                if (!progressMenu.contains(e.target)) {
                    progressMenu.classList.remove('active');
                    progressDropdown.style.display = 'none';
                }
            });
        }
    }

    // Initialize progress items
    function initializeProgress() {
        const items = document.querySelectorAll('.progress-item-fill');
        items.forEach(fill => {
            const width = fill.style.width;
            fill.style.width = '0%';
            setTimeout(() => {
                fill.style.width = width;
            }, 50);
        });
    }

    // View toggle functionality
    const viewToggles = document.querySelectorAll('.progress-view-toggle button');
    const chartView = document.querySelector('.progress-chart');
    const listView = document.querySelector('.progress-dropdown-list');

    if (viewToggles.length && chartView && listView) {
        viewToggles.forEach(btn => {
            btn.addEventListener('click', function() {
                viewToggles.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                if (btn.dataset.view === 'chart') {
                    listView.style.display = 'none';
                    chartView.style.display = 'block';
                    initializeChart();
                } else {
                    chartView.style.display = 'none';
                    listView.style.display = 'flex';
                }
            });
        });
    }

    // Initialize chart
    function initializeChart() {
        if (!window.Chart || !document.getElementById('progressChart')) return;

        const items = document.querySelectorAll('.progress-item');
        const data = {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: 'rgba(29, 185, 84, 0.6)',
                borderColor: '#1db954',
                borderWidth: 1,
                borderRadius: 4,
            }]
        };

        items.forEach(item => {
            const title = item.querySelector('.progress-item-title').textContent;
            const percent = parseInt(item.querySelector('.progress-item-percent').textContent);
            data.labels.push(title);
            data.datasets[0].data.push(percent);
        });

        if (window.progressChart) {
            window.progressChart.destroy();
        }

        window.progressChart = new Chart(
            document.getElementById('progressChart').getContext('2d'),
            {
                type: 'bar',
                data: data,
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
                            grid: {
                                color: 'rgba(0,0,0,0.05)'
                            },
                            ticks: {
                                callback: value => `${value}%`
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            }
        );
    }
});

// Expose toggle functions globally so templates with inline onclick can use them
window.toggleSidebar = function() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.toggle('show');
};

window.toggleProfileDropdown = function() {
    const dd = document.getElementById('profileDropdown');
    if (dd) dd.classList.toggle('show-dropdown');
};

// Close sidebar/profile dropdown when clicking navigation links to ensure they are responsive
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', function () {
            const sidebar = document.getElementById('sidebar');
            const dd = document.getElementById('profileDropdown');
            if (sidebar) sidebar.classList.remove('show');
            if (dd) dd.classList.remove('show-dropdown');
        });
    });
});

// Close profile dropdown when clicking outside the profile area
document.addEventListener('click', function (e) {
    const profileEl = document.querySelector('.profile');
    const dd = document.getElementById('profileDropdown');
    if (!dd) return;
    if (profileEl && !profileEl.contains(e.target)) {
        dd.classList.remove('show-dropdown');
    }
});

// Also attach handlers to menu-toggle and profile elements directly so clicks work even
// if inline onclick handlers are not yet bound or scripts load late.
document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.querySelector('.menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function (e) {
            e.preventDefault();
            window.toggleSidebar();
        });
    }

    const profileEl = document.querySelector('.profile');
    if (profileEl) {
        profileEl.addEventListener('click', function (e) {
            // allow clicks on inner links to function normally
            const target = e.target;
            if (target.tagName.toLowerCase() === 'a') return;
            window.toggleProfileDropdown();
        });
    }
});