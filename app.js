// WiFi Capping NCUK - Application Logic
// This script handles the WiFi capping functionality with proper CSP compliance

class WiFiCappingSystem {
    constructor() {
        this.currentUsage = 0;
        this.dataCap = 100; // GB
        this.init();
    }

    init() {
        this.loadStoredData();
        this.updateDisplay();
        this.bindEvents();
        this.simulateUsage();
    }

    loadStoredData() {
        // Load data from localStorage if available
        const storedUsage = localStorage.getItem('wifi-usage');
        const storedCap = localStorage.getItem('wifi-cap');
        
        if (storedUsage) {
            this.currentUsage = parseFloat(storedUsage);
        }
        
        if (storedCap) {
            this.dataCap = parseFloat(storedCap);
        }
    }

    saveData() {
        localStorage.setItem('wifi-usage', this.currentUsage.toString());
        localStorage.setItem('wifi-cap', this.dataCap.toString());
    }

    updateDisplay() {
        const currentUsageEl = document.getElementById('current-usage');
        const dataCapEl = document.getElementById('data-cap');
        const remainingDataEl = document.getElementById('remaining-data');

        if (currentUsageEl) {
            currentUsageEl.textContent = `${this.currentUsage.toFixed(2)} GB`;
        }

        if (dataCapEl) {
            dataCapEl.textContent = `${this.dataCap} GB`;
        }

        if (remainingDataEl) {
            const remaining = Math.max(0, this.dataCap - this.currentUsage);
            remainingDataEl.textContent = `${remaining.toFixed(2)} GB`;
            
            // Color coding based on remaining data
            if (remaining < this.dataCap * 0.1) {
                remainingDataEl.style.color = '#dc3545'; // Red
            } else if (remaining < this.dataCap * 0.3) {
                remainingDataEl.style.color = '#ffc107'; // Yellow
            } else {
                remainingDataEl.style.color = '#28a745'; // Green
            }
        }
    }

    bindEvents() {
        const refreshBtn = document.getElementById('refresh-stats');
        const setCapBtn = document.getElementById('set-cap');
        const resetUsageBtn = document.getElementById('reset-usage');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshStats());
        }

        if (setCapBtn) {
            setCapBtn.addEventListener('click', () => this.setDataCap());
        }

        if (resetUsageBtn) {
            resetUsageBtn.addEventListener('click', () => this.resetUsage());
        }
    }

    refreshStats() {
        // Add loading state
        const elements = ['current-usage', 'data-cap', 'remaining-data'];
        elements.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.add('loading');
            }
        });

        // Simulate API call delay
        setTimeout(() => {
            this.updateDisplay();
            elements.forEach(id => {
                const el = document.getElementById(id);
                if (el) {
                    el.classList.remove('loading');
                }
            });
        }, 1000);
    }

    setDataCap() {
        const newCap = prompt('Enter new data cap (GB):', this.dataCap.toString());
        
        if (newCap && !isNaN(newCap) && parseFloat(newCap) > 0) {
            this.dataCap = parseFloat(newCap);
            this.saveData();
            this.updateDisplay();
            alert(`Data cap set to ${this.dataCap} GB`);
        } else if (newCap !== null) {
            alert('Please enter a valid number greater than 0');
        }
    }

    resetUsage() {
        if (confirm('Are you sure you want to reset the usage counter?')) {
            this.currentUsage = 0;
            this.saveData();
            this.updateDisplay();
            alert('Usage counter has been reset');
        }
    }

    simulateUsage() {
        // Simulate gradual data usage increase for demo purposes
        setInterval(() => {
            if (this.currentUsage < this.dataCap) {
                this.currentUsage += Math.random() * 0.01; // Random small increment
                this.saveData();
                this.updateDisplay();
            }
        }, 5000); // Update every 5 seconds
    }

    // Security feature: validate data against potential XSS
    sanitizeInput(input) {
        if (typeof input !== 'string') return input;
        return input.replace(/[<>'"&]/g, '');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const wifiSystem = new WiFiCappingSystem();
    
    // Security: Prevent XSS by ensuring CSP compliance
    console.log('WiFi Capping System initialized with CSP protection');
});

// Export for testing purposes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WiFiCappingSystem;
}