// Multi-select filter functionality
document.addEventListener('DOMContentLoaded', function() {
    // Type filter
    const typeCheckboxes = document.querySelectorAll('.type-checkbox');
    const typeFilterBtn = document.getElementById('type-filter-btn');
    const typeFilterLabel = document.getElementById('type-filter-label');
    const typeFilterInput = document.getElementById('type-filter-input');
    
    typeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateFilter('type', this.checked, this.value);
        });
    });
    
    // City filter
    const cityCheckboxes = document.querySelectorAll('.city-checkbox');
    const cityFilterBtn = document.getElementById('city-filter-btn');
    const cityFilterLabel = document.getElementById('city-filter-label');
    const cityFilterInput = document.getElementById('city-filter-input');
    
    cityCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateFilter('city', this.checked, this.value);
        });
    });
    
    // Salesman filter
    const salesmanCheckboxes = document.querySelectorAll('.salesman-checkbox');
    const salesmanFilterBtn = document.getElementById('salesman-filter-btn');
    const salesmanFilterLabel = document.getElementById('salesman-filter-label');
    const salesmanFilterInput = document.getElementById('salesman-filter-input');
    
    salesmanCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateFilter('salesman', this.checked, this.value);
        });
    });
    
    function updateFilter(filterType, isChecked, value) {
        let checkboxes, label, input, allCheckbox;
        
        if (filterType === 'type') {
            checkboxes = document.querySelectorAll('.type-checkbox');
            label = typeFilterLabel;
            input = typeFilterInput;
            allCheckbox = document.querySelector('#type-filter-dropdown input[value="all"]');
        } else if (filterType === 'city') {
            checkboxes = document.querySelectorAll('.city-checkbox');
            label = cityFilterLabel;
            input = cityFilterInput;
            allCheckbox = document.querySelector('#city-filter-dropdown input[value="all"]');
        } else if (filterType === 'salesman') {
            checkboxes = document.querySelectorAll('.salesman-checkbox');
            label = salesmanFilterLabel;
            input = salesmanFilterInput;
            allCheckbox = document.querySelector('#salesman-filter-dropdown input[value="all"]');
        }
        
        // Handle "All" checkbox logic
        if (value === 'all') {
            if (isChecked) {
                // Select all checkboxes
                checkboxes.forEach(cb => cb.checked = true);
            } else {
                // Deselect all checkboxes
                checkboxes.forEach(cb => cb.checked = false);
            }
        } else {
            // If any specific checkbox is unchecked, uncheck "All"
            if (!isChecked) {
                allCheckbox.checked = false;
            }
            
            // If all specific checkboxes are checked, check "All"
            const allSpecificChecked = Array.from(checkboxes).every(cb => cb.checked);
            if (allSpecificChecked) {
                allCheckbox.checked = true;
            }
        }
        
        // Update label and hidden input
        updateFilterDisplay(filterType, label, input, checkboxes, allCheckbox);
    }
    
    function updateFilterDisplay(filterType, label, input, checkboxes, allCheckbox) {
        const checkedValues = Array.from(checkboxes).filter(cb => cb.checked).map(cb => cb.value);
        
        if (allCheckbox.checked || checkedValues.length === 0) {
            // Show "All" if "All" is checked or no specific options are selected
            if (filterType === 'type') {
                label.textContent = 'All Types';
            } else if (filterType === 'city') {
                label.textContent = 'All Cities';
            } else {
                label.textContent = 'All Salesmen';
            }
            input.value = 'all';
        } else {
            // Show selected values
            const selectedText = checkedValues.slice(0, 2).join(', ');
            const moreCount = checkedValues.length > 2 ? ' +' + (checkedValues.length - 2) + ' more' : '';
            label.textContent = selectedText + moreCount;
            input.value = checkedValues.join(',');
        }
    }
    
    // Initialize filter displays
    updateFilterDisplay('type', typeFilterLabel, typeFilterInput, typeCheckboxes, document.querySelector('#type-filter-dropdown input[value="all"]'));
    updateFilterDisplay('city', cityFilterLabel, cityFilterInput, cityCheckboxes, document.querySelector('#city-filter-dropdown input[value="all"]'));
    
    // Initialize salesman filter if user is manager and has salesmen
    if (document.querySelector('#salesman-filter-dropdown')) {
        updateFilterDisplay('salesman', salesmanFilterLabel, salesmanFilterInput, salesmanCheckboxes, document.querySelector('#salesman-filter-dropdown input[value="all"]'));
    }
});