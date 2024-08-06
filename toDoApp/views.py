from rest_framework import viewsets
from .models import Task, Category
from .serializers.category_serializer import CategorySerializer
from .serializers.task_serializer import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

