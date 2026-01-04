from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'branch')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('username', 'email', 'role', 'branch', 'is_active', 'is_staff')
    list_filter = ('role', 'branch', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Fields shown when editing existing user
    fieldsets = BaseUserAdmin.fieldsets + (
        ('CRM Info', {'fields': ('role', 'branch')}),
    )
    
    # Fields shown when creating new user (important!)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'branch'),
        }),
    )
