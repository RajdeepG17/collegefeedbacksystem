from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator, MinLengthValidator
from django.core.exceptions import ValidationError
import os
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import post_migrate
from django.dispatch import receiver

User = get_user_model()

def validate_file_type(value):
    """Validate that the uploaded file is of an allowed type"""
    ext = os.path.splitext(value.name)[1][1:].lower()
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt']
    if ext not in allowed_extensions:
        raise ValidationError(f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}')
    
    # Check file size (10MB limit)
    if value.size > 10 * 1024 * 1024:
        raise ValidationError('File size cannot exceed 10MB')

def validate_image_file(value):
    """Validate that the uploaded file is an image and meets size requirements"""
    # Check file extension
    ext = os.path.splitext(value.name)[1][1:].lower()
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
    if ext not in allowed_extensions:
        raise ValidationError(f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}')
    
    # Check file size (10MB limit)
    if value.size > 10 * 1024 * 1024:
        raise ValidationError('File size cannot exceed 10MB')

def feedback_attachment_path(instance, filename):
    """Generate path for feedback attachments"""
    ext = filename.split('.')[-1]
    filename = f"{instance.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return f'feedback_attachments/{instance.category.name}/{filename}'

def comment_attachment_path(instance, filename):
    """Generate path for comment attachments"""
    ext = filename.split('.')[-1]
    filename = f"{instance.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return f'comment_attachments/{instance.feedback.id}/{filename}'

class FeedbackCategory(models.Model):
    CATEGORY_CHOICES = (
        ('academic', 'Academic'),
        ('infrastructure', 'Infrastructure'),
        ('administrative', 'Administrative'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Feedback Category'
        verbose_name_plural = 'Feedback Categories'

    def __str__(self):
        return self.name

class FeedbackTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    feedbacks = models.ManyToManyField('Feedback', related_name='tags')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Feedback Tag'
        verbose_name_plural = 'Feedback Tags'

    def __str__(self):
        return self.name

class Feedback(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    title = models.CharField(max_length=200)
    content = models.TextField(default="No content provided")  # Add default value for 'content'
    category = models.ForeignKey(FeedbackCategory, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)  # Add default value for 'user'
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachment = models.FileField(upload_to='feedback_attachments/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'

    def __str__(self):
        return f"{self.title} - {self.user.email}"

class FeedbackResponse(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_internal = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='response_attachments/', null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Feedback Response'
        verbose_name_plural = 'Feedback Responses'

    def __str__(self):
        return f"Response to {self.feedback.title} by {self.responder.email}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('feedback_created', 'New Feedback'),
        ('feedback_updated', 'Feedback Updated'),
        ('feedback_status_changed', 'Status Changed'),
        ('feedback_assigned', 'Feedback Assigned'),
        ('feedback_comment', 'New Comment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.feedback.title}"

class FeedbackComment(models.Model):
    """Model to store comments on feedback"""
    
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_comments', null=True, blank=True)
    comment = models.TextField(validators=[MinLengthValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachment = models.ImageField(
        upload_to=comment_attachment_path,
        blank=True,
        null=True,
        validators=[validate_image_file]
    )
    is_internal = models.BooleanField(default=False, help_text="Visible only to admins")
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['feedback', 'created_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.feedback.title}"

class FeedbackHistory(models.Model):
    """Model to track feedback status changes"""
    
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, default='pending')
    old_assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='old_assignments',
        blank=True, 
        null=True
    )
    new_assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='new_assignments',
        blank=True, 
        null=True
    )
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Feedback Histories"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Status change on {self.feedback.title} by {self.changed_by.email}"

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    """
    Create default feedback categories after migration if they don't exist.
    """
    if sender.name == 'feedback':
        from feedback.models import FeedbackCategory
        
        # Define default categories
        default_categories = [
            {'name': 'Academic', 'description': 'Feedback related to academic matters', 'icon': 'school'},
            {'name': 'Infrastructure', 'description': 'Feedback related to infrastructure', 'icon': 'building'},
            {'name': 'Administrative', 'description': 'Feedback related to administrative matters', 'icon': 'admin_panel_settings'},
            {'name': 'Other', 'description': 'Other types of feedback', 'icon': 'more_horiz'}
        ]
        
        # Create categories if they don't exist
        for category_data in default_categories:
            FeedbackCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon'],
                    'active': True
                }
            )