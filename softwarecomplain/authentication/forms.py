from django import forms
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(
    widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Your Password',
        'data-toggle': 'password',  # For show/hide password functionality
        'id': 'id_password'  # For JavaScript targeting
    }),
    help_text="Your password must contain at least 8 characters.",
    min_length=8
    )

    class Meta:
        model = CustomUser
        fields = ['name', 'organization', 'email', 'phone', 'password']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Your Name'}),
            'organization': forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Your Organization Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control','placeholder':'Enter Your Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Your Phone Number'}),
        }

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )