from . import views
from . import api_views
from django.urls import path

app_name = 'inventory'

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('<str:pk>/', views.listing_detail, name = 'listing_detail'),
    
    path('listing/create/salesman/', views.listing_create_salesman, name='listing_create_salesman'),
    path('listing/create/manager/', views.listing_create_manager, name='listing_create_manager'),
    
    path('<str:pk>/edit', views.listing_edit, name='listing_edit'),
    path('<str:pk>/delete', views.listing_delete, name='listing_delete'),
    
    path('ajax/property-form/', views.get_property_form_ajax, name='get_property_form_ajax'),
    
    # Inline edit API
    path('api/listing/<str:pk>/inline-edit/', api_views.listing_inline_edit_api, name='listing_inline_edit_api'),
]
