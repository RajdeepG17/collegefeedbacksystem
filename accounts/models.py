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
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # Set username to email for compatibility with default auth
        extra_fields['username'] = email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )

    username = models.CharField(_('username'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    student_id = models.CharField(max_length=8, validators=[validate_student_id], blank=True, null=True)
    year_of_study = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    admin_category = models.CharField(max_length=20, choices=(
        ('academic', 'Academic'),
        ('infrastructure', 'Infrastructure'),
        ('administrative', 'Administrative'),
        ('other', 'Other'),
        ('none', 'None'),
    ), default='none')
    is_staff_member = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

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