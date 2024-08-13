from django.urls import path
from .views import CategoryDetail, CategoryList, TaskDetail, TaskList

urlpatterns = [
    path('categories/', CategoryList.as_view(), name='category-list-create'),  # For GET and POST
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-retrieve-update-delete'),  # For GET, PUT, PATCH, DELETE

    path('tasks/', TaskList.as_view(), name='task-list-create'),  # For GET and POST
    path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-retrieve-update-delete'),  # For GET, PUT, PATCH, DELETE
]
