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


# SessionSecurityMiddleware removed to prevent conflicts with Django's authentication system
# The CacheControlMiddleware is sufficient for preventing back button access to authenticated pages
