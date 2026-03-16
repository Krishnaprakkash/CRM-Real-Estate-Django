"""
Custom middleware for enhanced session security and cache control.
Prevents browser back button access to authenticated pages after logout.
"""

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse


class CacheControlMiddleware(MiddlewareMixin):
    """
    Adds cache control headers to all responses to prevent browser caching
    of authenticated pages. This prevents users from accessing cached pages
    via browser back button after logout.
    """
    
    def process_response(self, request, response):
        # Only apply cache control to authenticated users
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            # Prevent all caching of authenticated pages
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Enhanced session security middleware that checks session validity
    and prevents access to authenticated pages if session is invalid.
    """
    
    def process_request(self, request):
        # Skip middleware for login/logout pages and static files
        if (request.path.startswith('/accounts/login/') or 
            request.path.startswith('/accounts/logout/') or
            request.path.startswith('/static/') or
            request.path.startswith('/admin/')):
            return None
        
        # For authenticated users, check if session is still valid
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            # Check if session has been flushed (logout occurred)
            if not request.session.session_key:
                # Session was cleared, redirect to login
                return redirect('accounts:login')
            
            # Additional check: if user is authenticated but session doesn't contain auth info
            if '_auth_user_id' not in request.session:
                return redirect('accounts:login')
        
        return None
