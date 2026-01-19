from django import forms
from .models import Listing
from accounts.models import User

class SalesmanListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'type', 'address', 'city', 'proposed_price']

class ManagerListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'type', 'address', 'city', 'proposed_price', 'assigned_salesman']
    
    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)
        if manager and hasattr(manager, 'branch'):
            self.fields['assigned_salesman'].queryset = User.objects.filter(
                branch=manager.branch,
                role='Salesman'
            ).order_by('first_name', 'last_name')
