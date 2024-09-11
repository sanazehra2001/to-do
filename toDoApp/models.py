from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils import timezone
from .managers import CustomUserManager, EmployeeManager, EmployerManager
from django.conf import settings
import uuid


AUTH_PROVIDERS = {
    'email':'email',
    'google':'google',
    'github':'github',
    'facebook':'facebook',
    'twitter':'twitter',
}

class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        EMPLOYER = "EMPLOYER", 'Employer'
        EMPLOYEE = "EMPLOYEE", 'Employee'

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADMIN)
    email = models.EmailField(
        unique=True, 
        error_messages={'unique': "A user with that email already exists."}
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    auth_provider = models.CharField(
        max_length=50,
        default=AUTH_PROVIDERS.get('email')
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name='custom_user_set'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name='custom_user_set'
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.email



class Employer(CustomUser):
    base_role = CustomUser.Role.EMPLOYER
    objects = EmployerManager()

    class Meta:
        proxy = True

class Employee(CustomUser):
    base_role = CustomUser.Role.EMPLOYEE
    objects = EmployeeManager()

    class Meta:
        proxy = True


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.ForeignKey(Category, related_name='tasks', on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="tasks", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

