from django.http import JsonResponse
from django.conf import settings
import logging
import time
from collections import defaultdict
from ..utils.security import sanitize_input, log_security_event
from ..utils.logging import logger

logger = logging.getLogger(__name__)

class BasicSecurityMiddleware:
    """
    Basic security middleware for common security measures
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_data = defaultdict(list)
        self.rate_limit_window = 60  # 1 minute window
        self.max_requests = settings.SECURITY_MIDDLEWARE.get('MAX_REQUESTS_PER_MINUTE', 60)
        self.block_duration = settings.SECURITY_MIDDLEWARE.get('BLOCK_DURATION_MINUTES', 15) * 60

    def __call__(self, request):
        # Skip security checks for static files and admin
        if request.path.startswith(('/static/', '/admin/', '/media/')):
            return self.get_response(request)

        # Check rate limiting
        if self._is_rate_limited(request):
            return JsonResponse({
                'error': 'Too many requests. Please try again later.',
                'status': 429
            }, status=429)

        # Log request for security monitoring
        self._log_request(request)

        try:
            # Sanitize input data
            request.GET = sanitize_input(request.GET)
            if request.method == 'POST':
                request.POST = sanitize_input(request.POST)

            response = self.get_response(request)

            # Add security headers
            response = self._add_security_headers(response)

            return response
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            return JsonResponse({
                'error': 'An internal server error occurred.',
                'status': 500
            }, status=500)

    def _is_rate_limited(self, request):
        """
        Check if the request should be rate limited
        """
        if not settings.SECURITY_MIDDLEWARE.get('ENABLE_RATE_LIMITING', True):
            return False

        client_ip = request.META.get('REMOTE_ADDR')
        current_time = time.time()

        # Clean up old entries
        self.rate_limit_data[client_ip] = [
            t for t in self.rate_limit_data[client_ip]
            if current_time - t < self.rate_limit_window
        ]

        # Check if we've exceeded the rate limit
        if len(self.rate_limit_data[client_ip]) >= self.max_requests:
            return True

        # Add the current request timestamp
        self.rate_limit_data[client_ip].append(current_time)
        return False

    def _log_request(self, request):
        """
        Log request details for security monitoring
        """
        try:
            log_security_event(
                'request_received',
                {
                    'method': request.method,
                    'path': request.path,
                    'ip': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT'),
                    'user': request.user.email if request.user.is_authenticated else 'anonymous',
                    'timestamp': time.time()
                }
            )
        except Exception as e:
            logger.error(f"Error logging request: {str(e)}")

    def _add_security_headers(self, response):
        """
        Add basic security headers to response
        """
        try:
            # Prevent clickjacking
            response['X-Frame-Options'] = 'DENY'
            
            # Enable XSS protection
            response['X-XSS-Protection'] = '1; mode=block'
            
            # Prevent MIME type sniffing
            response['X-Content-Type-Options'] = 'nosniff'
            
            # Add Content Security Policy
            csp = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
            response['Content-Security-Policy'] = csp
            
            # CORS headers
            if settings.DEBUG:
                response['Access-Control-Allow-Origin'] = '*'
            else:
                response['Access-Control-Allow-Origin'] = settings.CORS_ALLOWED_ORIGINS[0]
            
            # Add HSTS header if not in debug mode
            if not settings.DEBUG:
                response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            return response
        except Exception as e:
            logger.error(f"Error adding security headers: {str(e)}")
            return response 