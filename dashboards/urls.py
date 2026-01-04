from . import views
from django.urls import path

app_name = 'dashboards'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
]