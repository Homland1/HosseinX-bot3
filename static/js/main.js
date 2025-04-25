/**
 * Main JavaScript file for HosseinX-bot3 Admin Panel
 */

// Make sure DOM is loaded before executing scripts
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(message);
            bsAlert.close();
        }, 5000);
    });
    
    // Add current year to footer
    const footerYear = document.querySelector('.footer .text-muted');
    if (footerYear) {
        const year = new Date().getFullYear();
        footerYear.innerHTML = footerYear.innerHTML.replace('{{ now.year }}', year);
    }
    
    // Add confirm dialog to dangerous actions
    const dangerousActions = document.querySelectorAll('.btn-danger[data-confirm]');
    dangerousActions.forEach(function(btn) {
        btn.addEventListener('click', function(event) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                event.preventDefault();
            }
        });
    });
});

/**
 * Function to fetch bot status
 * This would be used if you had a /bot/status endpoint
 */
function fetchBotStatus() {
    fetch('/bot/status')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const statusBadge = document.getElementById('bot-status-badge');
            if (statusBadge) {
                if (data.is_running) {
                    statusBadge.className = 'badge bg-success';
                    statusBadge.textContent = 'Running';
                } else {
                    statusBadge.className = 'badge bg-danger';
                    statusBadge.textContent = 'Stopped';
                }
            }
        })
        .catch(error => {
            console.error('Error fetching bot status:', error);
        });
}
