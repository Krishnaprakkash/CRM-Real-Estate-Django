from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Listing
from accounts.models import User
import json

def is_manager_or_salesman(user):
    return user.role in ['Salesman', 'Manager']

@login_required
@user_passes_test(is_manager_or_salesman)
@csrf_exempt
@require_POST
def listing_inline_save_api(request, pk):
    """
    JSON-only API endpoint for inline editing
    Accepts JSON data and returns JSON response
    """
    try:
        # Get the listing with proper permissions
        listings = Listing.objects.all()
        if request.user.role == 'Salesman':
            listings = listings.filter(assigned_salesman=request.user)
        elif request.user.role == 'Manager':
            listings = listings.filter(branch=request.user.branch)
        
        listing = get_object_or_404(listings, pk=pk)
        
        # Check permissions
        can_edit = (
            request.user.role == 'Manager' or
            listing.assigned_salesman == request.user
        )
        
        if not can_edit:
            return JsonResponse({
                'success': False,
                'error': 'You are not allowed to edit this listing.'
            }, status=403)
        
        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data.'
            }, status=400)
        
        # Validate required fields
        if not data.get('title'):
            return JsonResponse({
                'success': False,
                'error': 'Title is required.'
            }, status=400)
        
        # Update fields
        with transaction.atomic():
            # Update basic fields
            if 'title' in data:
                listing.title = data['title']
            
            if 'proposed_price' in data:
                try:
                    price = float(data['proposed_price']) if data['proposed_price'] else None
                    if price is not None and price < 0:
                        raise ValueError("Price cannot be negative")
                    listing.proposed_price = price
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid price value.'
                    }, status=400)
            
            # Update salesman (Manager only)
            if request.user.role == 'Manager' and 'assigned_salesman' in data:
                salesman_value = data['assigned_salesman']
                if salesman_value and salesman_value != '' and salesman_value != 'null':
                    try:
                        salesman_id = int(salesman_value)
                        salesman = User.objects.get(
                            id=salesman_id,
                            role='Salesman',
                            branch=request.user.branch
                        )
                        listing.assigned_salesman = salesman
                    except (User.DoesNotExist, ValueError):
                        return JsonResponse({
                            'success': False,
                            'error': 'Invalid salesman selected.'
                        }, status=400)
                else:
                    listing.assigned_salesman = None
            
            # Update timestamp
            listing.updated_at = timezone.now()
            listing.save()
        
        # Return updated data
        return JsonResponse({
            'success': True,
            'message': 'Listing updated successfully.',
            'data': {
                'listing_id': listing.id,
                'title': listing.title,
                'price': f"₹{listing.proposed_price:,}" if listing.proposed_price else '—',
                'salesman': listing.assigned_salesman.get_full_name() if listing.assigned_salesman else '—',
                'status': listing.get_lead_status_display() if listing.lead_status else 
                         listing.get_opp_status_display() if listing.opp_status else
                         listing.get_sale_status_display() if listing.sale_status else '—'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)