from django import forms
from .models import Listing, VillaDetails, ApartmentDetails, WarehouseDetails, OfficeDetails, RetailDetails
from accounts.models import User

class SalesmanListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'type', 'address', 'city', 'proposed_price']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make type field read-only for editing
        if self.instance and self.instance.pk:
            self.fields['type'].widget.attrs['readonly'] = True
            self.fields['type'].widget.attrs['style'] = 'background-color: #f8f9fa; cursor: not-allowed;'
            # Ensure the field is not required for editing since it's read-only
            self.fields['type'].required = False

class ManagerListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'type', 'address', 'city', 'proposed_price', 'assigned_salesman']
    
    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)
        if manager and hasattr(manager, 'branch'):
            self.fields['assigned_salesman'].queryset = User.objects.filter(
                branch=manager.branch,
                role='Salesman'
            ).order_by('first_name', 'last_name')
        
        # Make type field read-only for editing
        if self.instance and self.instance.pk:
            self.fields['type'].widget.attrs['readonly'] = True
            self.fields['type'].widget.attrs['style'] = 'background-color: #f8f9fa; cursor: not-allowed;'
            # Ensure the field is not required for editing since it's read-only
            self.fields['type'].required = False

class VillaDetailsForm(forms.ModelForm):
    class Meta:
        model = VillaDetails
        exclude = ['listing']
        widgets = {
            'bhk_config': forms.Select(attrs={'class': 'form-select'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'plot_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'built_up_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'carpet_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'number_of_floors': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'furnishing_status': forms.Select(attrs={'class': 'form-select'}),
            'facing': forms.Select(attrs={'class': 'form-select'}),
            'covered_parking_spaces': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'open_parking_spaces': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'parking_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'swimming_pool': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'private_garden': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'servant_quarters': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'power_backup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'security_24x7': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gated_community': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ApartmentDetailsForm(forms.ModelForm):
    class Meta:
        model = ApartmentDetails
        exclude = ['listing']
        widgets = {
            'bhk_config': forms.Select(attrs={'class': 'form-select'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'balconies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'carpet_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'built_up_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'super_built_up_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'floor_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'tower': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_number': forms.TextInput(attrs={'class': 'form-control'}),
            'parking_type': forms.Select(attrs={'class': 'form-select'}),
            'parking_spaces': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'furnishing_status': forms.Select(attrs={'class': 'form-select'}),
            'lift_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'power_backup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'swimming_pool': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gym': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'clubhouse': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'security_24x7': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'maintenance_monthly': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class WarehouseDetailsForm(forms.ModelForm):
    class Meta:
        model = WarehouseDetails
        exclude = ['listing']
        widgets = {
           'total_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'covered_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'open_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'office_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ceiling_height_ft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'floor_type': forms.Select(attrs={'class': 'form-select'}),
            'structure_type': forms.Select(attrs={'class': 'form-select'}),
            'floor_load_capacity_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'loading_docks': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'ground_level_doors': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'truck_accessible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'container_accessible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'power_load_kva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'three_phase_power': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'power_backup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fire_system_type': forms.Select(attrs={'class': 'form-select'}),
            'fire_noc': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cold_storage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'hazmat_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'truck_parking_spaces': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'car_parking_spaces': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'security_24x7': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cctv': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RetailDetailsForm(forms.ModelForm):
    class Meta:
        model = RetailDetails
        exclude = ['listing']
        widgets = {
            'carpet_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'frontage_ft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ceiling_height_ft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'floor_location': forms.Select(attrs={'class': 'form-select'}),
            'mezzanine_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'location_type': forms.Select(attrs={'class': 'form-select'}),
            'mall_name': forms.TextInput(attrs={'class': 'form-control'}),
            'display_window': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'corner_shop': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'main_road_facing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'storage_room': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'attached_restroom': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'power_load_kw': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'air_conditioning': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'power_backup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dedicated_parking': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'common_parking_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'external_signage_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'food_license_possible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'estimated_footfall': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_monthly': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class OfficeDetailsForm(forms.ModelForm):
    class Meta:
        model = OfficeDetails
        exclude = ['listing']
        widgets = {
           'office_type': forms.Select(attrs={'class': 'form-select'}),
            'furnishing_status': forms.Select(attrs={'class': 'form-select'}),
            'workstation_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'carpet_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'built_up_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'number_of_cabins': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'conference_rooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'meeting_rooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'reception_area': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'floor_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'building_name': forms.TextInput(attrs={'class': 'form-control'}),
            'building_grade': forms.Select(attrs={'class': 'form-select'}),
            'pantry': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cafeteria': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'server_room': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'parking_type': forms.Select(attrs={'class': 'form-select'}),
            'car_parking_spaces': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'power_load_kva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'power_backup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'central_ac': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fiber_optic': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'access_24x7': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'lifts': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'security_24x7': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fire_safety_system': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'maintenance_per_sqft': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


# Helper to get the correct form based on property type
def get_details_form(property_type, *args, **kwargs):
    """Returns the appropriate details form based on property type"""
    form_map = {
        Listing.typeChoices.VILLA: VillaDetailsForm,
        Listing.typeChoices.APARTMENT: ApartmentDetailsForm,
        Listing.typeChoices.WAREHOUSE: WarehouseDetailsForm,
        Listing.typeChoices.RETAIL_STORE: RetailDetailsForm,
        Listing.typeChoices.OFFICE_SPACE: OfficeDetailsForm,
    }
    form_class = form_map.get(property_type)
    if form_class:
        return form_class(*args, **kwargs)
    return None
