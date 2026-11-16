from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
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


# NEW: Custom Form to handle Suspended Accounts
class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                "Your account has been suspended by the SivunoLink Administration. Please contact support for assistance.",
                code='inactive',
            )
        super().confirm_login_allowed(user)