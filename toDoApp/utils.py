from google.auth.transport import requests
from google.oauth2 import id_token
from .models import CustomUser
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

from .serializers.user_serializer import CustomUserSerializer


class Google():
    @staticmethod
    def validate(received_token):
        try:
            id_info = id_token.verify_oauth2_token(str(received_token), requests.Request())
            
            if "accounts.google.com" in id_info['iss']:
                return id_info

        except Exception as e:
            print("Error during token validation:", str(e))
            raise AuthenticationFailed('Token is either invalid or has expired.')
        



def register_social_user(provider, email, role):
    # Define a default password for new users
    password = settings.SOCIAL_AUTH_PASSWORD
    # Create or update the user
    user, created = CustomUser.objects.get_or_create(
        email=email, 
        defaults={
            'password': make_password(password),
            'role': role,
            'auth_provider': provider
        }
    )

    if created:
        user.set_password(password)
        user.save()


    # Generate tokens
    tokens = get_tokens_for_user(user)

    # Serialize user data
    serializer = CustomUserSerializer(user)

    return {
        'user': serializer.data,
        'tokens': tokens
    }



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
