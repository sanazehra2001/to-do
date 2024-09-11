from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CategoryDetail, CategoryList, GoogleSignInView, TaskDetail, TaskList, google_login_view

urlpatterns = [
    path('categories/', CategoryList.as_view(), name='category-list-create'),  # For GET and POST
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-retrieve-update-delete'),  # For GET, PUT, PATCH, DELETE

    path('tasks/', TaskList.as_view(), name='task-list-create'),  # For GET and POST
    path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-retrieve-update-delete'),  # For GET, PUT, PATCH, DELETE

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('google/', GoogleSignInView.as_view(), name='google'),
    
    # for testing google-signin 
    path('google-login/', google_login_view, name='google_login'),
]
