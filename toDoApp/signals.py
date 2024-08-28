from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from toDoApp.models import CustomUser, Employee, Employer
import logging
from django.db import transaction

@receiver(post_save, sender=Employee)
def assign_employee_to_group(sender, instance, created, **kwargs):
    
    if created:
        try: 
            with transaction.atomic():
                if instance.role == CustomUser.Role.EMPLOYEE:
                    group, created = Group.objects.get_or_create(name='Employees')
                
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
                
                instance.groups.add(group)
                logging.info(f"User created: {instance.email}, Role: {instance.role}")

        except Exception as e:
            logging.error(f"Error adding user to group: {e}")
            instance.delete()
