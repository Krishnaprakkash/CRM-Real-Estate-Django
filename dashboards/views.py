from urllib import request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from inventory.views import listings_visible_to
from inventory.models import Listing
from django.utils import timezone
from django.contrib import messages

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
            if action == 'approve':
                listings_to_update.update(
                    status=Listing.statusChoices.APPROVED,
                    gm_approved_by=request.user,
                    gm_approved_at=timezone.now(),
                    comments=''
                )
                messages.success(request, f"Approved {len(selected_ids)} listings.")
            elif action == 'pending':
                listings_to_update.update(
                    status=Listing.statusChoices.PENDING_GM_APPROVAL,
                    gm_approved_by=None,
                    gm_approved_at=None,
                    comments=''
                )
                messages.success(request, f"Marked {len(selected_ids)} as pending.")
            elif action == 'reject':
                listings_to_update.update(
                    status=Listing.statusChoices.REJECTED,
                    gm_approved_by=request.user,
                    gm_approved_at=timezone.now(),
                )
                messages.success(request, f"Rejected {len(selected_ids)} listings.")

    listings = listings_visible_to(request.user)
    return render(request, 'dashboards/manager_dashboard.html', {'listings': listings})

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
