from . import views
from django.urls import path

app_name = 'inventory'

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('<str:pk>/', views.listing_detail, name = 'listing_detail'),

    path('listing/create/salesman/', views.listing_create_salesman, name='listing_create_salesman'),

    path('listing/create/manager/', views.listing_create_manager, name='listing_create_manager'),

    path('ajax/property-form/', views.get_property_form_ajax, name='get_property_form_ajax')
]