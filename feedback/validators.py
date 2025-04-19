from django.core.exceptions import ValidationError
from django.conf import settings
import os

def validate_file_size(value):
    """Validate file size is under 5MB"""
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(f'File size should not exceed 5MB.')

def validate_file_type(value):
    """Validate file type is allowed"""
    ext = os.path.splitext(value.name)[1][1:].lower()
    if ext not in settings.ALLOWED_FILE_TYPES:
        raise ValidationError(f'File type not allowed. Allowed types: {", ".join(settings.ALLOWED_FILE_TYPES)}') 