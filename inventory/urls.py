from . import views
from django.urls import path

app_name = 'inventory'

urlpatterns = [
    path('listing/create/salesman/', views.listing_create_salesman, name='listing_create_salesman'),
    path('listing/create/manager/', views.listing_create_manager, name='listing_create_manager'),
]