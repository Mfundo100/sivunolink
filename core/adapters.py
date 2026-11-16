from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
import uuid

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        # 1. Let allauth save the user first, but don't commit to DB yet
        user = super().save_user(request, sociallogin, form, commit=False)
        
        # 2. Check if the user already exists (e.g., linking account)
        User = get_user_model()
        if User.objects.filter(username=user.username).exists():
            existing_user = User.objects.get(username=user.username)
            # If the user exists, just return them (no need to change phone number)
            return existing_user

        # 3. Generate a unique placeholder phone number
        # Format: 7600 followed by a random 6-digit number
        unique_phone = f"7600{uuid.uuid4().hex[:6].upper()}"
        user.phone_number = unique_phone
        
        # 4. Ensure the user is marked as verified (optional, but useful)
        user.is_verified = True
        
        # 5. Save the user safely
        user.save()
        return user