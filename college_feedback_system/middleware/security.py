import re
import time
import logging
from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

logger = logging.getLogger('college_feedback_system')

class BasicSecurityMiddleware(MiddlewareMixin):
    """
    Basic security middleware for the college feedback system.
    Implements:
    - Basic XSS protection
    - Rate limiting for API requests
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'API_RATE_LIMIT', 60)  # requests per minute
        self.rate_limit_window = 60  # seconds
        
    def process_request(self, request):
        """
        Process the incoming request.
        - Sanitize input
        - Check rate limiting
        """
        # Skip middleware for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None
            
        # Rate limiting for API requests
        if request.path.startswith('/api/'):
            ip = self.get_client_ip(request)
            if not self.check_rate_limit(ip):
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                return HttpResponseForbidden("Rate limit exceeded. Try again later.")
        
        return None
        
    def process_response(self, request, response):
        """
        Process the outgoing response.
        Add security headers to the response.
        """
        # Add basic security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        
        return response
        
    def get_client_ip(self, request):
        """Get the client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
        
    def check_rate_limit(self, ip):
        """
        Check if the IP has exceeded rate limits.
        Return True if request is allowed, False otherwise.
        """
        cache_key = f"rate_limit:{ip}"
        history = cache.get(cache_key)
        
        now = time.time()
        
        if history is None:
            # First request from this IP
            new_history = [now]
            cache.set(cache_key, new_history, self.rate_limit_window * 2)
            return True
            
        # Filter out requests older than the window
        updated_history = [timestamp for timestamp in history if now - timestamp < self.rate_limit_window]
        
        # Add current request
        updated_history.append(now)
        
        # Update cache
        cache.set(cache_key, updated_history, self.rate_limit_window * 2)
        
        # Check if rate limit is exceeded
        return len(updated_history) <= self.rate_limit 