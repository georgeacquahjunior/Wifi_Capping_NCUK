// DOM Elements
const menuToggle = document.getElementById('menuToggle');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const menuItems = document.querySelectorAll('.menu-item');
const contentSections = document.querySelectorAll('.content-section');

// Create overlay for mobile menu
const overlay = document.createElement('div');
overlay.className = 'overlay';
document.body.appendChild(overlay);

// Mobile menu toggle
menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
});

// Close mobile menu when clicking overlay
overlay.addEventListener('click', () => {
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
});

// Navigation handling
menuItems.forEach((item, index) => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active class from all menu items
        menuItems.forEach(menuItem => menuItem.classList.remove('active'));
        
        // Add active class to clicked item
        item.classList.add('active');
        
        // Hide all content sections
        contentSections.forEach(section => section.classList.remove('active'));
        
        // Show corresponding content section
        const targetId = item.querySelector('a').getAttribute('href').substring(1);
        const targetSection = document.getElementById(targetId);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        // Close mobile menu after navigation
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    });
});

// Handle window resize
window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    }
});

// Form submissions
document.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    // Show success message (in a real app, this would send data to server)
    showNotification('Settings saved successfully!', 'success');
});

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 1001;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Simulate real-time data updates
function updateDashboardData() {
    // Update active connections with random variation
    const activeConnectionsElement = document.querySelector('.stat-card:nth-child(3) .stat-number');
    if (activeConnectionsElement) {
        const baseValue = 892;
        const variation = Math.floor(Math.random() * 40) - 20; // ±20
        activeConnectionsElement.textContent = (baseValue + variation).toString();
    }
    
    // Update bandwidth usage
    const bandwidthFill = document.querySelector('.bandwidth-fill');
    if (bandwidthFill) {
        const currentWidth = parseInt(bandwidthFill.style.width) || 65;
        const newWidth = Math.max(30, Math.min(95, currentWidth + (Math.random() * 10 - 5)));
        bandwidthFill.style.width = `${newWidth}%`;
        
        const bandwidthText = bandwidthFill.parentElement.nextElementSibling;
        if (bandwidthText) {
            const mbps = Math.floor(newWidth * 10);
            bandwidthText.textContent = `${mbps} Mbps / 1 Gbps`;
        }
    }
    
    // Update data usage
    const dataUsageElement = document.querySelector('.stat-card:nth-child(2) .stat-number');
    if (dataUsageElement) {
        const currentValue = parseFloat(dataUsageElement.textContent);
        const increment = Math.random() * 0.01;
        const newValue = (currentValue + increment).toFixed(1);
        dataUsageElement.textContent = `${newValue} TB`;
    }
}

// Update dashboard data every 5 seconds
setInterval(updateDashboardData, 5000);

// Handle table actions
document.addEventListener('click', (e) => {
    if (e.target.closest('.btn-icon')) {
        const action = e.target.classList.contains('fa-edit') ? 'edit' : 'delete';
        const row = e.target.closest('tr');
        const userName = row.querySelector('.user-info span').textContent;
        
        if (action === 'edit') {
            showNotification(`Edit user: ${userName}`, 'info');
        } else if (action === 'delete') {
            if (confirm(`Are you sure you want to delete user: ${userName}?`)) {
                row.remove();
                showNotification(`User ${userName} deleted successfully`, 'success');
            }
        }
    }
});

// Search functionality
const searchInput = document.querySelector('.search-box input');
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const tableRows = document.querySelectorAll('.data-table tbody tr');
        
        tableRows.forEach(row => {
            const userName = row.querySelector('.user-info span').textContent.toLowerCase();
            const userEmail = row.cells[1].textContent.toLowerCase();
            
            if (userName.includes(searchTerm) || userEmail.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

// Add new user button functionality
const addUserBtn = document.querySelector('.btn-primary');
if (addUserBtn && addUserBtn.textContent.includes('Add User')) {
    addUserBtn.addEventListener('click', () => {
        showNotification('Add User form would open here', 'info');
    });
}

// Export report functionality
const exportBtn = document.querySelector('.btn-secondary');
if (exportBtn && exportBtn.textContent.includes('Export Report')) {
    exportBtn.addEventListener('click', () => {
        // Simulate report generation
        showNotification('Generating report...', 'info');
        
        setTimeout(() => {
            showNotification('Report exported successfully!', 'success');
        }, 2000);
    });
}

// Simulate activity feed updates
function addNewActivity() {
    const activities = [
        {
            icon: 'fas fa-user-plus',
            text: 'New user registered: student@ncuk.ac.uk',
            time: 'Just now'
        },
        {
            icon: 'fas fa-exclamation-circle',
            text: 'Bandwidth threshold reached in Building B',
            time: '2 minutes ago'
        },
        {
            icon: 'fas fa-cog',
            text: 'System maintenance completed',
            time: '5 minutes ago'
        }
    ];
    
    const activityList = document.querySelector('.activity-list');
    if (activityList && Math.random() > 0.7) { // 30% chance every update
        const randomActivity = activities[Math.floor(Math.random() * activities.length)];
        
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <i class="${randomActivity.icon}"></i>
            <div class="activity-details">
                <p>${randomActivity.text}</p>
                <span class="activity-time">${randomActivity.time}</span>
            </div>
        `;
        
        // Add to top of list
        activityList.insertBefore(activityItem, activityList.firstChild);
        
        // Remove oldest item if more than 5 items
        if (activityList.children.length > 5) {
            activityList.removeChild(activityList.lastChild);
        }
    }
}

// Add new activity every 30 seconds
setInterval(addNewActivity, 30000);

// Progressive enhancement for forms
document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        const min = parseInt(e.target.min) || 0;
        const max = parseInt(e.target.max) || 1000;
        
        if (value < min) {
            e.target.value = min;
        } else if (value > max) {
            e.target.value = max;
        }
    });
});

// Handle logout
const logoutBtn = document.querySelector('.logout-btn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to logout?')) {
            showNotification('Logging out...', 'info');
            // In a real app, this would redirect to login page
        }
    });
}

// Keyboard navigation support
document.addEventListener('keydown', (e) => {
    // Escape key closes mobile menu
    if (e.key === 'Escape') {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    }
    
    // Alt + 1-5 for quick navigation
    if (e.altKey && e.key >= '1' && e.key <= '5') {
        e.preventDefault();
        const index = parseInt(e.key) - 1;
        if (menuItems[index]) {
            menuItems[index].click();
        }
    }
});

// Initialize tooltips for better UX
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[title]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = element.title;
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 0.5rem;
                border-radius: 4px;
                font-size: 0.875rem;
                white-space: nowrap;
                z-index: 1002;
                pointer-events: none;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = element.getBoundingClientRect();
            tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
            
            element.setAttribute('data-tooltip', 'true');
        });
        
        element.addEventListener('mouseleave', (e) => {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                document.body.removeChild(tooltip);
            }
            element.removeAttribute('data-tooltip');
        });
        
        // Remove title to prevent default browser tooltip
        element.setAttribute('data-title', element.title);
        element.removeAttribute('title');
    });
}

// Initialize tooltips when DOM is ready
document.addEventListener('DOMContentLoaded', initializeTooltips);

// Performance optimization: Throttle resize events
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        // Recalculate layout if needed
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    }, 100);
});

console.log('WiFi Capping Admin Dashboard initialized successfully!');