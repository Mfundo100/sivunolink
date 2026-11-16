from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
import uuid

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If the user is already logged in, skip
        if request.user.is_authenticated:
            return
        
        email = sociallogin.account.extra_data.get('email')
        if email:
            User = get_user_model()
            # Use filter().first() instead of get() to avoid MultipleObjectsReturned crashes
            user = User.objects.filter(email=email).first()
            if user:
                # Connect the Google account to the existing user
                sociallogin.connect(request, user)

    def save_user(self, request, sociallogin, form=None):
        # Let allauth create the user object
        user = super().save_user(request, sociallogin, form, commit=False)
        
        # Generate a unique phone number if missing
        if not user.phone_number:
            user.phone_number = f"76{uuid.uuid4().hex[:8].upper()}"
            
        # Generate a unique username if missing (Google doesn't provide usernames)
        if not user.username:
            user.username = f"user_{uuid.uuid4().hex[:6]}"
            
        user.is_verified = True
        user.save()
        return user