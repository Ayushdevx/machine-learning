// VetAI Performance and User Experience Enhancements
class VetAIEnhancer {
    constructor() {
        this.init();
    }

    init() {
        this.setupPerformanceMonitoring();
        this.setupUserExperience();
        this.setupAnimations();
        this.setupOfflineSupport();
    }

    setupPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('🚀 VetAI Performance Metrics:', {
                'Page Load Time': `${Math.round(perfData.loadEventEnd - perfData.fetchStart)}ms`,
                'DOM Content Loaded': `${Math.round(perfData.domContentLoadedEventEnd - perfData.fetchStart)}ms`,
                'First Paint': this.getFirstPaint(),
                'Memory Usage': this.getMemoryInfo()
            });
        });
    }

    getFirstPaint() {
        try {
            const paintEntries = performance.getEntriesByType('paint');
            const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
            return firstPaint ? `${Math.round(firstPaint.startTime)}ms` : 'N/A';
        } catch (e) {
            return 'N/A';
        }
    }

    getMemoryInfo() {
        try {
            if (performance.memory) {
                return `${Math.round(performance.memory.usedJSHeapSize / 1048576)}MB`;
            }
            return 'N/A';
        } catch (e) {
            return 'N/A';
        }
    }

    setupUserExperience() {
        // Add loading states
        this.addLoadingStates();
        
        // Enhance form interactions
        this.enhanceFormInteractions();
        
        // Add keyboard shortcuts
        this.addKeyboardShortcuts();
        
        // Setup tooltips
        this.setupTooltips();
    }

    addLoadingStates() {
        // Add loading animation to predict button
        const predictForm = document.querySelector('#prediction-form');
        if (predictForm) {
            predictForm.addEventListener('submit', (e) => {
                const submitBtn = predictForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
                    submitBtn.disabled = true;
                    
                    // Reset after 3 seconds (fallback)
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }, 5000);
                }
            });
        }
    }

    enhanceFormInteractions() {
        // Add auto-save functionality
        const formInputs = document.querySelectorAll('select, input');
        formInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.saveFormData();
            });
        });

        // Load saved form data
        this.loadFormData();
    }

    saveFormData() {
        try {
            const formData = {};
            const form = document.querySelector('#prediction-form');
            if (form) {
                const formElements = form.querySelectorAll('select, input');
                formElements.forEach(element => {
                    if (element.name) {
                        formData[element.name] = element.value;
                    }
                });
                localStorage.setItem('vetai_form_data', JSON.stringify(formData));
            }
        } catch (e) {
            console.log('Auto-save not available');
        }
    }

    loadFormData() {
        try {
            const savedData = localStorage.getItem('vetai_form_data');
            if (savedData) {
                const formData = JSON.parse(savedData);
                Object.keys(formData).forEach(key => {
                    const element = document.querySelector(`[name="${key}"]`);
                    if (element && formData[key] && !formData[key].startsWith('Select')) {
                        element.value = formData[key];
                    }
                });
            }
        } catch (e) {
            console.log('Auto-load not available');
        }
    }

    addKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to submit form
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                const submitBtn = document.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
            
            // Escape to clear form
            if (e.key === 'Escape') {
                const form = document.querySelector('#prediction-form');
                if (form) {
                    form.reset();
                    localStorage.removeItem('vetai_form_data');
                }
            }
        });
    }

    setupTooltips() {
        // Add helpful tooltips
        const tooltips = [
            { selector: '[name="Animal"]', text: 'Select the type of livestock animal' },
            { selector: '[name="Age"]', text: 'Enter age in years (e.g., 2.5 for 2.5 years)' },
            { selector: '[name="Temperature"]', text: 'Body temperature in Fahrenheit (normal: 101-103°F)' },
            { selector: '[name="Symptom 1"]', text: 'Primary symptom observed' },
            { selector: '[name="Symptom 2"]', text: 'Secondary symptom observed' },
            { selector: '[name="Symptom 3"]', text: 'Additional symptom observed' }
        ];

        tooltips.forEach(({ selector, text }) => {
            const element = document.querySelector(selector);
            if (element) {
                element.setAttribute('title', text);
                element.setAttribute('data-bs-toggle', 'tooltip');
                element.setAttribute('data-bs-placement', 'top');
            }
        });

        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    setupAnimations() {
        // Intersection Observer for animations
        if ('IntersectionObserver' in window) {
            const animateElements = document.querySelectorAll('.card, .stat-card, .chart-container');
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            }, { threshold: 0.1 });

            animateElements.forEach(el => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(20px)';
                el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                observer.observe(el);
            });
        }
    }

    setupOfflineSupport() {
        // Basic offline detection
        window.addEventListener('online', () => {
            this.showNotification('🌐 Connection restored!', 'success');
        });

        window.addEventListener('offline', () => {
            this.showNotification('📡 You are offline. Some features may be limited.', 'warning');
        });
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    // Analytics tracking
    trackEvent(category, action, label = '') {
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                event_category: category,
                event_label: label
            });
        }
        console.log(`📊 Analytics: ${category} - ${action} - ${label}`);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const enhancer = new VetAIEnhancer();
    
    // Track page view
    enhancer.trackEvent('Navigation', 'Page View', window.location.pathname);
    
    console.log('🎉 VetAI Enhanced Experience Loaded!');
    console.log('⌨️  Keyboard Shortcuts:');
    console.log('   Ctrl+Enter: Submit prediction');
    console.log('   Escape: Clear form');
    console.log('💾 Auto-save: Form data automatically saved');
    console.log('🔄 Offline Support: Basic offline detection enabled');
});

// Export for global access
window.VetAIEnhancer = VetAIEnhancer;
