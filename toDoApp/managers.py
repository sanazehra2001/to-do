from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Permission
from django.apps import apps

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """

        if not email:
            raise ValueError("The email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def _assign_permissions(self, user, permission_codenames):
        for codename in permission_codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                user.user_permissions.add(permission)
            except Permission.DoesNotExist:
                pass

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class EmployerManager(CustomUserManager):

    def create_user(self, email, password=None, **extra_fields):
        CustomUser = apps.get_model('toDoApp', 'CustomUser')
        extra_fields.setdefault('role', CustomUser.Role.EMPLOYER)
        return super().create_user(email, password, **extra_fields)

    def get_queryset(self, *args, **kwargs):
        CustomUser = apps.get_model('toDoApp', 'CustomUser')
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=CustomUser.Role.EMPLOYER)

class EmployeeManager(CustomUserManager):

    def create_user(self, email, password=None, **extra_fields):
        CustomUser = apps.get_model('toDoApp', 'CustomUser')
        extra_fields.setdefault('role', CustomUser.Role.EMPLOYEE)
        return super().create_user(email, password, **extra_fields)

    def get_queryset(self, *args, **kwargs):
        CustomUser = apps.get_model('toDoApp', 'CustomUser')
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=CustomUser.Role.EMPLOYEE)