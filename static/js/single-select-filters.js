// Filter functionality for dashboard tables
document.addEventListener('DOMContentLoaded', function() {
    // Apply filters when any select changes for dashboard tables
    document.querySelectorAll('select[name="type"], select[name="status"], select[name="salesman"]').forEach(filter => {
        filter.addEventListener('change', function() {
            const tabContent = this.closest('.tab-content');
            if (tabContent) {
                applyFilters(tabContent);
            } else {
                // For inventory page (no tab content wrapper)
                applyInventoryFilters();
            }
        });
    });
    
    // Clear filters function for dashboard
    window.clearFilters = function(tabName) {
        const tabContent = document.getElementById(tabName);
        if (tabContent) {
            // Reset all filters in this tab
            tabContent.querySelectorAll('select[name="type"], select[name="status"], select[name="salesman"]').forEach(select => {
                select.value = 'all';
            });
            
            // Apply filters
            applyFilters(tabContent);
        }
    };
    
    // Clear filters function for inventory page
    window.clearInventoryFilters = function() {
        // Reset all filters
        document.querySelectorAll('select[name="type"], select[name="city"], select[name="salesman"]').forEach(select => {
            select.value = 'all';
        });
        
        // Apply filters
        applyInventoryFilters();
    };
    
    // Apply filters for inventory page
    function applyInventoryFilters() {
        const typeFilter = document.getElementById('type-filter');
        const cityFilter = document.getElementById('city-filter');
        const salesmanFilter = document.getElementById('salesman-filter');
        
        const typeValue = typeFilter ? typeFilter.value : '';
        const cityValue = cityFilter ? cityFilter.value : '';
        const salesmanValue = salesmanFilter ? salesmanFilter.value : '';
        
        // Find the inventory table
        const table = document.getElementById('listings-table');
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const typeCell = row.querySelector('td:nth-child(3)'); // Type column (3rd column)
            const cityCell = row.querySelector('td:nth-child(4)'); // City column (4th column)
            const salesmanCell = row.querySelector('td:nth-child(6)'); // Salesman column (6th column)
            
            let showRow = true;
            
            // Filter by type
            if (typeValue && typeValue !== 'all') {
                if (!typeCell || !typeCell.textContent.trim().toLowerCase().includes(typeValue.toLowerCase())) {
                    showRow = false;
                }
            }
            
            // Filter by city
            if (cityValue && cityValue !== 'all') {
                // Get the city from the row's data attribute
                const rowCity = row.getAttribute('data-city');
                
                // If the row has a city attribute, compare it with the filter value
                if (rowCity) {
                    if (rowCity.toLowerCase() !== cityValue.toLowerCase()) {
                        showRow = false;
                    }
                } else {
                    // Fallback to text comparison if no data attribute exists
                    if (!cityCell || !cityCell.textContent.trim().toLowerCase().includes(cityValue.toLowerCase())) {
                        showRow = false;
                    }
                }
            }
            
            // Filter by salesman (using ID-based filtering)
            if (salesmanValue && salesmanValue !== 'all') {
                // Get the salesman ID from the row's data attribute
                const rowSalesmanId = row.getAttribute('data-salesman-id');
                
                // If the row has a salesman ID attribute, compare it with the filter value
                if (rowSalesmanId) {
                    if (rowSalesmanId !== salesmanValue) {
                        showRow = false;
                    }
                } else {
                    // Fallback to text comparison if no data attribute exists
                    if (!salesmanCell || !salesmanCell.textContent.trim().toLowerCase().includes(salesmanValue.toLowerCase())) {
                        showRow = false;
                    }
                }
            }
            
            // Show/hide row
            if (showRow) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    function applyFilters(tabContent) {
        const typeFilter = tabContent.querySelector('select[name="type"]');
        const statusFilter = tabContent.querySelector('select[name="status"]');
        const salesmanFilter = tabContent.querySelector('select[name="salesman"]');
        
        const typeValue = typeFilter ? typeFilter.value : '';
        const statusValue = statusFilter ? statusFilter.value : '';
        const salesmanValue = salesmanFilter ? salesmanFilter.value : '';
        
        // Find the table in this tab
        const table = tabContent.querySelector('.data-table');
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const typeCell = row.querySelector('td:nth-child(4)'); // Type column (4th column)
            const statusCell = row.querySelector('td:nth-child(7)'); // Status column (7th column)
            const salesmanCell = row.querySelector('td:nth-child(6)'); // Salesman column (6th column)
            
            let showRow = true;
            
            // Filter by type
            if (typeValue && typeValue !== 'all') {
                if (!typeCell || !typeCell.textContent.trim().toLowerCase().includes(typeValue.toLowerCase())) {
                    showRow = false;
                }
            }
            
            // Filter by status
            if (statusValue && statusValue !== 'all') {
                if (!statusCell || !statusCell.textContent.trim().toLowerCase().includes(statusValue.toLowerCase())) {
                    showRow = false;
                }
            }
            
            // Filter by salesman (using ID-based filtering)
            if (salesmanValue && salesmanValue !== 'all') {
                // Get the salesman ID from the row's data attribute
                const rowSalesmanId = row.getAttribute('data-salesman-id');
                
                // If the row has a salesman ID attribute, compare it with the filter value
                if (rowSalesmanId) {
                    if (rowSalesmanId !== salesmanValue) {
                        showRow = false;
                    }
                } else {
                    // Fallback to text comparison if no data attribute exists
                    if (!salesmanCell || !salesmanCell.textContent.trim().toLowerCase().includes(salesmanValue.toLowerCase())) {
                        showRow = false;
                    }
                }
            }
            
            // Show/hide row
            if (showRow) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    // Tab switching with stats group toggle
    function switchTab(evt, tabName) {
        // Hide all tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Hide all stats groups
        document.querySelectorAll('.stats-group').forEach(group => {
            group.classList.remove('active');
        });
        
        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        
        // Show selected tab content
        const selectedContent = document.getElementById(tabName);
        if (selectedContent) {
            selectedContent.classList.add('active');
        }
        
        // Show corresponding stats group
        const statsElement = document.getElementById('stats-' + tabName);
        if (statsElement) {
            statsElement.classList.add('active');
        }
        
        // Add active class to clicked button
        if (evt && evt.currentTarget) {
            evt.currentTarget.classList.add('active');
        }
        
        // Update URL hash and localStorage
        updateTabState(tabName);
    }
    
    // Update URL hash and localStorage to preserve tab state
    function updateTabState(tabName) {
        // Update URL hash without scrolling
        if (history.replaceState) {
            const newUrl = window.location.pathname + '#' + tabName;
            history.replaceState(null, null, newUrl);
        } else {
            window.location.hash = tabName;
        }
        
        // Store in localStorage for persistence across sessions
        localStorage.setItem('dashboard_active_tab', tabName);
    }
    
    // Initialize tab state on page load
    function initializeTabState() {
        // Check URL hash first
        const hash = window.location.hash.replace('#', '');
        
        // If hash exists and is a valid tab, use it
        if (hash && document.getElementById(hash)) {
            activateTab(hash);
            return;
        }
        
        // Otherwise check localStorage
        const savedTab = localStorage.getItem('dashboard_active_tab');
        if (savedTab && document.getElementById(savedTab)) {
            activateTab(savedTab);
            return;
        }
        
        // Default to leads tab if no saved state
        activateTab('leads');
    }
    
    // Helper function to activate a specific tab without event
    function activateTab(tabName) {
        // Hide all tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Hide all stats groups
        document.querySelectorAll('.stats-group').forEach(group => {
            group.classList.remove('active');
        });
        
        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        
        // Show selected tab content
        const selectedContent = document.getElementById(tabName);
        if (selectedContent) {
            selectedContent.classList.add('active');
        }
        
        // Show corresponding stats group
        const statsElement = document.getElementById('stats-' + tabName);
        if (statsElement) {
            statsElement.classList.add('active');
        }
        
        // Add active class to corresponding button
        const button = document.querySelector(`.tab-button[onclick*="'${tabName}'"]`);
        if (button) {
            button.classList.add('active');
        }
        
        // Update URL hash and localStorage
        updateTabState(tabName);
    }
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', function() {
        const hash = window.location.hash.replace('#', '');
        if (hash && document.getElementById(hash)) {
            activateTab(hash);
        }
    });
    
    // Initialize on page load
    initializeTabState();
});