// ===== BATCH ACTION FUNCTIONALITY =====

function toggleSelectAll(source) {
    const table = source.closest('table');
    if (!table) return;
    const checkboxes = table.querySelectorAll('input.listing-checkbox');
    checkboxes.forEach(cb => cb.checked = source.checked);
    console.log(`Toggled ${checkboxes.length} checkboxes`);
}

// Manager batch actions
function setAction(action, suffix = 'leads') {
    console.log('Action clicked:', action, 'for', suffix);

    const formSelector = `#batch-form-${suffix}`;
    const selected = document.querySelectorAll(`${formSelector} input.listing-checkbox:checked`);

    if (selected.length === 0) {
        alert(`Please select at least one listing first!`);
        return;
    }

    if (action === 'delete') {
        const confirmMsg = `Are you sure you want to DELETE ${selected.length} listing(s)?\n\nThis action CANNOT BE UNDONE.`;
        if (!confirm(confirmMsg)) {
            return;
        }
    }

    if (suffix === 'opps' && action !== 'delete') {
        const invalidItems = [];
        selected.forEach((checkbox) => {
            const row = checkbox.closest('tr');
            if (row) {
                const columnValue = row.cells[5]?.textContent?.trim();
                if (columnValue !== 'Pending Approval') {
                    const itemId = checkbox.value || row.cells[0]?.textContent?.trim();
                    invalidItems.push({ id: itemId, value: columnValue });
                }
            }
        });
        if (invalidItems.length > 0) {
            alert(`Cannot perform batch action. ${invalidItems.length} selected item(s) have not been submitted for approval.`);
            return;
        }
    }

    if (action === 'reject') {
        const reason = prompt('Enter rejection reason (required):');
        if (!reason || !reason.trim()) {
            alert('Rejection reason is required!');
            return;
        }
        const rr = document.getElementById(`rejection-reason-${suffix}`);
        if (rr) rr.value = reason;
    }

    if (action === 'approve') {
        if (!confirm(`Are you sure you want to approve the selected listings?`)) {
            return;
        }
    }

    const ba = document.getElementById(`batch-action-${suffix}`);
    const st = document.getElementById(`stage-${suffix}`);
    const bf = document.getElementById(`batch-form-${suffix}`);
    if (ba) ba.value = action;
    if (st) st.value = (st.value || '');
    console.log(`Submitting ${selected.length} listings for ${action} (form ${formSelector})`);
    if (bf) bf.submit();
}

// Salesman batch actions
function setSalesmanAction(action, suffix) {
    console.log('Salesman action clicked:', action, 'for', suffix);

    const formSelector = `#batch-form-${suffix}`;
    const selected = document.querySelectorAll(`${formSelector} input.listing-checkbox:checked`);

    if (selected.length === 0) {
        alert(`Please select at least one listing first!`);
        return;
    }

    if (action === 'delete') {
        const confirmMsg = `Are you sure you want to DELETE ${selected.length} listing(s)?\n\nThis action CANNOT BE UNDONE.`;
        if (!confirm(confirmMsg)) {
            return;
        }
    }

    // Validation for moving to negotiating
    if (suffix === 'opps' && action === 'negotiating') {
        const invalidItems = [];
        selected.forEach((checkbox) => {
            const row = checkbox.closest('tr');
            if (row) {
                const statusCell = row.cells[5]?.textContent?.trim();
                if (statusCell !== 'Prospecting') {
                    const itemId = checkbox.value || row.cells[0]?.textContent?.trim();
                    invalidItems.push({ id: itemId, status: statusCell });
                }
            }
        });
        if (invalidItems.length > 0) {
            alert(`Cannot submit for approval. ${invalidItems.length} selected item(s) are not in Prospecting status.`);
            return;
        }
    }

    // Validation for submitting opportunities
    if (suffix === 'opps' && action === 'submit') {
        const invalidItems = [];
        selected.forEach((checkbox) => {
            const row = checkbox.closest('tr');
            if (row) {
                const statusCell = row.cells[5]?.textContent?.trim();
                if (statusCell !== 'Negotiating') {
                    const itemId = checkbox.value || row.cells[0]?.textContent?.trim();
                    invalidItems.push({ id: itemId, status: statusCell });
                }
            }
        });
        if (invalidItems.length > 0) {
            alert(`Cannot submit for approval. ${invalidItems.length} selected item(s) are not in Negotiating status.`);
            return;
        }

        // Check if already submitted
        const alreadySubmitted = [];
        selected.forEach((checkbox) => {
            const row = checkbox.closest('tr');
            if (row) {
                const statusCell = row.cells[5]?.textContent?.trim();
                if (statusCell === 'Pending Approval' || statusCell === 'Approved') {
                    const itemId = checkbox.value || row.cells[0]?.textContent?.trim();
                    alreadySubmitted.push({ id: itemId, status: statusCell });
                }
            }
        });
        if (alreadySubmitted.length > 0) {
            alert(`Cannot submit for approval. ${alreadySubmitted.length} selected item(s) are already submitted for approval.`);
            return;
        }
    }

    // Validation for processing sales
    if (suffix === 'sale' && (action === 'won' || action === 'lost')) {
        const invalidItems = [];
        selected.forEach((checkbox) => {
            const row = checkbox.closest('tr');
            if (row) {
                const statusCell = row.cells[5]?.textContent?.trim();
                if (statusCell !== 'Processing') {
                    const itemId = checkbox.value || row.cells[0]?.textContent?.trim();
                    invalidItems.push({ id: itemId, status: statusCell });
                }
            }
        });
        if (invalidItems.length > 0) {
            alert(`Cannot mark as ${action}. ${invalidItems.length} selected item(s) are already closed.`);
            return;
        }
    }

    // Confirmations for critical actions
    const confirmations = {
        'submit': `Are you sure you want to submit ${selected.length} listing(s) for approval?`,
        'won': `Are you sure you want to mark ${selected.length} listing(s) as Closed Won?`,
        'lost': `Are you sure you want to mark ${selected.length} listing(s) as Closed Lost?`
    };

    if (confirmations[action]) {
        if (!confirm(confirmations[action])) {
            return;
        }
    }

    const ba = document.getElementById(`batch-action-${suffix}`);
    const st = document.getElementById(`stage-${suffix}`);
    const bf = document.getElementById(`batch-form-${suffix}`);
    if (ba) ba.value = action;
    if (st) st.value = (st.value || '');
    console.log(`Submitting ${selected.length} listings for ${action} (form ${formSelector})`);
    if (bf) bf.submit();
}