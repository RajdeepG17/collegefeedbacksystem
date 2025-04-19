from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.conf import settings
import re
import html
from .utils.logging import logger

class RequestThrottlingMiddleware:
    """
    Middleware to implement request throttling
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'RATE_LIMIT', 100)  # requests per minute
        self.rate_window = 60  # 1 minute window

    def __call__(self, request):
        # Skip throttling for admin and documentation URLs
        if request.path.startswith(('/admin/', '/swagger/', '/redoc/')):
            return self.get_response(request)

        # Generate cache key based on IP and path
        ip = request.META.get('REMOTE_ADDR')
        path = request.path
        cache_key = f"throttle:{ip}:{path}"

        # Get current request count
        request_count = cache.get(cache_key, 0)

        # Check if rate limit exceeded
        if request_count >= self.rate_limit:
            logger.warning(
                "rate_limit_exceeded",
                ip=ip,
                path=path,
                count=request_count
            )
            return HttpResponseForbidden("Rate limit exceeded. Please try again later.")

        # Increment request count
        cache.set(cache_key, request_count + 1, self.rate_window)

        response = self.get_response(request)
        return response

class InputSanitizationMiddleware:
    """
    Middleware to sanitize user input
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.sanitize_patterns = [
            (r'<script.*?>.*?</script>', ''),  # Remove script tags
            (r'<.*?javascript:.*?>', ''),     # Remove javascript: URLs
            (r'<.*?\son\w+=.*?>', ''),        # Remove event handlers
        ]

    def __call__(self, request):
        # Sanitize GET parameters
        request.GET = self._sanitize_dict(request.GET)
        
        # Sanitize POST parameters
        if request.method == 'POST':
            request.POST = self._sanitize_dict(request.POST)
        
        # Sanitize request body for JSON requests
        if request.content_type == 'application/json':
            try:
                request._body = self._sanitize_json(request.body)
            except:
                pass

        response = self.get_response(request)
        return response

    def _sanitize_dict(self, data):
        """
        Sanitize dictionary values
        """
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self._sanitize_string(value)
            elif isinstance(value, (list, tuple)):
                sanitized[key] = [self._sanitize_string(v) if isinstance(v, str) else v for v in value]
            else:
                sanitized[key] = value
        return sanitized

    def _sanitize_string(self, value):
        """
        Sanitize string value
        """
        # HTML escape
        value = html.escape(value)
        
        # Apply additional sanitization patterns
        for pattern, replacement in self.sanitize_patterns:
            value = re.sub(pattern, replacement, value, flags=re.IGNORECASE | re.DOTALL)
        
        return value

    def _sanitize_json(self, json_data):
        """
        Sanitize JSON data
        """
        import json
        data = json.loads(json_data)
        sanitized = self._sanitize_dict(data)
        return json.dumps(sanitized) 