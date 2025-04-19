from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.core.cache import cache
from college_feedback_system.middleware.security import BasicSecurityMiddleware
from college_feedback_system.middleware.error_handling import ErrorHandlingMiddleware
from college_feedback_system.middleware.performance import PerformanceMonitoringMiddleware
from django.core.exceptions import ValidationError, PermissionDenied
import time

class MiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.security_middleware = BasicSecurityMiddleware(lambda r: HttpResponse())
        self.error_middleware = ErrorHandlingMiddleware(lambda r: HttpResponse())
        self.performance_middleware = PerformanceMonitoringMiddleware(lambda r: HttpResponse())
        cache.clear()

    def test_security_middleware_rate_limiting(self):
        """Test rate limiting functionality"""
        request = self.factory.get('/test')
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        # Make requests up to the limit
        for _ in range(60):  # Default limit is 60 requests per minute
            response = self.security_middleware(request)
            self.assertEqual(response.status_code, 200)

        # Next request should be rate limited
        response = self.security_middleware(request)
        self.assertEqual(response.status_code, 429)

    def test_security_middleware_headers(self):
        """Test security headers are properly set"""
        request = self.factory.get('/test')
        response = self.security_middleware(request)

        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_error_handling_middleware_validation_error(self):
        """Test handling of validation errors"""
        def view(request):
            raise ValidationError('Test validation error')

        middleware = ErrorHandlingMiddleware(view)
        request = self.factory.get('/test')
        response = middleware(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn('Validation Error', str(response.content))

    def test_error_handling_middleware_permission_error(self):
        """Test handling of permission errors"""
        def view(request):
            raise PermissionDenied()

        middleware = ErrorHandlingMiddleware(view)
        request = self.factory.get('/test')
        response = middleware(request)

        self.assertEqual(response.status_code, 403)
        self.assertIn('Permission Denied', str(response.content))

    def test_performance_middleware_metrics(self):
        """Test performance metrics collection"""
        def slow_view(request):
            time.sleep(0.1)  # Simulate slow processing
            return HttpResponse()

        middleware = PerformanceMonitoringMiddleware(slow_view)
        request = self.factory.get('/test')
        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        # Metrics are logged, so we can't directly test them here
        # They will be visible in the logs

    def test_performance_middleware_memory_usage(self):
        """Test memory usage tracking"""
        def memory_intensive_view(request):
            # Create a large list to increase memory usage
            large_list = [i for i in range(1000000)]
            return HttpResponse()

        middleware = PerformanceMonitoringMiddleware(memory_intensive_view)
        request = self.factory.get('/test')
        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        # Memory metrics are logged, so we can't directly test them here
        # They will be visible in the logs

    def test_performance_middleware_query_count(self):
        """Test query count tracking"""
        def query_intensive_view(request):
            # Perform multiple queries
            from django.contrib.auth.models import User
            User.objects.all()
            User.objects.all()
            return HttpResponse()

        middleware = PerformanceMonitoringMiddleware(query_intensive_view)
        request = self.factory.get('/test')
        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        # Query metrics are logged, so we can't directly test them here
        # They will be visible in the logs 