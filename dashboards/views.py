from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

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
    return render(request, 'dashboards/salesman_dashboard.html')

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    return render(request, 'dashboards/manager_dashboard.html')

@login_required
@user_passes_test(is_ceo)
def ceo_dashboard(request):
    return render(request, 'dashboards/ceo_dashboard.html')

@login_required
def dashboard_view(request):
    if request.user.groups.filter(name='Salesman').exists():
        return redirect('dashboards:salesman_dashboard')
    if request.user.groups.filter(name='Manager').exists():
        return redirect('dashboards:manager_dashboard')
    if request.user.groups.filter(name='CEO').exists():
        return redirect('dashboards:ceo_dashboard')
