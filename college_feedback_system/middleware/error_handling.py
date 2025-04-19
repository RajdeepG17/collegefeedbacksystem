from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
import logging
import traceback
from django.conf import settings
import json

logger = logging.getLogger(__name__)

def get_error_details(exception):
    """Extract error details from exception"""
    if hasattr(exception, 'detail'):
        return exception.detail
    return str(exception)

def log_error(exception, context=None):
    """Log error with context"""
    error_details = {
        'error_type': type(exception).__name__,
        'error_message': str(exception),
        'traceback': traceback.format_exc(),
    }
    
    if context:
        error_details['context'] = {
            'view': context.get('view', None),
            'args': context.get('args', None),
            'kwargs': context.get('kwargs', None),
            'request_method': context.get('request').method if context.get('request') else None,
            'request_path': context.get('request').path if context.get('request') else None,
        }
    
    logger.error(json.dumps(error_details, default=str))

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, ValidationError):
            log_error(exc, context)
            return Response(
                {
                    'error': 'Validation Error',
                    'message': get_error_details(exc),
                    'status': status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, PermissionDenied):
            log_error(exc, context)
            return Response(
                {
                    'error': 'Permission Denied',
                    'message': 'You do not have permission to perform this action',
                    'status': status.HTTP_403_FORBIDDEN
                },
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            log_error(exc, context)
            return Response(
                {
                    'error': 'Internal Server Error',
                    'message': 'An unexpected error occurred. Please try again later.',
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return response

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.enable_logging = settings.ERROR_HANDLING.get('ENABLE_LOGGING', True)
        self.log_level = settings.ERROR_HANDLING.get('LOG_LEVEL', 'ERROR')
        self.send_email_notifications = settings.ERROR_HANDLING.get('SEND_EMAIL_NOTIFICATIONS', False)

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as exc:
            return self.process_exception(request, exc)

    def process_exception(self, request, exception):
        if self.enable_logging:
            log_error(exception, {'request': request})

        if isinstance(exception, ValidationError):
            return JsonResponse(
                {
                    'error': 'Validation Error',
                    'message': get_error_details(exception),
                    'status': 400
                },
                status=400
            )
        elif isinstance(exception, PermissionDenied):
            return JsonResponse(
                {
                    'error': 'Permission Denied',
                    'message': 'You do not have permission to perform this action',
                    'status': 403
                },
                status=403
            )
        else:
            return JsonResponse(
                {
                    'error': 'Internal Server Error',
                    'message': 'An unexpected error occurred. Please try again later.',
                    'status': 500
                },
                status=500
            ) 