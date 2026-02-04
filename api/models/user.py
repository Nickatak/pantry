from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Custom user manager that uses email instead of username."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with email and password."""
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom User model without username, first_name, and last_name fields.

    Available Fields:
    - id (int): Primary key, auto-generated
    - email (str): Unique email address, used for authentication
    - password (str): Hashed password
    - is_active (bool): Whether the user account is active (default: True)
    - is_staff (bool): Whether the user can access the admin interface (default: False)
    - is_superuser (bool): Whether the user has all permissions (default: False)
    - date_joined (datetime): Timestamp when the user account was created
    - last_login (datetime): Timestamp of the last successful login (nullable)
    - groups (ManyToMany): Groups the user belongs to for permission management
    - user_permissions (ManyToMany): Specific permissions assigned to the user
    """

    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # Remove username, first_name, last_name from the model
    username = None
    first_name = None
    last_name = None

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email
