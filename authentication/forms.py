from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(forms.Form):
    """Simple login form with email and password"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    ) 