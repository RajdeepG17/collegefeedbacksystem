import time
import logging
import psutil
from django.conf import settings
from django.db import connection
from django.core.cache import cache

logger = logging.getLogger('college_feedback')

class PerformanceMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        # Get initial query count
        initial_queries = len(connection.queries)

        response = self.get_response(request)

        # Calculate metrics
        duration = time.time() - start_time
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_used = end_memory - start_memory
        query_count = len(connection.queries) - initial_queries

        # Log performance metrics
        self._log_performance_metrics(request, duration, memory_used, query_count)

        return response

    def _log_performance_metrics(self, request, duration, memory_used, query_count):
        """Log performance metrics for the request"""
        metrics = {
            'path': request.path,
            'method': request.method,
            'duration': f"{duration:.2f}s",
            'memory_used': f"{memory_used:.2f}MB",
            'query_count': query_count,
            'user': request.user.email if request.user.is_authenticated else 'anonymous',
        }

        # Log SQL queries if enabled
        if settings.PERFORMANCE_MONITORING['ENABLE_SQL_LOGGING']:
            metrics['queries'] = connection.queries

        # Log cache stats if enabled
        if settings.PERFORMANCE_MONITORING['ENABLE_CACHE_LOGGING']:
            metrics['cache_stats'] = cache._cache.get_stats()

        # Log memory usage if enabled
        if settings.PERFORMANCE_MONITORING['ENABLE_MEMORY_LOGGING']:
            process = psutil.Process()
            metrics['memory_info'] = {
                'rss': process.memory_info().rss / 1024 / 1024,  # MB
                'vms': process.memory_info().vms / 1024 / 1024,  # MB
                'percent': process.memory_percent(),
            }

        logger.info("Performance metrics", extra=metrics)

        # Log warning if performance thresholds are exceeded
        if duration > 1.0:  # More than 1 second
            logger.warning(f"Slow request detected: {request.path} took {duration:.2f}s")
        if query_count > 20:  # More than 20 queries
            logger.warning(f"High query count detected: {request.path} made {query_count} queries")
        if memory_used > 50:  # More than 50MB
            logger.warning(f"High memory usage detected: {request.path} used {memory_used:.2f}MB") 