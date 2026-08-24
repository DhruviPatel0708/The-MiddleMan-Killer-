/**
 * THE MIDDLEMAN KILLER - Chart.js Data Visualizations
 */

window.MKCharts = {
    farmerMarketChart: null,
    adminGrowthChart: null,
    adminRegionalChart: null,

    initFarmerCharts() {
        const ctx = document.getElementById('farmerMarketChart');
        if (!ctx) return;

        if (this.farmerMarketChart) this.farmerMarketChart.destroy();

        this.farmerMarketChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['May', 'Jun', 'Jul', 'Aug 01', 'Aug 08', 'Aug 15', 'Aug 22 (Today)'],
                datasets: [
                    {
                        label: 'AI Fair Price (₹/Q)',
                        data: [2450, 2580, 2690, 2750, 2810, 2835, 2890],
                        borderColor: '#D6A84F',
                        backgroundColor: 'rgba(214, 168, 79, 0.15)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#D6A84F'
                    },
                    {
                        label: 'Traditional Intermediary Price (₹/Q)',
                        data: [2100, 2150, 2200, 2280, 2310, 2400, 2420],
                        borderColor: '#82957D',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#F4EFE4', font: { family: 'Plus Jakarta Sans' } } },
                    tooltip: { backgroundColor: '#0B2119', titleColor: '#D6A84F', bodyColor: '#F4EFE4' }
                },
                scales: {
                    x: { ticks: { color: '#A3B19B' }, grid: { color: 'rgba(130, 149, 125, 0.1)' } },
                    y: { ticks: { color: '#A3B19B' }, grid: { color: 'rgba(130, 149, 125, 0.1)' } }
                }
            }
        });
    },

    initAdminCharts() {
        const ctxGrowth = document.getElementById('adminGrowthChart');
        if (ctxGrowth) {
            if (this.adminGrowthChart) this.adminGrowthChart.destroy();
            this.adminGrowthChart = new Chart(ctxGrowth, {
                type: 'bar',
                data: {
                    labels: ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026', 'Q2 2026', 'Q3 2026'],
                    datasets: [
                        {
                            label: 'Direct Trade Volume (₹ Crores)',
                            data: [12.4, 28.6, 45.2, 68.9, 94.1, 122.5, 142.8],
                            backgroundColor: '#D96C3B',
                            borderRadius: 8
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#F4EFE4' } }
                    },
                    scales: {
                        x: { ticks: { color: '#A3B19B' }, grid: { display: false } },
                        y: { ticks: { color: '#A3B19B' }, grid: { color: 'rgba(130, 149, 125, 0.1)' } }
                    }
                }
            });
        }

        const ctxRegional = document.getElementById('adminRegionalChart');
        if (ctxRegional) {
            if (this.adminRegionalChart) this.adminRegionalChart.destroy();
            this.adminRegionalChart = new Chart(ctxRegional, {
                type: 'doughnut',
                data: {
                    labels: ['Rajkot (Groundnut)', 'Ahmedabad (Cotton)', 'Mehsana (Mustard)', 'Anand (Tobacco/Maize)', 'Junagadh (Mango)'],
                    datasets: [{
                        data: [32.1, 18.4, 21.5, 16.9, 26.4],
                        backgroundColor: ['#D6A84F', '#D96C3B', '#12372A', '#82957D', '#2ECC71'],
                        borderWidth: 2,
                        borderColor: '#101411'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#F4EFE4' } }
                    }
                }
            });
        }
    }
};
