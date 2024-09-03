from rest_framework import serializers
from toDoApp.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'role', 'auth_provider', 'date_joined')
