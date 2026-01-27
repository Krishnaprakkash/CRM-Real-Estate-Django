from django.shortcuts import render, redirect
from .forms import SalesmanListingForm, ManagerListingForm
from .models import Listing
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone

# Create your views here.

def is_salesman(user):
    return user.groups.filter(name='Salesman').exists()

def is_manager(user):
    return user.groups.filter(name='Manager').exists()


@login_required
@user_passes_test(is_salesman)
def listing_create_salesman(request):
    if request.method == 'POST':
        form = SalesmanListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.id = f"LIST{Listing.objects.count() + 1:04d}"
            listing.branch = request.user.branch
            listing.lead_status = Listing.leadStatusChoices.PENDING
            listing.assigned_salesman = request.user 
            listing.created_at = timezone.now()
            listing.save()
            return redirect('dashboards:salesman_dashboard')
    else:
        form = SalesmanListingForm()
    return render(request, 'inventory/listing_form.html', {'form': form})
        
@login_required
@user_passes_test(is_manager)
def listing_create_manager(request):
    if request.method == 'POST':
        form = ManagerListingForm(request.POST, manager=request.user)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.id = f"LIST{Listing.objects.count() + 1:04d}"
            listing.branch = request.user.branch
            listing.lead_status = Listing.leadStatusChoices.APPROVED
            listing.opportunity_status = Listing.oppStatusChoices.PROSPECTING
            listing.lead_approved_by = request.user
            listing.lead_approved_at = timezone.now()
            listing.created_at = timezone.now()
            listing.save()
            return redirect('dashboards:manager_dashboard')
    else:
        form = ManagerListingForm(manager=request.user)
    return render(request, 'inventory/listing_form.html', {'form': form})

def listings_visible_to(user):
    """Role-based listing visibility"""
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

def listing_list(request):
    listings = listings_visible_to(request.user)
    return render(request, 'inventory/listing_list.html', {'listings': listings})