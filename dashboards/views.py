from urllib import request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from inventory.views import listings_visible_to
from inventory.models import Listing
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q, Sum

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
    if request.method == 'POST' and request.POST.get('action'):
        selected_ids = request.POST.getlist('listing_ids')
        if selected_ids:
            listings_to_update = Listing.objects.filter(id__in=selected_ids)
            action = request.POST.get('action')
            stage = request.POST.get('stage', 'lead')  
            rejection_reason = request.POST.get('rejection-reason', '')
            
            if action == 'delete':
                count = listings_to_update.count()
                listings_to_update.delete()
                messages.success(request, f'Successfully deleted {count} listing(s).')
                return redirect('dashboards:salesman_dashboard')

            for listing in listings_to_update:       
                if stage == 'opportunity':
                    if action == 'prospect':
                        listing.opp_status = Listing.oppStatusChoices.PROSPECTING
                        listing.comments = 'Prospecting potential buyers for Listing.'
                        listing.sale_status = None
                        listing.sale_price = None
                    elif action == 'negotiate':
                        listing.opp_status = Listing.oppStatusChoices.NEGOTIATING
                        listing.comments = 'Negotiating sale with potential buyer.'
                        listing.sale_status = None
                        listing.sale_price = None
                    elif action == 'submit':
                        listing.opp_status = Listing.oppStatusChoices.PENDING
                        listing.comments = 'Negotiated with buyer. Raising for Approval.'
                        listing.sale_status = None
                        listing.sale_price = None
                        
                elif stage == 'sale':
                    if action == 'process':
                        listing.sale_status = Listing.saleStatusChoices.PROCESSING
                        listing.comments = 'Processing paperwork for handover.'
                    elif action == 'won':
                        listing.sale_status = Listing.saleStatusChoices.CLOSED_WON
                        listing.comments = 'Sale Closed and Won.'
                        listing.sale_closed_at = timezone.now()
                    elif action == 'lost':
                        listing.sale_status = Listing.saleStatusChoices.CLOSED_LOST
                        listing.comments = 'Sale Closed but Lost.'
                        listing.sale_closed_at = timezone.now()
                    
                listing.save()
            
            if action != 'delete':
                messages.success(request, f"{action.capitalize()}d {len(selected_ids)} listings in {stage} stage.")

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
    return render(request, 'dashboards/salesman_dashboard.html', context)

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
            
            if action == 'delete':
                count = listings_to_update.count()
                listings_to_update.delete()
                messages.success(request, f'Successfully deleted {count} listing(s).')
                return redirect('dashboards:manager_dashboard')

            for listing in listings_to_update:
                if stage == 'lead':
                    if action == 'approve':
                        listing.lead_status = Listing.leadStatusChoices.APPROVED
                        listing.comments = 'No further changes. Proceed as Opportunity.'
                        listing.lead_approved_by = request.user
                        listing.lead_approved_at = timezone.now()
                        listing.opp_status = Listing.oppStatusChoices.PROSPECTING
                        listing.opp_price = listing.proposed_price
                        listing.sale_status = None
                    elif action == 'reject':
                        listing.lead_status = Listing.leadStatusChoices.REJECTED
                        listing.comments = rejection_reason
                        listing.lead_approved_by = request.user
                        listing.lead_approved_at = timezone.now()
                        listing.opp_status = None
                        listing.opp_price = None
                        listing.sale_status = None
                    elif action == 'pending':
                        listing.lead_status = Listing.leadStatusChoices.PENDING
                        listing.comments = ''
                        listing.lead_approved_by = None
                        listing.lead_approved_at = None
                        listing.opp_status = None
                        listing.opp_price = None
                        listing.sale_status = None
                
                elif stage == 'opportunity':
                    if action == 'approve':
                        listing.opp_status = Listing.oppStatusChoices.APPROVED
                        listing.comments = 'No further changes. Proceed to sale. '
                        listing.opp_approved_by = request.user
                        listing.opp_approved_at = timezone.now()
                        listing.sale_status = Listing.saleStatusChoices.PROCESSING
                        listing.sale_price = listing.opp_price
                    elif action == 'reject':
                        listing.opp_status = Listing.oppStatusChoices.NEGOTIATING
                        listing.comments = rejection_reason
                        listing.opp_approved_by = request.user
                        listing.opp_approved_at = timezone.now()
                        listing.sale_status = None
                        listing.sale_price = None
                    elif action == 'pending':
                        listing.opp_status = Listing.oppStatusChoices.PENDING
                        listing.comments = ''
                        listing.opp_approved_by = None
                        listing.opp_approved_at = None
                        listing.sale_status = None
                        listing.sale_price = None
                
                listing.save()
            
            if action != 'delete':
                messages.success(request, f"{action.capitalize()}d {len(selected_ids)} listings in {stage} stage.")

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
@user_passes_test(is_salesman)
def salesman_home(request):
    listings = listings_visible_to(request.user)
    
    lead_pending = listings.filter(lead_status=Listing.leadStatusChoices.PENDING).count()
    lead_approved = listings.filter(lead_status=Listing.leadStatusChoices.APPROVED).count()
    lead_rejected = listings.filter(lead_status=Listing.leadStatusChoices.REJECTED).count()
    total_leads = lead_pending + lead_approved + lead_rejected
    
    opp_prospecting = listings.filter(opp_status=Listing.oppStatusChoices.PROSPECTING).count()
    opp_negotiating = listings.filter(opp_status=Listing.oppStatusChoices.NEGOTIATING).count()
    opp_pending = listings.filter(opp_status=Listing.oppStatusChoices.PENDING).count()
    opp_approved = listings.filter(opp_status=Listing.oppStatusChoices.APPROVED).count()
    opp_rejected = listings.filter(opp_status=Listing.oppStatusChoices.REJECTED).count()
    total_opportunities = opp_prospecting + opp_negotiating + opp_pending + opp_approved + opp_rejected
    
    sale_processing = listings.filter(sale_status=Listing.saleStatusChoices.PROCESSING).count()
    sale_won = listings.filter(sale_status=Listing.saleStatusChoices.CLOSED_WON).count()
    sale_lost = listings.filter(sale_status=Listing.saleStatusChoices.CLOSED_LOST).count()
    total_sales = sale_processing + sale_won + sale_lost
    total_closed = sale_won + sale_lost
    
    if total_closed > 0:
        won_percentage = round((sale_won / total_closed) * 100, 1)
    else:
        won_percentage = 0
    
    actual_revenue = listings.filter(
        sale_status=Listing.saleStatusChoices.CLOSED_WON
    ).aggregate(total=Sum('sale_price'))['total'] or 0
    
    projected_revenue = listings.aggregate(total=Sum('proposed_price'))['total'] or 0

    if projected_revenue > 0:
        revenue_percentage = round((actual_revenue / projected_revenue) * 100, 1)
    else:
        revenue_percentage = 0
    total_listings = listings.count()
    
    context = {
        'total_listings': total_listings,
        'total_leads': total_leads,
        'total_opportunities': total_opportunities,
        'total_sales': total_sales,
        'lead_pending': lead_pending,
        'lead_approved': lead_approved,
        'lead_rejected': lead_rejected,
        'opp_prospecting': opp_prospecting,
        'opp_negotiating': opp_negotiating,
        'opp_pending': opp_pending,
        'opp_approved': opp_approved,
        'opp_rejected': opp_rejected,
        'sale_processing': sale_processing,
        'sale_won': sale_won,
        'sale_lost': sale_lost,
        'total_closed': total_closed,
        'won_percentage': won_percentage,
        'actual_revenue': actual_revenue,
        'projected_revenue': projected_revenue,
        'revenue_percentage': revenue_percentage,
    }
    
    return render(request, 'dashboards/salesman_home.html', context)

@login_required
@user_passes_test(is_manager)
def manager_home(request):
    listings = listings_visible_to(request.user)
    
    lead_pending = listings.filter(lead_status=Listing.leadStatusChoices.PENDING).count()
    lead_approved = listings.filter(lead_status=Listing.leadStatusChoices.APPROVED).count()
    lead_rejected = listings.filter(lead_status=Listing.leadStatusChoices.REJECTED).count()
    total_leads = lead_pending + lead_approved + lead_rejected
    
    opp_prospecting = listings.filter(opp_status=Listing.oppStatusChoices.PROSPECTING).count()
    opp_negotiating = listings.filter(opp_status=Listing.oppStatusChoices.NEGOTIATING).count()
    opp_pending = listings.filter(opp_status=Listing.oppStatusChoices.PENDING).count()
    opp_approved = listings.filter(opp_status=Listing.oppStatusChoices.APPROVED).count()
    opp_rejected = listings.filter(opp_status=Listing.oppStatusChoices.REJECTED).count()
    total_opportunities = opp_prospecting + opp_negotiating + opp_pending + opp_approved + opp_rejected
    
    sale_processing = listings.filter(sale_status=Listing.saleStatusChoices.PROCESSING).count()
    sale_won = listings.filter(sale_status=Listing.saleStatusChoices.CLOSED_WON).count()
    sale_lost = listings.filter(sale_status=Listing.saleStatusChoices.CLOSED_LOST).count()
    total_sales = sale_processing + sale_won + sale_lost
    total_closed = sale_won + sale_lost
    
    if total_closed > 0:
        won_percentage = round((sale_won / total_closed) * 100, 1)
    else:
        won_percentage = 0
    
    actual_revenue = listings.filter(
        sale_status=Listing.saleStatusChoices.CLOSED_WON
    ).aggregate(total=Sum('sale_price'))['total'] or 0
    
    projected_revenue = listings.aggregate(total=Sum('proposed_price'))['total'] or 0
    
    if projected_revenue > 0:
        revenue_percentage = round((actual_revenue / projected_revenue) * 100, 1)
    else:
        revenue_percentage = 0
    
    total_listings = listings.count()

    from accounts.models import User
    team_size = User.objects.filter(
        branch=request.user.branch,
        role='Salesman'
    ).count()
    
    context = {
        'total_listings': total_listings,
        'total_leads': total_leads,
        'total_opportunities': total_opportunities,
        'total_sales': total_sales,
        'team_size': team_size,
        'lead_pending': lead_pending,
        'lead_approved': lead_approved,
        'lead_rejected': lead_rejected,
        'opp_prospecting': opp_prospecting,
        'opp_negotiating': opp_negotiating,
        'opp_pending': opp_pending,
        'opp_approved': opp_approved,
        'opp_rejected': opp_rejected,
        'sale_processing': sale_processing,
        'sale_won': sale_won,
        'sale_lost': sale_lost,
        'total_closed': total_closed,
        'won_percentage': won_percentage,
        'actual_revenue': actual_revenue,
        'projected_revenue': projected_revenue,
        'revenue_percentage': revenue_percentage,
    }
    
    return render(request, 'dashboards/manager_home.html', context)

    
@login_required
def dashboard_view(request):
    if request.user.groups.filter(name='Salesman').exists():
        return redirect('dashboards:salesman_dashboard')
    if request.user.groups.filter(name='Manager').exists():
        return redirect('dashboards:manager_dashboard')


@login_required
def home(request):
    if request.user.role == 'Salesman':
        return salesman_home(request)
    elif request.user.role == 'Manager':
        return manager_home(request);
    elif request.user.role == 'CEO':
        return redirect('dashboards:ceo_dashboard')
    else:
        return redirect('accounts:profile')
    