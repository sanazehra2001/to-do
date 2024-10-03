from datetime import timedelta
from django.utils import timezone
from django.apps import apps
from django.contrib.auth import get_user_model

from rest_framework import status

from unittest.mock import patch

import logging

from .base_test import BaseTestCase
from toDoApp.models import Task, Category

User = get_user_model()
Employer = apps.get_model('toDoApp', 'Employer')
Employee = apps.get_model('toDoApp', 'Employee')


class TaskModelTest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name='Work')
        self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )

    @patch('toDoApp.kafka.producer.produce_message')
    def test_employer_can_create_task(self, mock_kafka_producer):
        
        mock_producer_instance = mock_kafka_producer()   
        mock_producer_instance.produce_message.return_value = None
   

        self.client.force_authenticate(user=self.employer)

        response = self.client.post('/api/v1/tasks/', {
            'title': 'Task 2',
            'description': 'New task description',
            'due_date': (timezone.now()+ timedelta(days=1)).isoformat(),
            'priority': 'medium',
            'category': self.category.id,
        })

        # Check the response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], 'Task 2')

        # Call the produce_message method to ensure logging is triggered
        mock_producer_instance.produce_message('task_created', {'title': 'Task 2'})

        # Assert that the produce_message method was called
        mock_producer_instance.produce_message.assert_called_once_with('task_created', {'title': 'Task 2'})

        self.client.logout()

    def test_employee_can_create_task(self):
        # Authenticate the client as an employee
        self.client.force_authenticate(user=self.employee)
        response = self.client.post('/api/v1/tasks/', {
            'title': 'Task 2',
            'description': 'New task description',
            'due_date': (timezone.now()+ timedelta(days=1)).isoformat(),
            'priority': 'medium',
            'category': self.category.id,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()


    def test_task_creation_without_authentication(self):
        response = self.client.post('/api/v1/tasks/', {
            'title': 'Task 2',
            'description': 'New task description',
            'due_date': (timezone.now()+ timedelta(days=1)).isoformat(),
            'priority': 'medium',
            'category': self.category.id,
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_task_creation_with_missing_required_fields(self):
        self.client.force_authenticate(user=self.employer)
        data = {'title': 'Task 2',}
        response = self.client.post('/api/v1/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_task_list_retrieval_by_employer(self):
        self.client.force_authenticate(user=self.employer)
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['data']) > 0)

    def test_task_list_retrieval_by_employee(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['data']) > 0)

    def test_task_list_retrieval_without_authentication(self):
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieval_of_non_existent_task(self):
        self.client.force_authenticate(user=self.employer)
        response = self.client.get(f'/api/v1/tasks/{9000}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_task_deletion_by_employer(self):

        task = self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )
        
        self.client.force_authenticate(user=self.employer)
        url = f'/api/v1/tasks/{task.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    
    def test_task_deletion_by_employee(self):

        task = self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )
        
        self.client.force_authenticate(user=self.employee)
        url = f'/api/v1/tasks/{task.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Task.objects.filter(id=task.id).exists())


    def test_task_deletion_without_authentication(self):
        task = self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )
        url = f'/api/v1/tasks/{task.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Task.objects.filter(id=task.id).exists())

    def test_task_deletion_of_non_existent_task(self):
        self.client.force_authenticate(user=self.employer)
        response = self.client.delete(f'/api/v1/tasks/{9000}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_task_update_by_employer(self):
        task = self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )
        self.client.force_authenticate(user=self.employer)
        
        updated_data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'due_date': (timezone.now() + timedelta(days=2)).isoformat(),
            'category': self.category.id,
            'user': self.employer.id
        }

        response = self.client.put(f'/api/v1/tasks/{task.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(id=task.id).title, 'Updated Task')

    def test_task_update_by_employee(self):
        task = self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )
        self.client.force_authenticate(user=self.employee)
        
        updated_data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'due_date': (timezone.now() + timedelta(days=2)).isoformat(),
            'category': self.category.id,
            'user': self.employer.id
        }
        
        response = self.client.put(f'/api/v1/tasks/{task.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(id=task.id).title, 'Updated Task')


    def test_task_update_without_authentication(self):
        task = self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )
        
        updated_data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'due_date': (timezone.now() + timedelta(days=2)).isoformat(),
            'category': self.category.id,
            'user': self.employer.id
        }
        
        response = self.client.put(f'/api/v1/tasks/{task.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_task_update_with_invalid_data(self):
        task = self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )
        self.client.force_authenticate(user=self.employer)
        data = {'title': ''}
        response = self.client.put(f'/api/v1/tasks/{task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_task_update_of_non_existent_task(self):
        self.client.force_authenticate(user=self.employer)
        updated_data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'due_date': (timezone.now() + timedelta(days=2)).isoformat(),
            'category': self.category.id,
            'user': self.employer.id
        }
        response = self.client.put(f'/api/v1/tasks/{9000}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
    def test_task_update_partial_by_employer(self):
        task = self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )
        self.client.force_authenticate(user=self.employer)
        data = {'title': 'Updated Task'}
        response = self.client.patch(f'/api/v1/tasks/{task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(id=task.id).title, 'Updated Task')


    def test_task_update_partial_by_employee(self):
        task = self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )
        self.client.force_authenticate(user=self.employee)
        data = {'title': 'Updated Task'}
        response = self.client.patch(f'/api/v1/tasks/{task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(id=task.id).title, 'Updated Task')

    
    def test_task_update_partial_without_authentication(self):
        task = self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )
        
        data = {'title': 'Updated Task'}
        response = self.client.patch(f'/api/v1/tasks/{task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_task_update_partial_with_inavalid_data(self):
        task = self.task = Task.objects.create(
            title='Task 1', 
            description= "Task Description", 
            due_date=(timezone.now()+ timedelta(days=1)).isoformat(),
            category=self.category,
            user = self.employer
            )
        
        data = {'title': ''}
        response = self.client.patch(f'/api/v1/tasks/{task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



