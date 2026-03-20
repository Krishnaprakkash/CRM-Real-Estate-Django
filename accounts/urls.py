from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('create-salesman/', views.create_salesman_view, name='create_salesman'),
    path('login-redirect/', views.login_redirect, name='login_redirect'),
]
