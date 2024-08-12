from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from toDoApp.models import CustomUser, Employee, Employer
import logging

@receiver(post_save, sender=Employee)
def assign_employee_to_group(sender, instance, created, **kwargs):
    logging.info(f"User created: {instance.email}, Role: {instance.role}")
    if created:
        if instance.role == CustomUser.Role.EMPLOYEE:
            group = Group.objects.get(name='Employees')
        
        instance.groups.add(group)


@receiver(post_save, sender=Employer)
def assign_employer_to_group(sender, instance, created, **kwargs):
    logging.info(f"User created: {instance.email}, Role: {instance.role}")
    if created:
        if instance.role == CustomUser.Role.EMPLOYER:
            group = Group.objects.get(name='Employers')
        
        instance.groups.add(group)