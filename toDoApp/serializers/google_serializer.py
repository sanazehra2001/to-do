from os import access
from rest_framework import serializers
from toDoApp.utils import Google, register_social_user
from toDoApp.models import CustomUser
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField(min_length=6)

    def validate(self, data):
        id_token = data.get('id_token')
        if not id_token:
            raise serializers.ValidationError('id_token is required.')
        
        user_data = Google.validate(id_token)

        if not user_data:
            raise serializers.ValidationError('Invalid token.')
        
        try:
            user_id = user_data['sub']
        except KeyError:
            raise serializers.ValidationError('This token is invalid or has expired.')

        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed('Could not verify user.')

        email = user_data.get('email')
        if not email:
            raise serializers.ValidationError('Email not found in token.')

        provider = 'google'
        return register_social_user(provider, email, CustomUser.Role.EMPLOYER)
