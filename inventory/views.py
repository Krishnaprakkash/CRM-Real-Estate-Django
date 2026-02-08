from django.shortcuts import render, redirect, get_object_or_404 
from .forms import SalesmanListingForm, ManagerListingForm, VillaDetailsForm, ApartmentDetailsForm, WarehouseDetailsForm, OfficeDetailsForm, RetailDetailsForm
from .models import Listing, VillaDetails, ApartmentDetails, WarehouseDetails, OfficeDetails, RetailDetails
from accounts.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string  
from django.http import JsonResponse 
from django.db.models import Q

# Create your views here.

def is_salesman(user):
    return user.groups.filter(name='Salesman').exists()

def is_manager(user):
    return user.groups.filter(name='Manager').exists()

def is_manager_or_salesman(user):
    return user.groups.filter(name__in=['Salesman', 'Manager']).exists()

def get_details_form(property_type, data=None, instance=None):
    form_map = {
        'Villa': VillaDetailsForm,
        'Apartment': ApartmentDetailsForm,
        'Warehouse': WarehouseDetailsForm,
        'Retail': RetailDetailsForm,
        'Office': OfficeDetailsForm  # Fixed: was OfficeDetails (missing 'Form')
    }
    form_class = form_map.get(property_type)
    if form_class:  # Fixed: was form.class (wrong syntax)
        if data:
            return form_class(data, instance=instance)
        return form_class(instance=instance)
    return None

def get_existing_details(listing):
    try:
        details = listing.get_property_details()
        print(f"Details for {listing.id}: {details}")  # Debug
        return details
    except Exception as e:
        print(f"Error getting details for {listing.id}: {e}")  # Debug
        return None

def generate_listing_id():
    last_listing = Listing.objects.order_by('-created_at').first()
    if last_listing and last_listing.id.startswith('LIST'):  # Fixed: was startsWith (wrong method name)
        try:
            last_num = int(last_listing.id[4:])
            return f"LIST{last_num + 1:04d}"
        except ValueError:
            pass 
    return f"LIST{Listing.objects.count() + 1:04d}"

def get_all_details_forms():
    return {
        'villa_form': VillaDetailsForm(),
        'apartment_form': ApartmentDetailsForm(),
        'warehouse_form': WarehouseDetailsForm(),
        'retail_form': RetailDetailsForm(),
        'office_form': OfficeDetailsForm(),
    }

@login_required
@user_passes_test(is_salesman)
def listing_create_salesman(request):
    if request.method == 'POST':
        form = SalesmanListingForm(request.POST)
        property_type = request.POST.get('type')
        details_form = get_details_form(property_type, request.POST)

        form_valid = form.is_valid()
        details_valid = details_form.is_valid() if details_form else True

        if form_valid and details_valid:
            listing = form.save(commit=False)
            listing.id = generate_listing_id()
            listing.branch = request.user.branch
            listing.lead_status = Listing.leadStatusChoices.PENDING
            listing.assigned_salesman = request.user 
            listing.created_at = timezone.now()
            listing.save()

            if details_form:
                details = details_form.save(commit=False)
                details.listing = listing
                details.save()

            messages.success(request, 'Listing created successfully!')
            return redirect('dashboards:salesman_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')  # Fixed: was 'correxr'
    else:
        form = SalesmanListingForm()

    context = {
        'form': form,
        'title': 'Create New Listing',
        'submit_text': 'Create Listing',
        **get_all_details_forms()
    }
    return render(request, 'inventory/listing_form.html', context)

        
@login_required
@user_passes_test(is_manager)
def listing_create_manager(request):
    if request.method == 'POST':
        form = ManagerListingForm(request.POST, manager=request.user)
        property_type = request.POST.get('type')
        details_form = get_details_form(property_type, request.POST)  # Fixed: was 'propoerty_type'

        form_valid = form.is_valid()
        details_valid = details_form.is_valid() if details_form else True

        if form_valid and details_valid:
            listing = form.save(commit=False)
            listing.id = generate_listing_id()
            listing.branch = request.user.branch
            listing.lead_status = Listing.leadStatusChoices.APPROVED
            listing.opp_status = Listing.oppStatusChoices.PROSPECTING
            listing.lead_approved_by = request.user
            listing.lead_approved_at = timezone.now()
            listing.created_at = timezone.now()
            listing.save()

            if details_form:
                details = details_form.save(commit=False)
                details.listing = listing
                details.save()

            messages.success(request, 'Listing created successfully')  # Fixed: was 'Listin'
            return redirect('dashboards:manager_dashboard')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ManagerListingForm(manager=request.user)

    context = {
        'form': form,
        'title': 'Create New Listing',
        'submit_text': 'Create Listing',
        'is_manager': True,
        **get_all_details_forms()  # Fixed: was 'get_dall_details_forms'
    }
    return render(request, 'inventory/listing_form.html', context)  # Fixed: was {'form': form}


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

@login_required
def listing_list(request):
    listings = listings_visible_to(request.user)
    
    property_type = request.GET.get('type', '')
    city = request.GET.get('city', '')
    salesman_filter = request.GET.get('salesman', '')
    
    if property_type:
        listings = listings.filter(type=property_type)
    if city:
        listings = listings.filter(city__icontains=city)
    if salesman_filter:
        listings = listings.filter(assigned_salesman_id=salesman_filter)
        
    available_types = listings.values_list('type', flat=True).distinct()
    available_cities = listings.values_list('city', flat=True).distinct()
    
    salesmen = None
    if request.user.role == 'Manager':
        salesmen = User.objects.filter(
            branch = request.user.branch,
            role = 'Salesman').order_by('first_name', 'last_name')
        
    lead_count = listings.filter(
        Q(lead_status=Listing.leadStatusChoices.PENDING) |
        Q(lead_status=Listing.leadStatusChoices.APPROVED) |
        Q(lead_status=Listing.leadStatusChoices.REJECTED)).count()
    
    opp_count = listings.filter(
        Q(opp_status=Listing.oppStatusChoices.PENDING) |
        Q(opp_status=Listing.oppStatusChoices.PROSPECTING) |
        Q(opp_status=Listing.oppStatusChoices.NEGOTIATING) |
        Q(opp_status=Listing.oppStatusChoices.APPROVED) |
        Q(opp_status=Listing.oppStatusChoices.REJECTED)).count()
    
    sale_count = listings.filter(
        Q(sale_status=Listing.saleStatusChoices.PROCESSING) |
        Q(sale_status=Listing.saleStatusChoices.CLOSED_WON) |
        Q(sale_status=Listing.saleStatusChoices.CLOSED_LOST)).count()
        
    context = {
        'listings': listings,
        'available_types': available_types,
        'available_cities': available_cities,
        'salesmen': salesmen,
        'filters': {
            'type': property_type,
            'city': city,
            'salesman': salesman_filter
        },
        'total_count': listings.count(),
        'lead_count': lead_count,
        'opp_count': opp_count,
        'sale_count': sale_count
    } 
    return render(request, 'inventory/listing_list.html', context)

@login_required
def listing_detail(request, pk):
    listings = listings_visible_to(request.user)
    listing = get_object_or_404(listings, pk=pk)

    property_details = get_existing_details(listing)
    stage = listing.current_stage

    detail_template_map = {
        'Villa': 'inventory/partials/villa_detail.html',
        'Apartment': 'inventory/partials/apartment_detail.html',
        'Warehouse': 'inventory/partials/warehouse_detail.html',
        'Office': 'inventory/partials/office_detail.html',
        'Retail': 'inventory/partials/retail_detail.html',
    }
    
    context = {
        'listing': listing,
        'property_details': property_details,
        'stage': stage,
        'stage_display': listing.stage_display,
        'detail_template': detail_template_map.get(listing.type),
        'can_edit': (
            request.user.role == 'Manager' or
            listing.assigned_salesman == request.user
    )}

    return render(request, 'inventory/listing_detail.html', context)

@login_required
@user_passes_test(is_manager_or_salesman)
def listing_edit(request, pk):
    listings = listings_visible_to(request.user)
    listing = get_object_or_404(listings, pk=pk)
    
    can_edit = (
        request.user.role =='Manager' or
        listing.assigned_salesman == request.user
    )
    
    if not can_edit:
        messages.error(request, "You are not allowed to edit this Listing.")
        return redirect('inventory:listing_detail', pk=pk)
    
    property_details = get_existing_details(listing)
    
    if request.method == 'POST':
        if request.user.role == 'Manager':
            form = ManagerListingForm(request, instance=listing, manager=request.user)
        else:
            form = SalesmanListingForm(request, instance=listing)
        
        details_form = get_details_form(listing.type, request.POST, instance=property_details)
        
        form_valid = form.is_valid()
        details_valid = details_from.is_valid() if details_from else True
        
        if form_valid and details_valid:
            listing = form.save(commit=False)
            listing.updated_at = timezone.now()
            listing.save()
            
            if details_form:
                details = details_from.save(commit=False)
                details.listing = listing
                details.save()
            
            messages.success(request, 'Listing Updated Successfully.')
            return redirect('inventory:listing_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        if request.user.role == 'Manager':
            form = ManagerListingForm(instance=listing, manager=request.user)
        else:
            form = SalesmanListingForm(instance=listing)
        
        details_form = get_details_form(listing.type, instance=property_details)
        
    context = {
        'form': form,
        'details_form': details_form,
        'listing': listing,
        'title': f'Edit Listing {listing.title}',
        'submit_text': 'Update Listing',
        'is_edit': True,
        'property_type': listing.type,
        **get_all_details_forms()
    }
    
    return render(request, 'inventory/listing_edit.html', context)

@login_required
@user_passes_test(is_manager_or_salesman)
def listing_delete(request, pk):
    listings = listings_visible_to(request.user)
    listing = get_object_or_404(listings, pk=pk)
    
    if request.method == 'POST':
        listing_title = listing.title
        listing.delete()
        messages.success(request, f'Listing {listing_title} successfully deleted.')
        
        if request.user.role == 'Manager':
            return redirect('dashboards:manager_dashboard')
        elif request.user.role == 'Salesman':
            return redirect('dashboards:salesman_dashboard')
    
    return render(request, 'inventory/listing_confirm_delete.html', {'listing': listing})

@login_required 
def get_property_form_ajax(request):
    property_type = request.GET.get('property_type')
    listing_id = request.GET.get('listing_id')

    instance = None
    if listing_id:
        try:
            listing = Listing.objects.get(pk=listing_id)
            if listing.type == property_type:  # Fixed: was 'listing_type'
                instance = get_existing_details(listing)
        except Listing.DoesNotExist:
            pass
            
    template_map = {
        'Villa': 'inventory/partials/villa_form.html',  # Fixed: was missing quote
        'Apartment': 'inventory/partials/apartment_form.html',  # Fixed: was missing quote
        'Warehouse': 'inventory/partials/warehouse_form.html',  # Fixed: was missing quote
        'Office': 'inventory/partials/office_form.html',  # Fixed: was missing quote
        'Retail': 'inventory/partials/retail_form.html',  # Fixed: was missing quote
    }

    if property_type in template_map:
        form = get_details_form(property_type, instance=instance)
        html = render_to_string(
            template_map[property_type],
            {'form': form},
            request=request
        )
        return JsonResponse({'html': html, 'success': True})

    return JsonResponse({'html': '', 'success': False})