from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class SalesmanCreationForm(forms.ModelForm):
    """Form for managers to create new salesmen"""
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password for salesman',
            'required': True
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': True
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'manager', 'branch']
        widgets = {
            'role': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            'manager': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)
        
        # Set default values and make fields non-editable
        self.fields['role'].initial = User.Role.SALESMAN
        self.fields['role'].label = 'Role'
        self.fields['role'].widget.attrs.update({
            'readonly': True,
            'class': 'form-control',
            'value': 'Salesman'
        })
        
        if manager:
            self.fields['manager'].initial = manager
            self.fields['manager'].label = 'Manager'
            self.fields['manager'].widget.attrs.update({
                'readonly': True,
                'class': 'form-control',
                'value': manager.get_full_name()
            })
            
            self.fields['branch'].initial = manager.branch
            self.fields['branch'].label = 'Branch'
            self.fields['branch'].widget.attrs.update({
                'readonly': True,
                'class': 'form-control',
                'value': manager.branch.name if manager.branch else ''
            })
        
        # Add styling and validation to all visible fields
        for field_name in ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'required': True
            })
        
        # Set specific placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Enter username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter email address'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last name'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter password for salesman'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        # Validate required fields
        if not username:
            raise forms.ValidationError('Username is required.')
        if not email:
            raise forms.ValidationError('Email is required.')
        if not first_name:
            raise forms.ValidationError('First name is required.')
        if not last_name:
            raise forms.ValidationError('Last name is required.')
        if not password1:
            raise forms.ValidationError('Password is required.')
        if not password2:
            raise forms.ValidationError('Password confirmation is required.')
        
        # Check if email already exists
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        
        # Check if username already exists
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        
        # Check password match
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        
        # Ensure non-editable fields are properly set
        # These fields are readonly but should still be validated
        manager = self.fields['manager'].initial
        branch = self.fields['branch'].initial
        
        if not manager:
            raise forms.ValidationError('Manager information is required.')
        if not branch:
            raise forms.ValidationError('Branch information is required.')
        
        # Set the values explicitly to ensure they're saved correctly
        cleaned_data['role'] = User.Role.SALESMAN
        cleaned_data['manager'] = manager
        cleaned_data['branch'] = branch
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email already exists for another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is already in use.')
        return email