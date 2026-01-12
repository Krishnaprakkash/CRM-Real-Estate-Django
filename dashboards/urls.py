from . import views
from django.urls import path

app_name = 'dashboards'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('salesman/', views.salesman_dashboard, name='salesman_dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('ceo/', views.ceo_dashboard, name='ceo_dashboard'),
]