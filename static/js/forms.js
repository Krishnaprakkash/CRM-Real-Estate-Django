// Listing Edit Form Functions
document.addEventListener('DOMContentLoaded', function() {
    // Make type field read-only for listing edit forms (don't disable to allow form submission)
    const listingEditForm = document.getElementById('listing-edit-form');
    if (listingEditForm) {
        const typeField = document.querySelector('[name="type"]');
        if (typeField) {
            // Ensure the field is read-only but not disabled (to allow form submission)
            typeField.readOnly = true;
            typeField.disabled = false; // Make sure it's not disabled
            typeField.style.backgroundColor = '#f8f9fa';
            typeField.style.cursor = 'not-allowed';
            typeField.style.opacity = '0.6';
        }
    }
});


// Listing Create Form - Dynamic Property Type Fields
document.addEventListener('DOMContentLoaded', function() {
    const listingForm = document.getElementById('listing-form');
    
    if (listingForm) {
        const typeSelect = document.getElementById('id_type');
        const propertyFields = document.querySelectorAll('.property-fields');
        
        const typeToFieldsMap = {
            'Villa': 'villa-fields',
            'Apartment': 'apartment-fields',
            'Warehouse': 'warehouse-fields',
            'Retail': 'retail-fields',
            'Office': 'office-fields',
        };
        
        function showPropertyFields() {
            const selectedType = typeSelect.value;
            
            // Hide all and disable inputs
            propertyFields.forEach(container => {
                container.style.display = 'none';
                container.querySelectorAll('input, select, textarea').forEach(input => {
                    input.disabled = true;
                });
            });
            
            // Show selected and enable inputs
            const fieldsId = typeToFieldsMap[selectedType];
            if (fieldsId) {
                const container = document.getElementById(fieldsId);
                if (container) {
                    container.style.display = 'block';
                    container.querySelectorAll('input, select, textarea').forEach(input => {
                        input.disabled = false;
                    });
                }
            }
        }
        
        // Add event listener to trigger the function
        typeSelect.addEventListener('change', showPropertyFields);
        
        // Call on page load to show correct fields if form has errors or is being edited
        showPropertyFields();
    }
});