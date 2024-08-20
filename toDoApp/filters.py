from django_filters import rest_framework as filters
from .models import Category, Task

class CategoryFilter(filters.FilterSet):

    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['name']
            
            

class TaskFilter(filters.FilterSet):

    title = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    due_date_gt = filters.DateFilter(field_name='due_date', lookup_expr='gt', label='Due Date Greater Than')
    due_date_lt = filters.DateFilter(field_name='due_date', lookup_expr='lt', label='Due Date Less Than')
    is_completed = filters.BooleanFilter()
    priority = filters.ChoiceFilter(choices=Task.PRIORITY_CHOICES)

    class Meta:
        model = Task
        fields = [
            'title', 
            'description',
            'due_date',
            'is_completed',
            'priority',
            'category',
        ]