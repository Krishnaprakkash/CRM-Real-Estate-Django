def listing_visiible_to(user):
    from .models import Listing
    qs = Listing.objects.filter(is_active=True).select_related('branch', 'created_by', 'assigned_to')

    if user.groups.filter(name='CEO').exists():
        return qs
    elif user.groups.filter(name='Manager').exists():
        return qs.filter(branch=user.branch)
    else:
        return qs.filter(assigned_to=user)