import time
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('college_feedback_system')

# Constants for login tracking
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 15 * 60  # 15 minutes in seconds

def get_cache_key(email):
    """Generate a cache key for tracking login attempts"""
    return f'login_attempts_{email.lower()}'

def track_login_attempt(email, success=False):
    """
    Track login attempts for a user.
    If success is True, reset the counter.
    If success is False, increment the counter.
    """
    cache_key = get_cache_key(email)
    
    if success:
        # Reset counter on successful login
        cache.delete(cache_key)
        logger.info(f"Successful login: {email}")
        return True
    
    # Get current attempts
    attempts = cache.get(cache_key, {'count': 0, 'last_attempt': None})
    
    # Update attempts
    current_time = int(time.time())
    attempts['count'] += 1
    attempts['last_attempt'] = current_time
    
    # Set expiry time - default to 15 minutes
    cache.set(cache_key, attempts, LOCKOUT_TIME)
    
    logger.warning(f"Failed login attempt: {email} (Attempt {attempts['count']})")
    return attempts

def get_remaining_attempts(email):
    """Get remaining login attempts before lockout"""
    cache_key = get_cache_key(email)
    attempts = cache.get(cache_key, {'count': 0, 'last_attempt': None})
    
    if attempts['count'] >= MAX_LOGIN_ATTEMPTS:
        # Calculate when the lockout expires
        if attempts['last_attempt']:
            lockout_expires = attempts['last_attempt'] + LOCKOUT_TIME
            current_time = int(time.time())
            if current_time < lockout_expires:
                return 0
        
        # Reset if lockout has expired
        cache.delete(cache_key)
        return MAX_LOGIN_ATTEMPTS
    
    return MAX_LOGIN_ATTEMPTS - attempts['count'] 