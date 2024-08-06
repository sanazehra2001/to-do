from rest_framework import serializers
from .models import Task, Category
from datetime import datetime

class TaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'is_completed', 'priority', 'category']

    def validate_title(self, value):
        """
        Validate that the task title is not empty and has a minimum length.
        """
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        return value

    def validate_due_date(self, value):
        """
        Validate that the due date is not in the past.
        """
        if value and value < datetime.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate_priority(self, value):
        """
        Validate that the priority is one of the allowed choices.
        """
        if value not in ['low', 'medium', 'high']:
            raise serializers.ValidationError("Priority must be 'low', 'medium', or 'high'.")
        return value

    def validate_category(self, data):
        """
        Validate that the category exists and is valid.
        """
        category_data = data.get('category')
        if category_data:
            category_name = category_data.get('name')
            if not Category.objects.filter(name=category_name).exists():
                raise serializers.ValidationError("Category does not exist.")
        return data