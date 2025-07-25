/* VetAI Advanced Charts and Visualizations */

class VetAICharts {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4ecdc4'],
            success: '#51cf66',
            warning: '#feca57',
            danger: '#ff6b6b',
            info: '#74c0fc'
        };
    }

    // Disease Distribution Pie Chart
    createDiseaseChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const chartData = {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: this.colors.primary,
                borderColor: '#fff',
                borderWidth: 3,
                hoverBorderWidth: 5
            }]
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    // Animal Type Bar Chart
    createAnimalChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const chartData = {
            labels: Object.keys(data).map(animal => animal.charAt(0).toUpperCase() + animal.slice(1)),
            datasets: [{
                label: 'Predictions',
                data: Object.values(data),
                backgroundColor: this.colors.primary[0],
                borderColor: this.colors.primary[1],
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { color: 'rgba(0,0,0,0.1)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    // Prediction Timeline Chart
    createTimelineChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        // Process data for timeline
        const timelineData = this.processTimelineData(data);

        const chartData = {
            labels: timelineData.labels,
            datasets: [{
                label: 'Predictions per Day',
                data: timelineData.data,
                borderColor: this.colors.primary[0],
                backgroundColor: this.colors.primary[0] + '20',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: this.colors.primary[0],
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    // Confidence Score Gauge
    createConfidenceGauge(canvasId, confidence) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const chartData = {
            datasets: [{
                data: [confidence, 100 - confidence],
                backgroundColor: [
                    confidence >= 80 ? this.colors.success :
                    confidence >= 60 ? this.colors.warning : this.colors.danger,
                    'rgba(0,0,0,0.1)'
                ],
                borderWidth: 0
            }]
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '80%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            },
            plugins: [{
                id: 'centerText',
                beforeDraw: (chart) => {
                    const { ctx, width, height } = chart;
                    ctx.restore();
                    const fontSize = (height / 180).toFixed(2);
                    ctx.font = `bold ${fontSize}em Arial`;
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#333';
                    const text = `${confidence}%`;
                    const textX = Math.round((width - ctx.measureText(text).width) / 2);
                    const textY = height / 2;
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            }]
        });
    }

    processTimelineData(data) {
        const last7Days = [];
        const counts = {};
        
        // Generate last 7 days
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const dateStr = date.toLocaleDateString();
            last7Days.push(dateStr);
            counts[dateStr] = 0;
        }

        // Count predictions per day
        data.forEach(prediction => {
            const date = new Date(prediction.timestamp).toLocaleDateString();
            if (counts.hasOwnProperty(date)) {
                counts[date]++;
            }
        });

        return {
            labels: last7Days.map(date => {
                const d = new Date(date);
                return d.toLocaleDateString('en-US', { weekday: 'short' });
            }),
            data: last7Days.map(date => counts[date])
        };
    }

    // Update all charts with new data
    updateCharts(analyticsData) {
        if (this.charts.diseaseChart) {
            this.charts.diseaseChart.data.datasets[0].data = Object.values(analyticsData.disease_distribution);
            this.charts.diseaseChart.update();
        }

        if (this.charts.animalChart) {
            this.charts.animalChart.data.datasets[0].data = Object.values(analyticsData.animal_distribution);
            this.charts.animalChart.update();
        }

        if (this.charts.timelineChart && analyticsData.recent_activity) {
            const timelineData = this.processTimelineData(analyticsData.recent_activity);
            this.charts.timelineChart.data.labels = timelineData.labels;
            this.charts.timelineChart.data.datasets[0].data = timelineData.data;
            this.charts.timelineChart.update();
        }
    }

    // Destroy all charts
    destroyCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

// Export for global access
window.VetAICharts = VetAICharts;
