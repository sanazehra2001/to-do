from django.db import transaction
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import Group, Permission

import logging

from toDoApp.models import CustomUser, Employee, Employer, Category


@receiver(post_save, sender=Employee)
def assign_employee_to_group(sender, instance, created, **kwargs):
    
    if created:
        try: 
            with transaction.atomic():
                if instance.role == CustomUser.Role.EMPLOYEE:
                    group, created = Group.objects.get_or_create(name='Employees')

                    if created:
                        permissions = [
                            'change_task', 'delete_task', 'view_task',
                            'view_category'
                        ]
                        add_permissions_to_group(group, permissions)
                
                instance.groups.add(group)
                logging.info(f"User created: {instance.email}, Role: {instance.role}")
        except Exception as e:
            logging.error(f"Error adding user to group: {e}")
            instance.delete()


@receiver(post_save, sender=Employer)
def assign_employer_to_group(sender, instance, created, **kwargs):
    
    if created:
        try: 
            with transaction.atomic():
                if instance.role == CustomUser.Role.EMPLOYER:
                    group, created = Group.objects.get_or_create(name='Employers')

                    if created:
                        permissions = [
                            'add_task', 'change_task', 'delete_task', 'view_task',
                            'add_category', 'change_category', 'delete_category', 'view_category'
                        ]
                        add_permissions_to_group(group, permissions)
                
                instance.groups.add(group)
                logging.info(f"User created: {instance.email}, Role: {instance.role}")

        except Exception as e:
            logging.error(f"Error adding user to group: {e}")
            instance.delete()


@receiver(post_delete, sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    """
    Invalidate the cache when a Category instance is saved.
    """
    cache_key = 'all_categories'
    cache.delete(cache_key)


def add_permissions_to_group(group, permissions):
    """
    Add a list of permissions to the given group.
    """
    for codename in permissions:
        try:
            permission = Permission.objects.get(codename=codename)
            group.permissions.add(permission)
        except Permission.DoesNotExist:
            logging.warning(f"Permission '{codename}' does not exist.")