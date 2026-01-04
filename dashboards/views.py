from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def dashboard_view(request):
    if request.user.groups.filter(name='Salesman').exists():
        return HttpResponse("Salesman Dashboard")
    if request.user.groups.filter(name='Manager').exists():
        return HttpResponse("Manager Dashboard")
    if request.user.groups.filter(name='CEO').exists():
        return HttpResponse("CEO Dashboard")
