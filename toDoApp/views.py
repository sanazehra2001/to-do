from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Task, Category, CustomUser
from .serializers.category_serializer import CategorySerializer
from .serializers.task_serializer import TaskSerializer



class BaseAPIView(APIView):
   
    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        """
        Return a success response with the given data and message.
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data
        }
        return Response(response_data, status=status_code)
    
    def bad_request_response(self, errors=None, message="Bad Request", status_code=status.HTTP_400_BAD_REQUEST):
        """
        Return a bad request response with the given errors and message.
        """
        response_data = {
            "success": False,
            "message": message,
            "errors": errors
        }
        return Response(response_data, status=status_code)


class TaskViewSet(BaseAPIView, viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    # authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return self.success_response(data=response.data, message="Task created successfully.")
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to create task.")

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            return self.success_response(data=response.data, message="Tasks retrieved successfully.")
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to retrieve tasks.")

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return self.success_response(data=response.data, message="Task updated successfully.")
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to update task.")

    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            return self.success_response(message="Task deleted successfully.")
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to delete task.")


class CategoryViewSet(BaseAPIView, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return self.success_response(data=response.data, message="Category created successfully.")
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to create category.")

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            return self.success_response(data=response.data, message="Categories retrieved successfully.")
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to retrieve categories.")

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return self.success_response(data=response.data, message="Category updated successfully.")
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to update category.")

    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            return self.success_response(message="Category deleted successfully.")
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to delete category.")
