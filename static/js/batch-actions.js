// ===== FIXED BATCH ACTIONS - SIMPLE AND RELIABLE =====

// Toggle select all checkboxes
function toggleSelectAll(source) {
    const table = source.closest('table');
    if (!table) return;
    const checkboxes = table.querySelectorAll('input[name="listing_ids"]');
    checkboxes.forEach(cb => cb.checked = source.checked);
}

// Get selected listing IDs - FIXED VERSION
function getSelectedListings(button) {
    // Find the form that contains this button
    const form = button.closest('form');
    if (!form) {
        console.error('No form found for batch action button');
        return [];
    }
    
    // Get all checked checkboxes in this form
    const checkboxes = form.querySelectorAll('input[name="listing_ids"]:checked');
    const selected = [];
    
    checkboxes.forEach(checkbox => {
        selected.push(checkbox.value);
    });
    
    return selected;
}

// Show rejection modal
function showRejectionModal(button) {
    const modal = document.getElementById('rejection-modal');
    if (!modal) return;
    
    // Store reference to the button that triggered this
    modal.dataset.triggerButton = button.id || 'unknown';
    modal.style.display = 'flex';
    
    const textarea = document.getElementById('rejection-reason-input');
    if (textarea) {
        textarea.value = ''; // Clear previous content
        textarea.focus();
    }
}

// Close rejection modal
function closeRejectionModal() {
    const modal = document.getElementById('rejection-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.dataset.triggerButton = '';
    }
    const textarea = document.getElementById('rejection-reason-input');
    if (textarea) textarea.value = '';
}

// Submit rejection
function submitRejection() {
    const modal = document.getElementById('rejection-modal');
    const reasonInput = document.getElementById('rejection-reason-input');
    const reason = reasonInput.value.trim();
    
    if (!reason) {
        alert('Please provide a reason for rejection!');
        return;
    }
    
    // Find the form and submit it
    const triggerButtonId = modal.dataset.triggerButton;
    let form = null;
    
    if (triggerButtonId) {
        const triggerButton = document.getElementById(triggerButtonId);
        if (triggerButton) {
            form = triggerButton.closest('form');
        }
    }
    
    // Fallback: find any visible form
    if (!form) {
        form = document.querySelector('form:has(input[name="action"])');
    }
    
    if (!form) {
        alert('Could not find form to submit rejection');
        return;
    }
    
    // Set the rejection reason and action
    const reasonField = form.querySelector('input[name="rejection-reason"]');
    const actionField = form.querySelector('input[name="action"]');
    
    if (reasonField) reasonField.value = reason;
    if (actionField) actionField.value = 'reject';
    
    // Submit the form
    form.submit();
    
    closeRejectionModal();
}

// Unified batch action handler for both manager and salesman
function handleBatchAction(button, action) {
    // Get selected listings from the form containing this button
    const selected = getSelectedListings(button);
    
    if (selected.length === 0) {
        alert('Please select at least one listing first!');
        return;
    }
    
    // Handle rejection (requires modal)
    if (action === 'reject') {
        showRejectionModal(button);
        return;
    }
    
    // Handle delete with confirmation
    if (action === 'delete') {
        if (!confirm(`Are you sure you want to DELETE ${selected.length} listing(s)?`)) {
            return;
        }
    }
    
    // Handle other actions with confirmation
    const confirmations = {
        'approve': 'Are you sure you want to approve the selected listings?',
        'submit': `Are you sure you want to submit ${selected.length} listing(s) for approval?`,
        'won': `Are you sure you want to mark ${selected.length} listing(s) as Closed Won?`,
        'lost': `Are you sure you want to mark ${selected.length} listing(s) as Closed Lost?`,
        'prospect': `Are you sure you want to set ${selected.length} listing(s) to Prospecting?`,
        'negotiate': `Are you sure you want to set ${selected.length} listing(s) to Negotiating?`,
        'process': `Are you sure you want to set ${selected.length} listing(s) to Processing?`,
        'pending': 'Are you sure you want to mark the selected listings as Pending?'
    };
    
    if (confirmations[action] && !confirm(confirmations[action])) {
        return;
    }
    
    // Find the form and submit it
    const form = button.closest('form');
    if (!form) {
        alert('Could not find form to submit action');
        return;
    }
    
    // Set the action
    const actionField = form.querySelector('input[name="action"]');
    if (actionField) {
        actionField.value = action;
    } else {
        // Create hidden input if it doesn't exist
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'action';
        hiddenInput.value = action;
        form.appendChild(hiddenInput);
    }
    
    // Submit the form
    form.submit();
}

// Initialize modal
document.addEventListener('DOMContentLoaded', function() {
    console.log('Batch actions script loaded successfully');
    
    const modal = document.getElementById('rejection-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) closeRejectionModal();
        });
    }
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeRejectionModal();
    });
});
