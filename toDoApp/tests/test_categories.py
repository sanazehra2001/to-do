from rest_framework import status
from toDoApp.tests.base_test import BaseTestCase
from django.apps import apps
from django.contrib.auth import get_user_model

from toDoApp.models import Category

User = get_user_model()
Employer = apps.get_model('toDoApp', 'Employer')
Employee = apps.get_model('toDoApp', 'Employee')

class CategoryModelTest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name='Work')

    def test_employer_can_create_category(self):
        # Authenticate the client as an employer
        self.client.force_authenticate(user=self.employer)
        response = self.client.post('/api/v1/categories/', {'name': 'Personal'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Personal')
        self.client.logout()

    def test_employee_cannot_create_category(self):
        # Authenticate the client as an employee
        self.client.force_authenticate(user=self.employee)
        response = self.client.post('/api/v1/categories/', {'name': 'Personal'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 
        self.client.logout()

    def test_category_creation_without_authentication(self):
        response = self.client.post('/api/v1/categories/', {'name': 'Personal'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  

    def test_category_creation_with_missing_required_fields(self):
        self.client.force_authenticate(user=self.employer)
        data = {}
        response = self.client.post('/api/v1/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_category_list_retrieval_by_employer(self):
        self.client.force_authenticate(user=self.employer)
        response = self.client.get('/api/v1/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['data']) > 0) 

    def test_category_list_retrieval_by_employee(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.get('/api/v1/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['data']) > 0) 

    def test_category_list_retrieval_without_authentication(self):
        response = self.client.get('/api/v1/categories/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieval_of_non_existent_category(self):
        self.client.force_authenticate(user=self.employer)
        response = self.client.get(f'/api/v1/categories/{9000}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_category_deletion_by_employer(self):
        category = Category.objects.create(name='Test Category')
        self.client.force_authenticate(user=self.employer)
        url = f'/api/v1/categories/{category.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_category_deletion_by_employee(self):
        category = Category.objects.create(name='Test Category')
        self.client.force_authenticate(user=self.employee)
        url = f'/api/v1/categories/{category.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Category.objects.filter(id=category.id).exists())

    def test_category_deletion_without_authentication(self):
        category = Category.objects.create(name='Test Category')
        url = f'/api/v1/categories/{category.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Category.objects.filter(id=category.id).exists())

    def test_category_deletion_of_non_existent_category(self):
        self.client.force_authenticate(user=self.employer)
        response = self.client.delete(f'/api/v1/categories/{9000}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_category_update_by_employer(self):
        category = Category.objects.create(name='Test Category')
        self.client.force_authenticate(user=self.employer)
        data = {'name': 'Updated Category'}
        response = self.client.put(f'/api/v1/categories/{category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Category.objects.get(id=category.id).name, 'Updated Category')

    def test_category_update_by_employee(self):
        category = Category.objects.create(name='Test Category')
        self.client.force_authenticate(user=self.employee)
        data = {'name': 'Updated Category'}
        response = self.client.put(f'/api/v1/categories/{category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_update_without_authentication(self):
        category = Category.objects.create(name='Test Category')
        url = f'/api/v1/categories/{category.id}/'
        data = {'name': 'Updated Category'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_category_update_with_invalid_data(self):
        category = Category.objects.create(name='Test Category')
        self.client.force_authenticate(user=self.employer)
        data = {'name': ''}
        response = self.client.put(f'/api/v1/categories/{category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_category_update_of_non_existent_category(self):
        self.client.force_authenticate(user=self.employer)
        data = {'name': 'Updated Category'}
        response = self.client.put(f'/api/v1/categories/{9000}/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
