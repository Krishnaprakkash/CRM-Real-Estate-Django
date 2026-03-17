from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseForbidden
from .forms import ProfileUpdateForm, SalesmanCreationForm

def login_view(request):
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('dashboards:home')  # Redirect to home
    
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(next_url or 'dashboards:home')  # Changed from dashboard to home
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})

def logout_view(request):
    # Get user info before logout for logging purposes
    user = request.user
    
    # Clear all session data to prevent browser back button access
    request.session.flush()
    
    # Additional security: clear any cached authentication data
    if hasattr(request, 'user'):
        request.user = None
    
    # Add cache control headers to logout response
    response = redirect('accounts:login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    messages.success(request, 'You have been logged out successfully.')
    return response

@login_required
def profile_view(request):
    """User profile page with update functionality"""
    user = request.user
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'Manager', login_url='accounts:login')
def create_salesman_view(request):
    """View for managers to create new salesmen"""
    if request.method == 'POST':
        form = SalesmanCreationForm(request.POST, manager=request.user)
        if form.is_valid():
            salesman = form.save(commit=False)
            # Set the branch to match the manager's branch
            salesman.branch = request.user.branch
            # The password is already set by the form's save method
            salesman.save()
            
            # Add success message that will persist
            messages.success(request, f'Salesman "{salesman.get_full_name()}" has been created successfully!')
            
            # Return the same page with success message instead of redirecting
            context = {
                'form': SalesmanCreationForm(manager=request.user),  # Reset form
                'manager': request.user,
                'success_message': f'Salesman "{salesman.get_full_name()}" has been created successfully!'
            }
            return render(request, 'accounts/create_salesman.html', context)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SalesmanCreationForm(manager=request.user)
    
    context = {
        'form': form,
        'manager': request.user,
    }
    
    return render(request, 'accounts/create_salesman.html', context)
