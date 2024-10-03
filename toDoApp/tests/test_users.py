
from .base_test import BaseTestCase
from django.apps import apps
from django.contrib.auth import get_user_model

User = get_user_model()
Employer = apps.get_model('toDoApp', 'Employer')
Employee = apps.get_model('toDoApp', 'Employee')


class UserModelTest(BaseTestCase):

    def setUp(self):
        super().setUp()

    def test_admin_creation(self):
        # Test that the admin user is created with correct attributes
        self.assertEqual(self.admin.email, 'admin@example.com')
        self.assertTrue(self.admin.is_superuser)
        self.assertTrue(self.admin.is_staff)

    def test_employer_creation(self):
        # Test that the employer user is created with correct attributes
        self.assertEqual(self.employer.role, User.Role.EMPLOYER)
        self.assertFalse(self.employer.is_superuser)

    def test_employee_creation(self):
        # Test that the employee user is created with correct attributes
        self.assertEqual(self.employee.role, User.Role.EMPLOYEE)
        self.assertFalse(self.employee.is_superuser)

    def test_employer_manager(self):
        # Test that the EmployerManager filters correctly
        self.assertTrue(Employer.objects.filter(email='employer@example.com').exists())
        self.assertFalse(Employer.objects.filter(email='employee@example.com').exists())

    def test_employee_manager(self):
        # Test that the EmployeeManager filters correctly
        self.assertTrue(Employee.objects.filter(email='employee@example.com').exists())
        self.assertFalse(Employee.objects.filter(email='employer@example.com').exists())

    def test_employer_permissions(self):
        # Test that the employer has all the permissions assigned to the employer group
        self.assertTrue(self.employer.has_perm('toDoApp.add_category'))
        self.assertTrue(self.employer.has_perm('toDoApp.change_category'))
        self.assertTrue(self.employer.has_perm('toDoApp.delete_category'))
        self.assertTrue(self.employer.has_perm('toDoApp.view_category'))
        self.assertTrue(self.employer.has_perm('toDoApp.add_task'))
        self.assertTrue(self.employer.has_perm('toDoApp.change_task'))
        self.assertTrue(self.employer.has_perm('toDoApp.delete_task'))
        self.assertTrue(self.employer.has_perm('toDoApp.view_task'))

    def test_employee_permissions(self):
        # Test that the employee has only the permissions assigned to the employee group
        self.assertFalse(self.employee.has_perm('toDoApp.add_category'))
        self.assertFalse(self.employee.has_perm('toDoApp.change_category'))
        self.assertFalse(self.employee.has_perm('toDoApp.delete_category'))
        self.assertTrue(self.employee.has_perm('toDoApp.view_category'))

        self.assertFalse(self.employee.has_perm('toDoApp.add_task'))
        self.assertTrue(self.employee.has_perm('toDoApp.change_task'))
        self.assertFalse(self.employee.has_perm('toDoApp.delete_task'))
        self.assertTrue(self.employee.has_perm('toDoApp.view_task'))