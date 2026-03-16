// ===== INLINE EDIT FUNCTIONALITY =====

class InlineEditor {
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
        console.log(`InlineEditor initialized for table: ${this.tableId}`);
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
        
        // Event delegation for Save buttons
        table.addEventListener('click', (e) => {
            const saveBtn = e.target.closest('.btn-inline-save');
            if (saveBtn) {
                e.preventDefault();
                const row = saveBtn.closest('tr');
                this.saveEdit(row);
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
                this.saveEdit(row);
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
        this.propertyType = row.dataset.propertyType || 'Villa';
        
        // Show loading state
        this.setLoadingState(row, true);
        
        // Fetch current data and options
        const listingId = row.dataset.listingId;
        fetch(`${this.apiUrl}${listingId}/inline-edit/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.renderEditForm(row, data.data, data.options);
                    this.setLoadingState(row, false);
                } else {
                    this.showError(data.error || 'Failed to load listing data');
                    this.setLoadingState(row, false);
                }
            })
            .catch(error => {
                console.error('Error fetching listing data:', error);
                this.showError('Failed to load listing data');
                this.setLoadingState(row, false);
            });
    }
    
    renderEditForm(row, data, options) {
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
            this.makeCellEditable(cells[cellIndex], 'assigned_salesman', data.assigned_salesman, 'select', {
                options: options.salesmen || []
            });
            cellIndex++;
        }
        
        // Skip Status column - make it read-only like ID and Type columns
        // Status will remain as display text and not be editable
        
        // Add property-specific fields
        this.addPropertyFields(row, data.property_details, options.property_type);
        
        // Update Actions column
        this.updateActionsColumn(row, 'editing');
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
                           step="${options.step || '1'}"
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
    
    addPropertyFields(row, propertyData, propertyType) {
        // For now, we'll keep the basic fields editable
        // Property-specific fields can be added here in the future
        // This would require more complex form rendering
    }
    
    getStatusOptions(statusOptions, data) {
        // Determine which status field to use based on current stage
        if (data.lead_status) return statusOptions.lead_status || [];
        if (data.opp_status) return statusOptions.opp_status || [];
        if (data.sale_status) return statusOptions.sale_status || [];
        return [];
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
        const formData = this.getFormData(row);
        const listingId = row.dataset.listingId;
        
        // Basic validation - only validate fields that are actually editable
        if (!formData.title) {
            this.showError('Please provide a title');
            return;
        }
        
        // Show saving state
        this.setSavingState(row, true);
        
        fetch(`${this.apiUrl}${listingId}/inline-edit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            this.setSavingState(row, false);
            
            if (data.success) {
                // Show success message
                this.showSuccess(data.message || 'Listing updated successfully');
                
                // Close the edit mode
                this.cancelEdit(row);
                
                // Force page reload to ensure changes reflect immediately
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            } else {
                this.showErrors(data.errors || {}, row);
            }
        })
        .catch(error => {
            console.error('Error saving listing:', error);
            this.setSavingState(row, false);
            this.showError('Failed to save changes');
        });
    }
    
    applyUpdatedData(row, data) {
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
            const statusText = data.lead_status_display || data.opp_status_display || data.sale_status_display || '';
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
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
        toast.style.cssText = `
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            width: auto;
            min-width: 120px;
            max-width: 150px;
            text-align: center;
        `;
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    }
    
    getCSRFToken() {
        // Try multiple methods to get CSRF token
        let token = null;
        
        // Method 1: Look for csrfmiddlewaretoken in forms
        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenInput) {
            token = tokenInput.value;
        }
        
        // Method 2: Look for CSRF token in meta tags
        if (!token) {
            const metaTag = document.querySelector('meta[name=csrf-token]');
            if (metaTag) {
                token = metaTag.getAttribute('content');
            }
        }
        
        // Method 3: Look for CSRF token in cookies
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
        
        return token;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize inline editors for all dashboard tables
document.addEventListener('DOMContentLoaded', function() {
    // Initialize for Salesman Dashboard
    if (document.getElementById('salesman-leads-table')) {
        new InlineEditor('salesman-leads-table', '/inventory/api/listing/');
    }
    
    if (document.getElementById('salesman-opps-table')) {
        new InlineEditor('salesman-opps-table', '/inventory/api/listing/');
    }
    
    if (document.getElementById('salesman-sales-table')) {
        new InlineEditor('salesman-sales-table', '/inventory/api/listing/');
    }
    
    // Initialize for Manager Dashboard
    if (document.getElementById('manager-leads-table')) {
        new InlineEditor('manager-leads-table', '/inventory/api/listing/');
    }
    
    if (document.getElementById('manager-opps-table')) {
        new InlineEditor('manager-opps-table', '/inventory/api/listing/');
    }
    
    if (document.getElementById('manager-sales-table')) {
        new InlineEditor('manager-sales-table', '/inventory/api/listing/');
    }
});