from . import views
from django.urls import path

app_name = 'dashboards'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('salesman/', views.salesman_dashboard, name='salesman_dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('ceo/', views.ceo_dashboard, name='ceo_dashboard'),
    path('', views.home, name='home'),
    path('home/salesman/', views.salesman_home, name='salesman_home'),
    path('home/manager/', views.manager_home, name='manager_home')
]