from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator
import re

def validate_student_id(value):
    """Validate student ID format"""
    pattern = r'^[A-Z]{2}\d{6}$'  # Example: AB123456
    if not re.match(pattern, value):
        raise ValidationError(
            _('Student ID must be in the format: 2 letters followed by 6 numbers (e.g., AB123456)')
        )

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
        extra_fields.setdefault('user_type', 'superadmin')

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
    student_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_student_id],
        help_text="Format: 2 letters followed by 6 numbers (e.g., AB123456)"
    )
    department = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Profile information
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    address = models.TextField(blank=True, null=True)
    
    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_admin_for_category(self, category):
        """Check if user is admin for the given feedback category"""
        return self.user_type == 'admin' and self.admin_category == category

    def clean(self):
        """Validate user data"""
        # Student-specific validation
        if self.user_type == 'student':
            if not self.student_id:
                raise ValidationError({'student_id': 'Student ID is required for student accounts.'})
            if not self.department:
                raise ValidationError({'department': 'Department is required for student accounts.'})
            if not self.year_of_study:
                raise ValidationError({'year_of_study': 'Year of study is required for student accounts.'})
        
        # Admin-specific validation
        if self.user_type == 'admin':
            if self.admin_category == 'none':
                raise ValidationError({'admin_category': 'Admin category is required for admin accounts.'})