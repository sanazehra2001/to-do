from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import DjangoModelPermissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from django.shortcuts import render
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend

from toDoApp.filters import CategoryFilter, TaskFilter
from toDoApp.serializers.google_serializer import GoogleLoginSerializer

from .models import Task, Category
from toDoApp.kafka.producer import produce_message
from .serializers.category_serializer import CategorySerializer
from .serializers.task_serializer import TaskSerializer



class BaseAPIView(GenericAPIView):
   
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


class TaskList(BaseAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [DjangoModelPermissions]

    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    pagination_class = PageNumberPagination 

    serializer_class = TaskSerializer   
    queryset = Task.objects.all().order_by('due_date')  

    @extend_schema(
            operation_id="get_all_tasks",
            parameters=[
            OpenApiParameter(name='title', description='Title of the Task', required=False, type=str),
            OpenApiParameter(name='description', description='Task Description', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='due_date_gt', description='Due Date Greater Than', required=False, type=OpenApiTypes.DATE),
            OpenApiParameter(name='due_date_lt', description='Due Date Less Than', required=False, type=OpenApiTypes.DATE),
            OpenApiParameter(name='is_completed', description='Status', required=False, type=OpenApiTypes.BOOL),
            OpenApiParameter(name='priority', description='Priority', required=False, type=OpenApiTypes.STR, enum=[choice[0] for choice in Task.PRIORITY_CHOICES]),
            OpenApiParameter(name='category', description='Category', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='page', description='Page Number', required=False, type=OpenApiTypes.INT),
        ]
            )
    def get(self, request, *args, **kwargs):
        try:
            tasks = self.filter_queryset(self.queryset)
            page_tasks = self.paginate_queryset(tasks)
            serializer = TaskSerializer(page_tasks, many=True)
            return self.success_response(data=self.get_paginated_response(serializer.data).data, message="Tasks retrieved successfully.")
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to retrieve tasks.")

    @extend_schema(operation_id="create_task")
    def post(self, request, *args, **kwargs):
        try:
            serializer = TaskSerializer(data=request.data, context = {'request':request})
            if serializer.is_valid():
                task = serializer.save(user=request.user)

                produce_message('task_topic', {'task_data': serializer.data, 'user_data': request.user})

                return self.success_response(data=serializer.data, message="Task created successfully.")
            return self.bad_request_response(errors=serializer.errors, message="Failed to create task.")
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to create task.")
        

class TaskDetail(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [DjangoModelPermissions]
    
    serializer_class = TaskSerializer   
    queryset = Task.objects.all()  

    @extend_schema(operation_id="retrieve_task")
    def get(self, request, pk, *args, **kwargs):
        """
        Handle GET requests for retrieving a single task.
        """
        try:
            task = self.queryset.get(pk=pk)
            serializer = self.serializer_class(task)
            return self.success_response(data=serializer.data, message="Task retrieved successfully.")
        except Task.DoesNotExist:
            return self.bad_request_response(message="Task not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to retrieve task.")
        

    @extend_schema(operation_id="update_task")
    def put(self, request, pk, *args, **kwargs):
        try:
            task = self.queryset.get(pk=pk)
            serializer = self.serializer_class(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(data=serializer.data, message="Task updated successfully.")
            return self.bad_request_response(errors=serializer.errors, message="Failed to update task.")
        except Task.DoesNotExist:
            return self.bad_request_response(message="Task not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to update task.")
        
    @extend_schema(operation_id="update_task_partial")
    def patch(self, request, pk, *args, **kwargs):
        """
        Handle PATCH requests for partially updating an existing task.
        """
        try:
            task = self.queryset.get(pk=pk)
            serializer = self.serializer_class(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(data=serializer.data, message="Task updated successfully.")
            return self.bad_request_response(errors=serializer.errors, message="Failed to update task.")
        except Task.DoesNotExist:
            return self.bad_request_response(message="Task not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to update task.")

    @extend_schema(operation_id="delete_task")
    def delete(self, request, pk, *args, **kwargs):
        try:
            task = self.queryset.get(pk=pk)
            task.delete()
            return self.success_response(message="Task deleted successfully.")
        except Task.DoesNotExist:
            return self.bad_request_response(message="Task not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to delete task.")



class CategoryList(BaseAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [DjangoModelPermissions]
    
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter

    pagination_class = PageNumberPagination 

    serializer_class = CategorySerializer   
    queryset = Category.objects.all()  


    def get_cache_key(self):
        return 'all_categories'

    @extend_schema(operation_id="get_all_categories", 
        parameters=[
            OpenApiParameter(name='name', description='Category Name', required=False, type=str),
            OpenApiParameter(name='page', description='Page Number', required=False, type=OpenApiTypes.INT),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for listing categories.
        """
        cache_key = self.get_cache_key()
        cached_data = cache.get(cache_key)

        if cached_data:
            return self.success_response(data=cached_data, message="Categories retrieved successfully.")

        try:
            categories = self.filter_queryset(self.queryset)
            page_categories = self.paginate_queryset(categories)
            serializer = self.serializer_class(page_categories, many=True)

            data = self.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, 60 * 15)

            return self.success_response(data=data, message="Categories retrieved successfully.")
        
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to retrieve categories.")

    @extend_schema(operation_id="create_category")
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for creating a new category.
        """
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                cache.delete(self.get_cache_key())
                return self.success_response(data=serializer.data, message="Category created successfully.")
            return self.bad_request_response(errors=serializer.errors, message="Failed to create category.")
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to create category.")



class CategoryDetail(BaseAPIView):

    """
    Retrieve, update or delete a category.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [DjangoModelPermissions]
    serializer_class = CategorySerializer     
    queryset = Category.objects.all()  

    @extend_schema(operation_id="retrieve_category")
    def get(self, request, pk, *args, **kwargs):
        """
        Handle GET requests for retrieving a single category.
        """
        try:
            category = self.queryset.get(pk=pk)
            serializer = self.serializer_class(category)
            return self.success_response(data=serializer.data, message="Category retrieved successfully.")
        except Category.DoesNotExist:
            return self.bad_request_response(message="Category not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to retrieve category.")

    @extend_schema(operation_id="update_category")
    def put(self, request, pk, *args, **kwargs):
        """
        Handle PUT requests for updating an existing category.
        """
        try:
            category = self.queryset.get(pk=pk)
            serializer = self.serializer_class(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(data=serializer.data, message="Category updated successfully.")
            return self.bad_request_response(errors=serializer.errors, message="Failed to update category.")
        except Category.DoesNotExist:
            return self.bad_request_response(message="Category not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to update category.")

    @extend_schema(operation_id="update_category_partial") 
    def patch(self, request, pk, *args, **kwargs):
        """
        Handle PATCH requests for partially updating an existing category.
        """
        try:
            category = self.queryset.get(pk=pk)
            serializer = self.serializer_class(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(data=serializer.data, message="Category updated successfully.")
            return self.bad_request_response(errors=serializer.errors, message="Failed to update category.")
        except Category.DoesNotExist:
            return self.bad_request_response(message="Category not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to update category.")
        

    @extend_schema(operation_id="delete_category")
    def delete(self, request, pk, *args, **kwargs):
        """
        Handle DELETE requests for deleting a category.
        """
        try:
            category = self.queryset.get(pk=pk)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return self.bad_request_response(message="Category not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.bad_request_response(errors=str(e), message="Failed to delete category.")
        

class GoogleSignInView(BaseAPIView):
    serializer_class = GoogleLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            print("Request:")
            print(request.data)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            validated_data = serializer.validated_data
            tokens = validated_data.get('tokens')
            print("Tokens")
            print(tokens)
            
            return self.success_response(data=tokens, message="User successfully logged in using Google")
        except serializers.ValidationError as e:
            return self.bad_request_response(errors=str(e), message="Google authentication failed.")
        except Exception as e:
            import traceback
            print("Exception:", traceback.format_exc())
            return self.bad_request_response(errors=str(e), message="Google authentication failed.")

# For testing google signin

def google_login_view(request):
    return render(request, 'index.html')

