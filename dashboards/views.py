from urllib import request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from inventory.views import listings_visible_to
from inventory.models import Listing
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q

# Create your views here.
def is_salesman(user):
    return user.groups.filter(name='Salesman').exists()

def is_manager(user):
    return user.groups.filter(name='Manager').exists()

def is_ceo(user):
    return user.groups.filter(name='CEO').exists()

@login_required
@user_passes_test(is_salesman)
def salesman_dashboard(request):
    listings = listings_visible_to(request.user)
    return render(request, 'dashboards/salesman_dashboard.html', {'listings': listings})

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    if request.method == 'POST' and request.POST.get('action'):
        selected_ids = request.POST.getlist('listing_ids')
        if selected_ids:
            listings_to_update = Listing.objects.filter(id__in=selected_ids)
            action = request.POST.get('action')
            stage = request.POST.get('stage', 'lead')  
            rejection_reason = request.POST.get('rejection-reason', '')

            for listing in listings_to_update:
                if stage == 'lead':
                    if action == 'approve':
                        listing.lead_status = Listing.leadStatusChoices.APPROVED
                        listing.comments = 'No further changes. Proceed as Opportunity.'
                        listing.lead_approved_by = request.user
                        listing.lead_approved_at = timezone.now()
                        listing.opp_status = Listing.oppStatusChoices.PROSPECTING
                        listing.sale_status = None
                    elif action == 'reject':
                        listing.lead_status = Listing.leadStatusChoices.REJECTED
                        listing.comments = rejection_reason
                        listing.lead_approved_by = request.user
                        listing.lead_approved_at = timezone.now()
                        listing.opp_status = None
                        listing.sale_status = None
                    elif action == 'pending':
                        listing.lead_status = Listing.leadStatusChoices.PENDING
                        listing.comments = ''
                        listing.lead_approved_by = None
                        listing.lead_approved_at = None
                        listing.opp_status = None
                        listing.sale_status = None
                
                elif stage == 'opportunity':
                    if action == 'approve':
                        listing.opp_status = Listing.oppStatusChoices.APPROVED
                        listing.comments = 'No further changes. Proceed to sale. '
                        listing.opp_approved_by = request.user
                        listing.opp_approved_at = timezone.now()
                        listing.sale_status = Listing.saleStatusChoices.PROCESSING
                    elif action == 'reject':
                        listing.opp_status = Listing.oppStatusChoices.REJECTED
                        listing.comments = rejection_reason
                        listing.opp_approved_by = request.user
                        listing.opp_approved_at = timezone.now()
                        listing.sale_status = None
                    elif action == 'pending':
                        listing.opp_status = Listing.oppStatusChoices.PENDING
                        listing.comments = ''
                        listing.opp_approved_by = None
                        listing.opp_approved_at = None
                        listing.sale_status = None
                
                listing.save()

            messages.success(request, f"{action.capitalize()} {len(selected_ids)} listings in {stage} stage.")
            
    listings = listings_visible_to(request.user)
    lead_count = listings.filter(
        Q(lead_status=Listing.leadStatusChoices.PENDING) |
        Q(lead_status=Listing.leadStatusChoices.APPROVED) |
        Q(lead_status=Listing.leadStatusChoices.REJECTED)).count()
    lead_active_count = listings.filter(lead_status=Listing.leadStatusChoices.PENDING).count()
    lead_approved_count = listings.filter(lead_status=Listing.leadStatusChoices.APPROVED).count()
    lead_rejected_count = listings.filter(lead_status=Listing.leadStatusChoices.REJECTED).count()
    opp_count = listings.filter(
        Q(opp_status=Listing.oppStatusChoices.PENDING) |
        Q(opp_status=Listing.oppStatusChoices.PROSPECTING) |
        Q(opp_status=Listing.oppStatusChoices.NEGOTIATING) |
        Q(opp_status=Listing.oppStatusChoices.APPROVED) |
        Q(opp_status=Listing.oppStatusChoices.REJECTED)).count()
    opp_active_count = listings.filter(
        Q(opp_status=Listing.oppStatusChoices.PENDING) |
        Q(opp_status=Listing.oppStatusChoices.PROSPECTING) |
        Q(opp_status=Listing.oppStatusChoices.NEGOTIATING)).count()
    opp_approved_count = listings.filter(opp_status=Listing.oppStatusChoices.APPROVED).count()
    opp_rejected_count = listings.filter(opp_status=Listing.oppStatusChoices.REJECTED).count()
    sale_count = listings.filter(
        Q(sale_status=Listing.saleStatusChoices.PROCESSING) |
        Q(sale_status=Listing.saleStatusChoices.CLOSED_WON) |
        Q(sale_status=Listing.saleStatusChoices.CLOSED_LOST)).count()
    sale_active_count = listings.filter(sale_status=Listing.saleStatusChoices.PROCESSING).count()
    sale_won_count = listings.filter(sale_status=Listing.saleStatusChoices.CLOSED_WON).count()
    sale_lost_count = listings.filter(sale_status=Listing.saleStatusChoices.CLOSED_LOST).count()
    stage = request.POST.get('stage', 'lead') 
            
    context = {
        'listings': listings,
        'lead_count': lead_count,
        'lead_active_count': lead_active_count,
        'lead_approved_count': lead_approved_count,
        'lead_rejected_count': lead_rejected_count,
        'opp_count': opp_count,
        'opp_active_count': opp_active_count,
        'opp_approved_count': opp_approved_count,
        'opp_rejected_count': opp_rejected_count,
        'sale_count': sale_count,
        'sale_active_count': sale_active_count,
        'sale_won_count': sale_won_count,
        'sale_lost_count': sale_lost_count,
        'stage': stage
    }
    return render(request, 'dashboards/manager_dashboard.html', context)

@login_required
@user_passes_test(is_ceo)
def ceo_dashboard(request):

    listings = listings_visible_to(request.user)
    return render(request, 'dashboards/ceo_dashboard.html', {'listings': listings})

@login_required
def dashboard_view(request):
    if request.user.groups.filter(name='Salesman').exists():
        return redirect('dashboards:salesman_dashboard')
    if request.user.groups.filter(name='Manager').exists():
        return redirect('dashboards:manager_dashboard')
    if request.user.groups.filter(name='CEO').exists():
        return redirect('dashboards:ceo_dashboard')
