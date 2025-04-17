from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Custom User model with email as the unique identifier."""
    
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
    )

    ADMIN_CATEGORY_CHOICES = (
        ('academic', 'Academic'),
        ('infrastructure', 'Infrastructure'),
        ('administrative', 'Administrative'),
        ('other', 'Other'),
        ('none', 'None'),
    )
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    admin_category = models.CharField(
        max_length=20, 
        choices=ADMIN_CATEGORY_CHOICES, 
        default='none',
        help_text="Category of feedback this admin manages (only applicable for admin users)"
    )
    
    # Additional fields for students
    student_id = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.PositiveSmallIntegerField(blank=True, null=True)
    
    # Profile information
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def _str_(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_admin_for_category(self, category):
        """Check if user is admin for the given feedback category"""
        return self.user_type == 'admin' and self.admin_category == category