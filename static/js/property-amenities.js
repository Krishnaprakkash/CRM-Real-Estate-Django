document.addEventListener('DOMContentLoaded', function() {
    // Enhanced property amenities highlighting system
    // Works across all property forms with consistent green gradient highlighting
    
    // Find all property amenity checkbox containers
    var amenityCheckboxes = document.querySelectorAll('.property-form-partial .form-check');
    
    amenityCheckboxes.forEach(function(wrapper) {
        var checkbox = wrapper.querySelector('input[type="checkbox"]') || wrapper.querySelector('input');
        var label = wrapper.querySelector('.form-check-label') || wrapper.querySelector('label');
        
        if (!checkbox || !label) return;

        // Store original styles for hover effect
        var originalBackground = label.style.background || '#f8f9fa';
        var originalColor = label.style.color || '#495057';
        var originalBorderColor = label.style.borderColor || '#e9ecef';
        var originalFontWeight = label.style.fontWeight || '500';

        // Set initial state based on checkbox
        updateAmenityState(checkbox, label, wrapper);

        // Handle checkbox changes
        checkbox.addEventListener('change', function() {
            updateAmenityState(checkbox, label, wrapper);
        });

        // Handle label clicks with immediate visual feedback
        label.addEventListener('click', function(e) {
            // Prevent default to avoid double-triggering
            e.preventDefault();
            
            // Toggle checkbox state
            checkbox.checked = !checkbox.checked;
            
            // Update visual state immediately
            updateAmenityState(checkbox, label, wrapper);
        });

        // Enhanced hover effects
        label.addEventListener('mouseenter', function() {
            if (checkbox.checked) {
                // Already selected - enhance the green gradient (lighter to darker)
                label.style.background = 'linear-gradient(135deg, #218838 0%, #1e7e34 100%)';
                label.style.transform = 'translateY(-1px)';
                label.style.boxShadow = '0 4px 12px rgba(40, 167, 69, 0.3)';
            } else {
                // Not selected - white box with dark blue outline on hover
                label.style.background = '#ffffff';
                label.style.borderColor = '#1e3c72';
                label.style.transform = 'translateY(-1px)';
                label.style.boxShadow = '0 4px 12px rgba(42, 82, 152, 0.2)';
            }
        });

        label.addEventListener('mouseleave', function() {
            // Reset to current state without hover effects
            updateAmenityState(checkbox, label, wrapper);
            label.style.transform = 'translateY(0)';
            label.style.boxShadow = 'none';
        });

        // Accessibility: keyboard navigation
        wrapper.addEventListener('keydown', function(e) {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                checkbox.checked = !checkbox.checked;
                updateAmenityState(checkbox, label, wrapper);
            }
        });

        // Ensure wrapper can receive focus for keyboard navigation
        wrapper.tabIndex = 0;
        wrapper.style.cursor = 'pointer';
    });

    function updateAmenityState(checkbox, label, wrapper) {
        if (checkbox.checked) {
            // Selected state - green gradient like Create buttons
            wrapper.classList.add('active');
            label.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
            label.style.color = 'white';
            label.style.borderColor = 'transparent';
            label.style.fontWeight = '600';
            label.style.boxShadow = '0 2px 8px rgba(40, 167, 69, 0.25)';
        } else {
            // Unselected state
            wrapper.classList.remove('active');
            label.style.background = '#f8f9fa';
            label.style.color = '#495057';
            label.style.borderColor = '#e9ecef';
            label.style.fontWeight = '500';
            label.style.boxShadow = 'none';
        }
    }
});
