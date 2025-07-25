/* VetAI Real-time Notifications and Live Updates */

class VetAINotifications {
    constructor() {
        this.notifications = [];
        this.maxNotifications = 5;
        this.init();
    }

    init() {
        this.createNotificationContainer();
        this.setupAutoRefresh();
        this.setupWebSocket();
    }

    createNotificationContainer() {
        if (document.getElementById('notification-container')) return;
        
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            width: 350px;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }

    show(message, type = 'info', duration = 5000) {
        const notification = this.createNotification(message, type, duration);
        this.addNotification(notification);
        this.animateIn(notification);
        
        if (duration > 0) {
            setTimeout(() => this.remove(notification), duration);
        }
        
        return notification;
    }

    createNotification(message, type, duration) {
        const notification = document.createElement('div');
        const id = 'notification-' + Date.now();
        notification.id = id;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle',
            prediction: 'fas fa-brain',
            system: 'fas fa-cog'
        };
        
        const colors = {
            success: '#51cf66',
            error: '#ff6b6b',
            warning: '#feca57',
            info: '#74c0fc',
            prediction: '#667eea',
            system: '#6c757d'
        };
        
        notification.style.cssText = `
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            border-left: 4px solid ${colors[type] || colors.info};
            transform: translateX(100%);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            pointer-events: auto;
            opacity: 0;
        `;
        
        notification.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="flex-shrink-0">
                    <i class="${icons[type] || icons.info}" style="color: ${colors[type] || colors.info}; font-size: 1.2rem;"></i>
                </div>
                <div class="flex-grow-1 ms-3">
                    <div style="font-weight: 600; color: #2c3e50; margin-bottom: 0.25rem;">
                        ${this.getTypeLabel(type)}
                    </div>
                    <div style="color: #6c757d; font-size: 0.9rem; line-height: 1.4;">
                        ${message}
                    </div>
                    ${duration > 0 ? `
                        <div style="width: 100%; height: 2px; background: #e9ecef; border-radius: 1px; margin-top: 0.5rem; overflow: hidden;">
                            <div style="height: 100%; background: ${colors[type] || colors.info}; width: 100%; animation: shrink ${duration}ms linear;"></div>
                        </div>
                    ` : ''}
                </div>
                <button onclick="window.vetaiNotifications.remove(this.parentElement.parentElement)" 
                        style="background: none; border: none; color: #6c757d; font-size: 1.1rem; cursor: pointer; padding: 0; margin-left: 0.5rem;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Add shrink animation
        if (!document.getElementById('notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                @keyframes shrink {
                    from { width: 100%; }
                    to { width: 0%; }
                }
                .notification-shake {
                    animation: shake 0.5s ease-in-out;
                }
                @keyframes shake {
                    0%, 100% { transform: translateX(0); }
                    25% { transform: translateX(-5px); }
                    75% { transform: translateX(5px); }
                }
            `;
            document.head.appendChild(styles);
        }
        
        return notification;
    }

    getTypeLabel(type) {
        const labels = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information',
            prediction: 'Prediction Complete',
            system: 'System Update'
        };
        return labels[type] || 'Notification';
    }

    addNotification(notification) {
        const container = document.getElementById('notification-container');
        container.appendChild(notification);
        
        this.notifications.push(notification);
        
        // Remove old notifications if exceeding limit
        while (this.notifications.length > this.maxNotifications) {
            const oldest = this.notifications.shift();
            this.remove(oldest);
        }
    }

    animateIn(notification) {
        requestAnimationFrame(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        });
    }

    remove(notification) {
        if (!notification || !notification.parentElement) return;
        
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.parentElement.removeChild(notification);
            }
            this.notifications = this.notifications.filter(n => n !== notification);
        }, 300);
    }

    setupAutoRefresh() {
        // Auto-refresh data every 30 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/api/analytics');
                if (response.ok) {
                    const data = await response.json();
                    this.updateLiveStats(data);
                }
            } catch (error) {
                console.log('Auto-refresh error:', error);
            }
        }, 30000);
    }

    setupWebSocket() {
        // Simulate real-time updates (in real app, this would be WebSocket)
        this.simulateRealTimeUpdates();
    }

    simulateRealTimeUpdates() {
        // Show system status updates
        setTimeout(() => {
            this.show('VetAI system is running optimally', 'system', 3000);
        }, 2000);
        
        // Simulate periodic health tips
        const healthTips = [
            'Regular vaccination is key to preventing livestock diseases',
            'Monitor animal temperature daily for early disease detection',
            'Maintain proper ventilation in animal housing',
            'Quarantine new animals for 21 days before introducing to herd',
            'Clean water sources help prevent many livestock diseases'
        ];
        
        let tipIndex = 0;
        setInterval(() => {
            this.show(healthTips[tipIndex], 'info', 8000);
            tipIndex = (tipIndex + 1) % healthTips.length;
        }, 45000);
    }

    updateLiveStats(data) {
        // Update live statistics in the interface
        const event = new CustomEvent('vetai-stats-update', { detail: data });
        document.dispatchEvent(event);
    }

    // Predefined notification methods
    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 8000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }

    prediction(message, duration = 7000) {
        return this.show(message, 'prediction', duration);
    }

    system(message, duration = 4000) {
        return this.show(message, 'system', duration);
    }
}

// Live Statistics Updater
class VetAILiveStats {
    constructor() {
        this.updateInterval = 15000; // 15 seconds
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startLiveUpdates();
    }

    setupEventListeners() {
        document.addEventListener('vetai-stats-update', (event) => {
            this.updateDisplay(event.detail);
        });
    }

    startLiveUpdates() {
        setInterval(async () => {
            await this.fetchAndUpdateStats();
        }, this.updateInterval);
    }

    async fetchAndUpdateStats() {
        try {
            const [analytics, predictionStats] = await Promise.all([
                fetch('/api/analytics').then(r => r.json()),
                fetch('/api/prediction-stats').then(r => r.json())
            ]);

            this.updateDisplay({ analytics, predictionStats });
        } catch (error) {
            console.error('Error fetching live stats:', error);
        }
    }

    updateDisplay(data) {
        // Update counters with animation
        this.animateCounter('total-predictions', data.analytics?.total_predictions || 0);
        this.animateCounter('avg-confidence', Math.round(data.predictionStats?.average_confidence || 0));
        
        // Update charts if available
        if (window.vetaiCharts && data.analytics) {
            window.vetaiCharts.updateCharts(data.analytics);
        }
    }

    animateCounter(elementId, newValue) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const currentValue = parseInt(element.textContent) || 0;
        const increment = (newValue - currentValue) / 20;
        
        if (Math.abs(increment) < 1) return;
        
        let current = currentValue;
        const timer = setInterval(() => {
            current += increment;
            
            if ((increment > 0 && current >= newValue) || (increment < 0 && current <= newValue)) {
                current = newValue;
                clearInterval(timer);
            }
            
            element.textContent = Math.round(current);
            
            // Add pulse effect for significant changes
            if (Math.abs(newValue - currentValue) > 5) {
                element.classList.add('pulse');
                setTimeout(() => element.classList.remove('pulse'), 1000);
            }
        }, 50);
    }
}

// Progressive Web App features
class VetAIPWA {
    constructor() {
        this.init();
    }

    init() {
        this.setupServiceWorker();
        this.setupInstallPrompt();
        this.setupOfflineDetection();
    }

    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/sw.js')
                .then(registration => {
                    console.log('SW registered:', registration);
                })
                .catch(error => {
                    console.log('SW registration failed:', error);
                });
        }
    }

    setupInstallPrompt() {
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            
            // Show install button
            this.showInstallPrompt(deferredPrompt);
        });
    }

    showInstallPrompt(deferredPrompt) {
        if (window.vetaiNotifications) {
            const notification = window.vetaiNotifications.show(
                'Install VetAI as an app for offline access and better performance. <button onclick="window.vetaiPWA.installApp()" class="btn btn-sm btn-primary ms-2">Install</button>',
                'info',
                0
            );
            
            window.vetaiPWA.deferredPrompt = deferredPrompt;
        }
    }

    async installApp() {
        if (!this.deferredPrompt) return;
        
        this.deferredPrompt.prompt();
        const result = await this.deferredPrompt.userChoice;
        
        if (result.outcome === 'accepted') {
            window.vetaiNotifications.success('VetAI app installed successfully!');
        }
        
        this.deferredPrompt = null;
    }

    setupOfflineDetection() {
        window.addEventListener('online', () => {
            if (window.vetaiNotifications) {
                window.vetaiNotifications.success('Connection restored! All features available.');
            }
        });

        window.addEventListener('offline', () => {
            if (window.vetaiNotifications) {
                window.vetaiNotifications.warning('You are offline. Some features may be limited.');
            }
        });
    }
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.vetaiNotifications = new VetAINotifications();
    window.vetaiLiveStats = new VetAILiveStats();
    window.vetaiPWA = new VetAIPWA();
    
    console.log('🎉 VetAI Live Features Initialized!');
    
    // Welcome message
    setTimeout(() => {
        window.vetaiNotifications.success('Welcome to VetAI! Real-time updates are now active.');
    }, 1000);
});

// Export for global access
window.VetAINotifications = VetAINotifications;
window.VetAILiveStats = VetAILiveStats;
window.VetAIPWA = VetAIPWA;
