from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class BuyerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'BUYER' # Automatically assign the BUYER role
        if commit:
            user.save()
        return user