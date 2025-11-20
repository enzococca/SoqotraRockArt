/**
 * JavaScript for Rock Art Database Web Application
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    autoHideAlerts();

    // Initialize tooltips
    initTooltips();

    // Initialize image upload preview
    initImageUpload();

    // Initialize table row click handling
    initTableRowClick();
});

/**
 * Auto-hide alert messages after 5 seconds
 */
function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize image upload preview
 */
function initImageUpload() {
    const imageInput = document.getElementById('imageFile');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                // Show file info
                const fileInfo = document.createElement('div');
                fileInfo.className = 'alert alert-info mt-2';
                fileInfo.innerHTML = `
                    <i class="bi bi-info-circle"></i>
                    Selected: ${file.name} (${formatFileSize(file.size)})
                `;

                // Remove previous info if exists
                const existingInfo = imageInput.parentElement.querySelector('.alert-info');
                if (existingInfo) {
                    existingInfo.remove();
                }

                imageInput.parentElement.appendChild(fileInfo);
            }
        });
    }
}

/**
 * Format file size to human-readable format
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Initialize table row click to view details
 */
function initTableRowClick() {
    const tableRows = document.querySelectorAll('.table-hover tbody tr');
    tableRows.forEach(row => {
        // Skip rows without data-record-id attribute
        const recordId = row.dataset.recordId;
        if (!recordId) return;

        row.style.cursor = 'pointer';
        row.addEventListener('click', function(e) {
            // Don't navigate if clicking on buttons/links
            if (e.target.closest('a, button')) return;

            window.location.href = `/record/${recordId}`;
        });
    });
}

/**
 * Confirm deletion with custom message
 */
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item? This action cannot be undone.');
}

/**
 * Show loading spinner
 */
function showLoading(element) {
    const spinner = document.createElement('span');
    spinner.className = 'spinner-border spinner-border-sm me-2';
    spinner.setAttribute('role', 'status');
    element.prepend(spinner);
    element.disabled = true;
}

/**
 * Hide loading spinner
 */
function hideLoading(element) {
    const spinner = element.querySelector('.spinner-border');
    if (spinner) {
        spinner.remove();
    }
    element.disabled = false;
}

/**
 * Search highlighting
 */
function highlightSearchTerm(text, searchTerm) {
    if (!searchTerm) return text;
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    return text.replace(regex, '<span class="search-highlight">$1</span>');
}

/**
 * Debounce function for search
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format date to locale string
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showToast('Failed to copy to clipboard', 'danger');
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

/**
 * Validate coordinates
 */
function validateCoordinates(lat, lon) {
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lon);

    if (isNaN(latitude) || isNaN(longitude)) {
        return { valid: false, message: 'Coordinates must be numbers' };
    }

    if (latitude < -90 || latitude > 90) {
        return { valid: false, message: 'Latitude must be between -90 and 90' };
    }

    if (longitude < -180 || longitude > 180) {
        return { valid: false, message: 'Longitude must be between -180 and 180' };
    }

    return { valid: true };
}

/**
 * Confirm before leaving page with unsaved changes
 */
function setupFormChangeDetection() {
    const forms = document.querySelectorAll('form[data-confirm-leave]');
    let formChanged = false;

    forms.forEach(form => {
        form.addEventListener('change', () => {
            formChanged = true;
        });

        form.addEventListener('submit', () => {
            formChanged = false;
        });
    });

    window.addEventListener('beforeunload', (e) => {
        if (formChanged) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
}

// Export functions for use in templates
window.RockArtApp = {
    confirmDelete,
    showLoading,
    hideLoading,
    highlightSearchTerm,
    debounce,
    formatDate,
    copyToClipboard,
    showToast,
    validateCoordinates
};
