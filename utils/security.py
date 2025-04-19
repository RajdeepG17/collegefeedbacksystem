import re
import logging
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

logger = logging.getLogger(__name__)

def validate_password_strength(password):
    """
    Validate that the password meets minimum security requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    """
    if len(password) < 8:
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[a-z]', password):
        return False
    
    if not re.search(r'\d', password):
        return False
    
    return True

def sanitize_input(data):
    """Basic input sanitization"""
    if isinstance(data, str):
        # Remove any potential script tags
        data = re.sub(r'<script.*?>.*?</script>', '', data, flags=re.IGNORECASE | re.DOTALL)
        # Remove any potential HTML tags
        data = re.sub(r'<.*?>', '', data)
        return data.strip()
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(x) for x in data]
    return data

def validate_file_upload(file, allowed_types=None, max_size=None):
    """
    Validate file uploads.
    """
    if not file:
        return False

    if max_size is None:
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 5 * 1024 * 1024)  # 5MB default

    if allowed_types is None:
        allowed_types = getattr(settings, 'ALLOWED_FILE_TYPES', ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])

    # Check file size
    if file.size > max_size:
        raise ValidationError(f'File size must not exceed {max_size/1024/1024}MB')

    # Check file type
    file_extension = file.name.split('.')[-1].lower()
    if file_extension not in allowed_types:
        raise ValidationError(f'File type not allowed. Allowed types: {", ".join(allowed_types)}')

    return True

def log_security_event(event_type, data):
    """Log security-related events"""
    logger.info(
        f"security_{event_type}",
        **data
    )

def generate_password_reset_token(user):
    """
    Generate password reset token for a user.
    Returns uid and token.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token

def send_password_reset_email(user, reset_url):
    """
    Send password reset email to user.
    """
    try:
        subject = 'Password Reset Request'
        message = f'Click the link to reset your password: {reset_url}'
        user.email_user(subject, message)
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        return False

def validate_reset_token(user, token):
    """
    Validate password reset token.
    Returns True if token is valid, False otherwise.
    """
    try:
        return default_token_generator.check_token(user, token)
    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        return False 