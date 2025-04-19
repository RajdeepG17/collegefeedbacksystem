from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.conf import settings

def get_cache_key(email):
    """Get cache key for login attempts."""
    return f'login_attempts_{email}'

def track_login_attempt(email, success):
    """
    Track login attempts for a given email.
    Raises ValidationError if too many failed attempts.
    """
    cache_key = get_cache_key(email)
    attempts = cache.get(cache_key, 0)

    if success:
        # Reset counter on successful login
        cache.delete(cache_key)
        return

    # Increment failed attempts
    attempts += 1
    timeout = getattr(settings, 'LOGIN_ATTEMPTS_TIMEOUT', 900)  # 15 minutes default
    max_attempts = getattr(settings, 'LOGIN_ATTEMPTS_LIMIT', 5)

    if attempts >= max_attempts:
        cache.set(cache_key, attempts, timeout)
        raise ValidationError(
            f'Too many failed login attempts. Please try again in {timeout//60} minutes.'
        )

    cache.set(cache_key, attempts, timeout)

def get_remaining_attempts(email):
    """Get remaining login attempts for a given email."""
    cache_key = get_cache_key(email)
    attempts = cache.get(cache_key, 0)
    max_attempts = getattr(settings, 'LOGIN_ATTEMPTS_LIMIT', 5)
    return max(0, max_attempts - attempts) 