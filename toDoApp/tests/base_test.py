from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import Permission, Group
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.apps import apps



User = get_user_model()
Employer = apps.get_model('toDoApp', 'Employer')
Employee = apps.get_model('toDoApp', 'Employee')

class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create groups
        self.employer_group = Group.objects.create(name='Employers')
        self.employee_group = Group.objects.create(name='Employees')

        # Create permissions (if needed)
        self.add_category_permission, created = Permission.objects.get_or_create(codename='add_category', name='Can add category')
        self.change_category_permission, created = Permission.objects.get_or_create(codename='change_category', name='Can change category')
        self.delete_category_permission, created = Permission.objects.get_or_create(codename='delete_category', name='Can delete category')
        self.view_category_permission, created = Permission.objects.get_or_create(codename='view_category', name='Can view category')

        self.add_task_permission, created = Permission.objects.get_or_create(codename='add_task', name='Can add task')
        self.change_task_permission, created = Permission.objects.get_or_create(codename='change_task', name='Can change task')
        self.delete_task_permission, created = Permission.objects.get_or_create(codename='delete_task', name='Can delete task')
        self.view_task_permission, created = Permission.objects.get_or_create(codename='view_task', name='Can view task')

        # Assign permissions to groups
        self.employer_group.permissions.add(
            self.add_category_permission, 
            self.change_category_permission, 
            self.delete_category_permission, 
            self.view_category_permission,
            self.add_task_permission,
            self.change_task_permission,
            self.delete_task_permission, 
            self.view_task_permission, 
        )
        
        self.employee_group.permissions.add(
            self.view_category_permission,
            self.view_task_permission, 
            self.change_task_permission,
        )

        # Create users with different roles
        self.admin = User.objects.create_superuser(email='admin@example.com', password='adminpassword')
        self.employer = Employer.objects.create_user(email='employer@example.com', password='employerpassword')
        self.employee = Employee.objects.create_user(email='employee@example.com', password='employeepassword')
