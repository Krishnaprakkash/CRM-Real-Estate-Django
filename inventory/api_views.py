from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
import json
from .models import Listing, VillaDetails, ApartmentDetails, WarehouseDetails, OfficeDetails, RetailDetails
from .forms import SalesmanListingForm, ManagerListingForm, VillaDetailsForm, ApartmentDetailsForm, WarehouseDetailsForm, OfficeDetailsForm, RetailDetailsForm
from accounts.models import User

def is_manager_or_salesman(user):
    return user.groups.filter(name__in=['Salesman', 'Manager']).exists()

def listings_visible_to(user):
    """Role-based listing visibility"""
    if not user.is_authenticated:
        return Listing.objects.none()
    if user.role == 'Salesman':
        return Listing.objects.filter(
            branch=user.branch,
            assigned_salesman=user
        )
    elif user.role == 'Manager':
        return Listing.objects.filter(branch=user.branch)
    elif user.role == 'CEO':
        return Listing.objects.all()
    return Listing.objects.none()

def can_edit_listing(user, listing):
    """Check if user can edit this listing"""
    if user.role == 'Manager':
        return listing.branch == user.branch
    elif user.role == 'Salesman':
        return listing.assigned_salesman == user
    return False

def get_details_form_class(property_type):
    """Get the appropriate details form class"""
    form_map = {
        'Villa': VillaDetailsForm,
        'Apartment': ApartmentDetailsForm,
        'Warehouse': WarehouseDetailsForm,
        'Retail': RetailDetailsForm,
        'Office': OfficeDetailsForm
    }
    return form_map.get(property_type)

def get_property_details(listing):
    """Get property-specific details"""
    try:
        return listing.get_property_details()
    except:
        return None


@login_required
@user_passes_test(is_manager_or_salesman)
@require_http_methods(["GET", "POST"])
@csrf_exempt
def listing_inline_edit_api(request, pk):
    """API endpoint for inline editing of listings"""
    try:
        # Get listing with proper permissions
        listings = listings_visible_to(request.user)
        listing = get_object_or_404(listings, pk=pk)
        
        # Check edit permissions
        if not can_edit_listing(request.user, listing):
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to edit this listing.'
            }, status=403)
        
        if request.method == 'GET':
            # Return current data and available options
            property_details = get_property_details(listing)
            
            # Get property-specific data
            property_data = {}
            if property_details:
                for field in property_details._meta.fields:
                    if field.name != 'listing':  # Skip the foreign key
                        value = getattr(property_details, field.name)
                        if isinstance(value, bool):
                            property_data[field.name] = value
                        elif value is not None:
                            property_data[field.name] = str(value)
            
            # Get available salesmen for Manager role
            salesmen_options = []
            if request.user.role == 'Manager':
                salesmen = User.objects.filter(
                    branch=request.user.branch,
                    role='Salesman'
                ).order_by('first_name', 'last_name')
                salesmen_options = [
                    {
                        'value': str(salesman.id),
                        'label': salesman.get_full_name() or salesman.username
                    }
                    for salesman in salesmen
                ]
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': listing.id,
                    'title': listing.title,
                    'type': listing.type,
                    'address': listing.address,
                    'city': listing.city,
                    'proposed_price': float(listing.proposed_price) if listing.proposed_price else None,
                    'assigned_salesman': str(listing.assigned_salesman.id) if listing.assigned_salesman else None,
                    'comments': listing.comments or '',
                    'property_details': property_data
                },
                'options': {
                    'salesmen': salesmen_options,
                    'property_type': listing.type
                }
            })
            
        elif request.method == 'POST':
            # Handle form submission
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON data.'
                }, status=400)
            
            # Get forms - only include fields that are actually being edited
            form_data = {}
            if 'title' in data:
                form_data['title'] = data['title']
            if 'proposed_price' in data:
                form_data['proposed_price'] = data['proposed_price']
            if 'assigned_salesman' in data and request.user.role == 'Manager':
                form_data['assigned_salesman'] = data['assigned_salesman']
            # Skip status field - status columns are now read-only
            # Status will not be processed or saved during inline edit
            
            if request.user.role == 'Manager':
                form = ManagerListingForm(form_data, instance=listing, manager=request.user)
            else:
                form = SalesmanListingForm(form_data, instance=listing)
            
            # Get property details form
            details_form_class = get_details_form_class(listing.type)
            property_details = get_property_details(listing)
            
            if details_form_class and 'property_details' in data:
                details_form = details_form_class(data['property_details'], instance=property_details)
            else:
                details_form = None
            
            # Validate forms
            form_valid = form.is_valid()
            details_valid = details_form.is_valid() if details_form else True
            
            if form_valid and details_valid:
                with transaction.atomic():
                    # Save main listing
                    listing = form.save(commit=False)
                    listing.updated_at = timezone.now()
                    listing.save()
                    
                    # Save property details
                    if details_form:
                        details = details_form.save(commit=False)
                        details.listing = listing
                        details.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Listing updated successfully.',
                    'data': {
                        'id': listing.id,
                        'title': listing.title,
                        'type': listing.type,
                        'address': listing.address,
                        'city': listing.city,
                        'proposed_price': float(listing.proposed_price) if listing.proposed_price else None,
                        'assigned_salesman': listing.assigned_salesman.get_full_name() if listing.assigned_salesman else '—',
                        'comments': listing.comments or '',
                        'price_display': f'₹{float(listing.proposed_price):,.0f}' if listing.proposed_price else '—'
                    }
                })
            else:
                # Return validation errors
                errors = {}
                if not form_valid:
                    errors.update(form.errors)
                if details_form and not details_valid:
                    errors.update(details_form.errors)
                
                return JsonResponse({
                    'success': False,
                    'error': 'Validation failed.',
                    'errors': errors
                }, status=400)
                
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)
                    
