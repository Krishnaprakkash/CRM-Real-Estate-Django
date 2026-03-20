// ===== NEW ROBUST INLINE EDIT FUNCTIONALITY =====
// Completely rewritten to eliminate AJAX GET requests and use table cell data

class RobustInlineEditor {
    constructor(tableId, apiUrl) {
        this.tableId = tableId;
        this.apiUrl = apiUrl;
        this.editingRow = null;
        this.originalData = null;
        this.propertyType = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
    }
    
    bindEvents() {
        const table = document.getElementById(this.tableId);
        if (!table) return;
        
        // Event delegation for Edit buttons
        table.addEventListener('click', (e) => {
            const editBtn = e.target.closest('.btn-inline-edit');
            if (editBtn) {
                e.preventDefault();
                const row = editBtn.closest('tr');
                this.startEdit(row);
            }
        });
        
        // Event delegation for Save buttons with improved timing
        table.addEventListener('click', (e) => {
            const saveBtn = e.target.closest('.btn-inline-save');
            if (saveBtn) {
                e.preventDefault();
                const row = saveBtn.closest('tr');
                // Add a small delay to ensure form is fully rendered
                setTimeout(() => {
                    this.saveEdit(row);
                }, 50);
            }
        });
        
        // Event delegation for Cancel buttons
        table.addEventListener('click', (e) => {
            const cancelBtn = e.target.closest('.btn-inline-cancel');
            if (cancelBtn) {
                e.preventDefault();
                const row = cancelBtn.closest('tr');
                this.cancelEdit(row);
            }
        });
        
        // Handle Enter key in input fields
        table.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.classList.contains('inline-edit-input')) {
                e.preventDefault();
                const row = e.target.closest('tr');
                // Add a small delay to ensure form is fully rendered
                setTimeout(() => {
                    this.saveEdit(row);
                }, 50);
            } else if (e.key === 'Escape' && e.target.classList.contains('inline-edit-input')) {
                e.preventDefault();
                const row = e.target.closest('tr');
                this.cancelEdit(row);
            }
        });
    }
    
    startEdit(row) {
        // Prevent editing multiple rows simultaneously
        if (this.editingRow && this.editingRow !== row) {
            this.cancelEdit(this.editingRow);
        }
        
        this.editingRow = row;
        this.originalData = this.getOriginalData(row);
        
        // Extract data attributes with better error handling
        const listingId = row.dataset.listingId;
        const propertyType = row.dataset.propertyType;
        const salesmanId = row.dataset.salesmanId;
        
        
        if (!listingId) {
            this.showError('Listing ID not found. Cannot edit this row.');
            return;
        }
        
        this.propertyType = propertyType || 'Villa';
        
        // Show loading state
        this.setLoadingState(row, true);
        
        // Use data from table cells directly - NO AJAX REQUEST
        
        // Get CSRF token
        const csrfToken = this.getCSRFToken();
        
        // Render the edit form using data from table cells
        try {
            this.renderEditForm(row, this.originalData);
            this.setLoadingState(row, false);
        } catch (error) {
            this.setLoadingState(row, false);
            this.showError('Failed to render edit form. Please refresh the page.');
        }
    }
    
    renderEditForm(row, data) {
        const cells = row.querySelectorAll('td');
        const tableId = row.closest('table').id;
        
        // Determine if this is a manager dashboard (has Salesman column)
        const isManagerDashboard = tableId.includes('manager');
        
        let cellIndex = 1; // Start after checkbox column (cell 0)
        
        // Skip ID column (cell 1) - not editable
        cellIndex++;
        
        // Edit Title (cell 2)
        this.makeCellEditable(cells[cellIndex], 'title', data.title, 'text');
        cellIndex++;
        
        // Skip Type column (cell 3) - not editable
        cellIndex++;
        
        // Edit Price (cell 4)
        this.makeCellEditable(cells[cellIndex], 'proposed_price', data.proposed_price, 'number', {
            step: '0.01',
            min: '0'
        });
        cellIndex++;
        
        // Edit Salesman (Manager only, cell 5)
        if (isManagerDashboard) {
            // For manager dashboard, we need to fetch salesman options
            this.makeCellEditable(cells[cellIndex], 'assigned_salesman', data.assigned_salesman, 'select', {
                options: this.getSalesmanOptions(row)
            });
            cellIndex++;
        }
        
        // Skip Status column - make it read-only like ID and Type columns
        // Status will remain as display text and not be editable
        
        // Update Actions column
        this.updateActionsColumn(row, 'editing');
    }
    
    getSalesmanOptions(row) {
        // Try to get salesman options from the page filters
        const salesmanFilter = document.getElementById('salesman-filter') || 
                              document.getElementById('salesman-filter-leads') ||
                              document.getElementById('salesman-filter-opps') ||
                              document.getElementById('salesman-filter-sale');
        
        if (salesmanFilter) {
            const options = [];
            // Add default option
            options.push({ value: '', label: '— Select Salesman —' });
            
            // Get all options from the filter dropdown
            const filterOptions = salesmanFilter.querySelectorAll('option');
            filterOptions.forEach(option => {
                if (option.value !== 'all' && option.value !== '') {
                    options.push({
                        value: option.value,
                        label: option.textContent.trim()
                    });
                }
            });
            
            return options;
        }
        
        // Fallback: try to get from row data attributes
        const salesmanId = row.dataset.salesmanId;
        const currentSalesman = row.querySelector('td:nth-child(6)')?.textContent.trim();
        
        if (currentSalesman) {
            return [
                { value: '', label: '— Select Salesman —' },
                { value: salesmanId || 'current', label: currentSalesman }
            ];
        }
        
        return [];
    }
    
    makeCellEditable(cell, fieldName, currentValue, inputType, options = {}) {
        const originalContent = cell.innerHTML;
        cell.dataset.originalContent = originalContent;
        
        let inputHtml = '';
        
        switch (inputType) {
            case 'text':
                inputHtml = `
                    <input type="text" 
                           name="${fieldName}" 
                           value="${this.escapeHtml(currentValue || '')}" 
                           class="form-control form-control-sm inline-edit-input"
                           style="min-width: 120px;">
                `;
                break;
                
            case 'number':
                inputHtml = `
                    <input type="number" 
                           name="${fieldName}" 
                           value="${currentValue || ''}" 
                           class="form-control form-control-sm inline-edit-input"
                           step="${options.step || '0.01'}"
                           min="${options.min || '0'}"
                           style="min-width: 120px;">
                `;
                break;
                
            case 'select':
                const optionsHtml = options.options.map(opt => 
                    `<option value="${opt.value}" ${opt.value === currentValue ? 'selected' : ''}>${opt.label}</option>`
                ).join('');
                inputHtml = `
                    <select name="${fieldName}" class="form-select form-select-sm inline-edit-input" style="min-width: 150px;">
                        ${optionsHtml}
                    </select>
                `;
                break;
        }
        
        cell.innerHTML = inputHtml;
        cell.classList.add('editing');
    }
    
    updateActionsColumn(row, state) {
        const actionsCell = row.querySelector('td:last-child');
        if (!actionsCell) return;
        
        if (state === 'editing') {
            actionsCell.innerHTML = `
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-sm btn-success btn-inline-save" title="Save Changes">
                        <i class="bi bi-check-circle"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-secondary btn-inline-cancel" title="Cancel">
                        <i class="bi bi-x-circle"></i>
                    </button>
                </div>
            `;
        } else {
            actionsCell.innerHTML = `
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-sm btn-primary btn-inline-edit" title="Edit">
                        <i class="bi bi-pencil"></i>
                    </button>
                </div>
            `;
        }
    }
    
    getFormData(row) {
        const formData = {};
        const inputs = row.querySelectorAll('.inline-edit-input');
        
        inputs.forEach(input => {
            const name = input.name;
            let value = input.value;
            
            // Handle number fields
            if (input.type === 'number' && value) {
                value = parseFloat(value);
            }
            
            // Handle empty values
            if (value === '') {
                value = null;
            }
            
            formData[name] = value;
        });
        
        return formData;
    }
    
    getOriginalData(row) {
        const data = {};
        const cells = row.querySelectorAll('td');
        const tableId = row.closest('table').id;
        
        // Determine if this is a manager dashboard (has Salesman column)
        const isManagerDashboard = tableId.includes('manager');
        
        let cellIndex = 1; // Start after checkbox column (cell 0)
        
        // Skip ID column (cell 1) - not editable
        cellIndex++;
        
        // Extract Title (cell 2)
        data.title = cells[cellIndex].textContent.trim();
        cellIndex++;
        
        // Skip Type column (cell 3) - not editable
        cellIndex++;
        
        // Extract Price (cell 4)
        const priceText = cells[cellIndex].textContent.trim().replace(/[₹,]/g, '');
        data.proposed_price = priceText ? parseFloat(priceText) : null;
        cellIndex++;
        
        // Extract Salesman (Manager only, cell 5)
        if (isManagerDashboard) {
            data.assigned_salesman = cells[cellIndex].textContent.trim();
            cellIndex++;
        }
        
        // Extract Status (cell 5 for salesman, cell 6 for manager)
        data.status = cells[cellIndex].textContent.trim();
        
        return data;
    }
    
    saveEdit(row) {
        // Validate that we're actually in edit mode and form is ready
        const inputs = row.querySelectorAll('.inline-edit-input');
        if (inputs.length === 0) {
            this.showError('Please wait for the form to load completely');
            return;
        }
        
        const formData = this.getFormData(row);
        const listingId = row.dataset.listingId;
        
        // Basic validation - only validate fields that are actually editable
        if (!formData.title) {
            this.showError('Please provide a title');
            return;
        }
        
        // Clear any existing error states before saving
        this.clearErrorStates(row);
        
        // Show saving state
        this.setSavingState(row, true);
        
        // Make AJAX POST request to save changes
        fetch(`${this.apiUrl}${listingId}/inline-save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            this.setSavingState(row, false);
            
            if (data.success) {
                // Clear any existing messages before showing success
                this.clearToastsByType('danger');
                
                // Show success message
                this.showSuccess(data.message || 'Listing updated successfully');
                
                // Update the table with new data - ensure immediate update
                setTimeout(() => {
                    this.updateTableRow(row, data.data || formData);
                }, 100);
                
                // Close the edit mode after a small delay to ensure update completes
                setTimeout(() => {
                    this.cancelEdit(row);
                    // Reload page after successful save to ensure all data is updated
                    window.location.reload();
                }, 200);
            } else {
                // Only show errors if there are actual errors
                if (data.errors && Object.keys(data.errors).length > 0) {
                    this.showErrors(data.errors, row);
                } else {
                    // If no specific errors, show a generic error message
                    this.showError(data.error || 'Failed to update listing. Please try again.');
                }
            }
        })
        .catch(error => {
            this.setSavingState(row, false);
            this.clearToastsByType('success');
            this.showError('Failed to save changes. Please try again.');
        });
    }
    
    updateTableRow(row, data) {
        const cells = row.querySelectorAll('td');
        const tableId = row.closest('table').id;
        
        // Determine if this is a manager dashboard (has Salesman column)
        const isManagerDashboard = tableId.includes('manager');
        
        let cellIndex = 1; // Start after checkbox column (cell 0)
        
        // Skip ID column (cell 1) - not editable
        cellIndex++;
        
        // Update Title (cell 2)
        if (cells[cellIndex]) {
            cells[cellIndex].textContent = data.title || '';
        }
        cellIndex++;
        
        // Skip Type column (cell 3) - not editable
        cellIndex++;
        
        // Update Price (cell 4)
        if (cells[cellIndex]) {
            const priceDisplay = data.price_display || (data.proposed_price ? `₹${parseFloat(data.proposed_price).toLocaleString()}` : '—');
            cells[cellIndex].innerHTML = `<span class="price-cell">${priceDisplay}</span>`;
        }
        cellIndex++;
        
        // Update Salesman (Manager only, cell 5)
        if (isManagerDashboard && cells[cellIndex]) {
            cells[cellIndex].textContent = data.assigned_salesman || '—';
            cellIndex++;
        }
        
        // Update Status (cell 5 for salesman, cell 6 for manager)
        if (cells[cellIndex]) {
            const statusText = data.status || cells[cellIndex].textContent.trim();
            const statusBadge = this.getStatusBadge(statusText);
            cells[cellIndex].innerHTML = statusBadge;
        }
    }
    
    getStatusBadge(statusText) {
        // Determine badge class based on status
        let badgeClass = 'status-badge';
        
        if (statusText.includes('Pending') || statusText.includes('Prospecting')) {
            badgeClass += ' pending';
        } else if (statusText.includes('Approved') || statusText.includes('Won')) {
            badgeClass += ' approved';
        } else if (statusText.includes('Rejected') || statusText.includes('Lost')) {
            badgeClass += ' rejected';
        } else if (statusText.includes('Negotiating')) {
            badgeClass += ' negotiating';
        } else if (statusText.includes('Processing')) {
            badgeClass += ' processing';
        }
        
        return `<span class="${badgeClass}">${statusText}</span>`;
    }
    
    cancelEdit(row) {
        // Restore original content
        const cells = row.querySelectorAll('td.editing');
        cells.forEach(cell => {
            cell.innerHTML = cell.dataset.originalContent;
            cell.classList.remove('editing');
        });
        
        // Restore Actions column
        this.updateActionsColumn(row, 'viewing');
        
        this.editingRow = null;
        this.originalData = null;
    }
    
    showErrors(errors, row) {
        // Clear any existing error states first
        this.clearErrorStates(row);
        
        // Highlight error fields
        Object.keys(errors).forEach(fieldName => {
            const input = row.querySelector(`input[name="${fieldName}"], select[name="${fieldName}"]`);
            if (input) {
                input.classList.add('is-invalid');
                const errorHtml = `<div class="invalid-feedback">${errors[fieldName][0]}</div>`;
                input.parentNode.insertAdjacentHTML('beforeend', errorHtml);
            }
        });
    }
    
    clearErrorStates(row) {
        // Remove all invalid classes and error messages
        const inputs = row.querySelectorAll('.inline-edit-input');
        inputs.forEach(input => {
            input.classList.remove('is-invalid');
        });
        
        // Remove all error message elements
        const errorMessages = row.querySelectorAll('.invalid-feedback');
        errorMessages.forEach(error => {
            error.remove();
        });
    }
    
    setLoadingState(row, isLoading) {
        const cells = row.querySelectorAll('td');
        cells.forEach(cell => {
            if (isLoading) {
                cell.style.opacity = '0.5';
            } else {
                cell.style.opacity = '1';
            }
        });
    }
    
    setSavingState(row, isSaving) {
        const saveBtn = row.querySelector('.btn-inline-save i');
        if (saveBtn) {
            if (isSaving) {
                saveBtn.className = 'bi bi-hourglass-split';
            } else {
                saveBtn.className = 'bi bi-check-circle';
            }
        }
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'error');
    }
    
    showToast(message, type) {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('inline-edit-toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'inline-edit-toast-container';
            toastContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 300px;
                width: 100%;
                pointer-events: none;
            `;
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        const alertType = type === 'success' ? 'success' : 'danger';
        toast.className = `alert alert-${alertType} alert-dismissible fade show mb-2`;
        toast.style.cssText = `
            pointer-events: auto;
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-${type === 'success' ? 'check-circle-fill' : 'exclamation-triangle-fill'} me-2"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add CSS animation if not already added
        this.addToastAnimation();
        
        // Clear existing toasts of the same type to prevent stacking
        this.clearToastsByType(alertType);
        
        // Add the new toast
        toastContainer.appendChild(toast);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOutRight 0.3s ease-out';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 300);
            }
        }, 3000);
    }
    
    addToastAnimation() {
        // Add CSS animations if not already present
        if (!document.getElementById('inline-edit-toast-styles')) {
            const style = document.createElement('style');
            style.id = 'inline-edit-toast-styles';
            style.textContent = `
                @keyframes slideInRight {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
                #inline-edit-toast-container .alert {
                    margin-bottom: 10px !important;
                    border-radius: 8px;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    clearToastsByType(type) {
        const toastContainer = document.getElementById('inline-edit-toast-container');
        if (toastContainer) {
            const toasts = toastContainer.querySelectorAll(`.alert-${type}`);
            toasts.forEach(toast => {
                toast.style.animation = 'slideOutRight 0.3s ease-out';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 300);
            });
        }
    }
    
    getCSRFToken() {
        // Try multiple methods to get CSRF token - improved order and reliability
        let token = null;
        
        // Method 1: Check window object first (set by base template)
        if (window.csrfToken) {
            token = window.csrfToken;
            return token;
        }
        
        // Method 2: Look for CSRF token in meta tags
        if (!token) {
            const metaTag = document.querySelector('meta[name=csrf-token]');
            if (metaTag) {
                token = metaTag.getAttribute('content');
                return token;
            }
        }
        
        // Method 3: Look for csrfmiddlewaretoken in forms
        if (!token) {
            const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
            if (tokenInput) {
                token = tokenInput.value;
                return token;
            }
        }
        
        // Method 4: Look for CSRF token in cookies (Django default)
        if (!token) {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {
                    token = value;
                    break;
                }
            }
        }
        
        // Method 5: Try to find any form on the page and extract token
        if (!token) {
            const forms = document.querySelectorAll('form');
            for (let form of forms) {
                const csrfInput = form.querySelector('[name=csrfmiddlewaretoken]');
                if (csrfInput) {
                    token = csrfInput.value;
                    break;
                }
            }
        }
        
        if (!token) {
            this.showError('Security token missing. Please refresh the page and try again.');
        }
        
        return token;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize robust inline editors for all dashboard tables
document.addEventListener('DOMContentLoaded', function() {
    // Initialize for Salesman Dashboard
    if (document.getElementById('salesman-leads-table')) {
        new RobustInlineEditor('salesman-leads-table', '/inventory/api/listing/');
    }
    
    if (document.getElementById('salesman-opps-table')) {
        new RobustInlineEditor('salesman-opps-table', '/inventory/api/listing/');
    }
    
    if (document.getElementById('salesman-sales-table')) {
        new RobustInlineEditor('salesman-sales-table', '/inventory/api/listing/');
    }
    
    // Initialize for Manager Dashboard
    if (document.getElementById('manager-leads-table')) {
        new RobustInlineEditor('manager-leads-table', '/inventory/api/listing/');
    }
    
    if (document.getElementById('manager-opps-table')) {
        new RobustInlineEditor('manager-opps-table', '/inventory/api/listing/');
    }
    
    if (document.getElementById('manager-sales-table')) {
        new RobustInlineEditor('manager-sales-table', '/inventory/api/listing/');
    }
});
