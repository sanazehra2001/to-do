from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

    def validate_name(self, value):
        """
        Validate that the category name is not empty and is unique.
        """
        if not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return value
