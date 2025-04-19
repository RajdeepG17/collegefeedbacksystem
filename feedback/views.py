from django.utils import timezone
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.db.models import Q, Count
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError

from .models import FeedbackCategory, Feedback, FeedbackComment, FeedbackHistory
from .serializers import (
    FeedbackCategorySerializer, FeedbackListSerializer, 
    FeedbackDetailSerializer, FeedbackCreateSerializer,
    FeedbackUpdateSerializer, FeedbackCommentSerializer,
    FeedbackHistorySerializer
)
from accounts.views import IsAdminUser

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class FeedbackCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for feedback categories"""
    
    queryset = FeedbackCategory.objects.filter(active=True)
    serializer_class = FeedbackCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserRateThrottle]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for feedback management"""
    
    queryset = Feedback.objects.all()
    serializer_class = FeedbackListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserRateThrottle]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'status', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FeedbackCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FeedbackUpdateSerializer
        elif self.action == 'retrieve':
            return FeedbackDetailSerializer
        return FeedbackListSerializer
    
    def get_queryset(self):
        try:
            user = self.request.user
            cache_key = f'feedback_queryset_{user.id}_{user.user_type}_{self.request.query_params}'
            queryset = cache.get(cache_key)
            
            if queryset is None:
                if user.user_type == 'student':
                    queryset = Feedback.objects.filter(submitter=user)
                elif user.user_type == 'admin' and user.admin_category != 'none':
                    queryset = Feedback.objects.filter(
                        Q(category__name__iexact=user.admin_category) |
                        Q(assigned_to=user)
                    )
                else:
                    queryset = Feedback.objects.all()
                
                queryset = queryset.select_related(
                    'category',
                    'submitter',
                    'assigned_to'
                ).prefetch_related(
                    'comments',
                    'history'
                )
                
                cache.set(cache_key, queryset, 300)
            
            return queryset
        except Exception as e:
            raise DRFValidationError(f"Error fetching feedback: {str(e)}")
    
    def perform_create(self, serializer):
        try:
            serializer.save(submitter=self.request.user)
        except ValidationError as e:
            raise DRFValidationError(str(e))
        except Exception as e:
            raise DRFValidationError(f"Error creating feedback: {str(e)}")
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'resolve']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def perform_update(self, serializer):
        try:
            feedback = self.get_object()
            if not self.request.user.user_type in ['admin', 'superadmin']:
                raise PermissionDenied("Only admins can update feedback")
            if feedback.status in ['resolved', 'closed']:
                raise PermissionDenied("Cannot update resolved or closed feedback")
            serializer.save()
        except ValidationError as e:
            raise DRFValidationError(str(e))
        except Exception as e:
            raise DRFValidationError(f"Error updating feedback: {str(e)}")
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics"""
        try:
            user = request.user
            cache_key = f'dashboard_stats_{user.id}_{user.user_type}'
            stats = cache.get(cache_key)
            
            if stats is None:
                if user.user_type == 'student':
                    queryset = Feedback.objects.filter(submitter=user)
                elif user.user_type == 'admin' and user.admin_category != 'none':
                    queryset = Feedback.objects.filter(
                        Q(category__name__iexact=user.admin_category) |
                        Q(assigned_to=user)
                    )
                else:
                    queryset = Feedback.objects.all()
                
                queryset = queryset.select_related('category')
                
                status_counts = {
                    status: queryset.filter(status=status).count()
                    for status in dict(Feedback.STATUS_CHOICES).keys()
                }
                
                priority_counts = {
                    priority: queryset.filter(priority=priority).count()
                    for priority in dict(Feedback.PRIORITY_CHOICES).keys()
                }
                
                category_counts = queryset.values('category__name').annotate(
                    count=Count('id')
                ).order_by('-count')
                
                recent = queryset.order_by('-created_at')[:5]
                recent_serializer = FeedbackListSerializer(recent, many=True)
                
                urgent = queryset.filter(priority='urgent', status__in=['pending', 'in_progress'])
                urgent_serializer = FeedbackListSerializer(urgent, many=True)
                
                stats = {
                    'status_counts': status_counts,
                    'priority_counts': priority_counts,
                    'category_counts': list(category_counts),
                    'recent': recent_serializer.data,
                    'urgent': urgent_serializer.data,
                    'total': queryset.count(),
                }
                
                cache.set(cache_key, stats, 300)
            
            return Response(stats)
        except Exception as e:
            return Response(
                {'error': f"Error fetching dashboard data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark feedback as resolved"""
        try:
            feedback = self.get_object()
            
            if not (request.user.user_type in ['admin', 'superadmin'] or 
                    request.user == feedback.assigned_to):
                raise PermissionDenied(
                    'You do not have permission to resolve this feedback. Only admins or assigned users can resolve feedback.'
                )
            
            if feedback.status == 'resolved':
                raise DRFValidationError('This feedback is already resolved.')
            
            feedback.status = 'resolved'
            feedback.resolved_at = timezone.now()
            feedback.save()
            
            FeedbackHistory.objects.create(
                feedback=feedback,
                changed_by=request.user,
                old_status='in_progress' if feedback.status == 'in_progress' else 'pending',
                new_status='resolved',
                old_assigned_to=feedback.assigned_to,
                new_assigned_to=feedback.assigned_to,
                notes=f"Marked as resolved by {request.user.email}"
            )
            
            return Response({
                'message': 'Feedback marked as resolved',
                'feedback': FeedbackDetailSerializer(feedback, context={'request': request}).data
            })
        except PermissionDenied as e:
            return Response(
                {'error': 'Permission denied', 'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except DRFValidationError as e:
            return Response(
                {'error': 'Invalid operation', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f"Error resolving feedback: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen a resolved or closed feedback"""
        try:
            feedback = self.get_object()
            
            if feedback.status not in ['resolved', 'closed', 'rejected']:
                raise DRFValidationError('Only resolved, closed, or rejected feedback can be reopened.')
            
            if not (request.user == feedback.submitter or 
                    request.user.user_type in ['admin', 'superadmin']):
                raise PermissionDenied(
                    'You do not have permission to reopen this feedback. Only the submitter or admins can reopen feedback.'
                )
            
            old_status = feedback.status
            
            feedback.status = 'in_progress'
            feedback.resolved_at = None
            feedback.save()
            
            FeedbackHistory.objects.create(
                feedback=feedback,
                changed_by=request.user,
                old_status=old_status,
                new_status='in_progress',
                old_assigned_to=feedback.assigned_to,
                new_assigned_to=feedback.assigned_to,
                notes=f"Reopened by {request.user.email}"
            )
            
            return Response({
                'message': 'Feedback reopened',
                'feedback': FeedbackDetailSerializer(feedback, context={'request': request}).data
            })
        except PermissionDenied as e:
            return Response(
                {'error': 'Permission denied', 'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except DRFValidationError as e:
            return Response(
                {'error': 'Invalid operation', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f"Error reopening feedback: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate feedback"""
        feedback = self.get_object()
        
        if request.user != feedback.submitter:
            return Response(
                {'error': 'Only the submitter can rate feedback'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if feedback.status != 'resolved':
            return Response(
                {'error': 'Can only rate resolved feedback'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rating = request.data.get('rating')
        if not rating or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            return Response(
                {'error': 'Rating must be a number between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        feedback.rating = rating
        feedback.save()
        
        # Create a comment if provided
        comment = request.data.get('comment')
        if comment:
            FeedbackComment.objects.create(
                feedback=feedback,
                user=request.user,
                comment=comment,
                is_internal=False
            )
        
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class FeedbackCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for feedback comments"""
    
    queryset = FeedbackComment.objects.all()
    serializer_class = FeedbackCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserRateThrottle]
    
    def get_queryset(self):
        try:
            feedback_id = self.kwargs.get('feedback_id')
            user = self.request.user
            
            queryset = FeedbackComment.objects.filter(feedback_id=feedback_id)
            
            if user.user_type not in ['admin', 'superadmin']:
                queryset = queryset.filter(is_internal=False)
            
            return queryset.select_related('user', 'feedback')
        except Exception as e:
            raise DRFValidationError(f"Error fetching comments: {str(e)}")
    
    def perform_create(self, serializer):
        try:
            feedback_id = self.kwargs.get('feedback_id')
            feedback = Feedback.objects.get(id=feedback_id)
            
            # Check if user can create internal comments
            if serializer.validated_data.get('is_internal', False):
                if self.request.user.user_type not in ['admin', 'superadmin']:
                    raise PermissionDenied('Only admins can create internal comments')
            
            serializer.save(
                feedback=feedback,
                user=self.request.user
            )
        except PermissionDenied as e:
            raise PermissionDenied(str(e))
        except Feedback.DoesNotExist:
            raise DRFValidationError('Feedback not found')
        except Exception as e:
            raise DRFValidationError(f"Error creating comment: {str(e)}")

class FeedbackHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for feedback history (read-only)"""
    
    queryset = FeedbackHistory.objects.all()
    serializer_class = FeedbackHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        try:
            feedback_id = self.kwargs.get('feedback_id')
            user = self.request.user
            
            if user.user_type == 'student':
                return FeedbackHistory.objects.filter(
                    feedback_id=feedback_id,
                    feedback__submitter=user
                )
            elif user.user_type == 'admin' and user.admin_category != 'none':
                return FeedbackHistory.objects.filter(
                    feedback_id=feedback_id,
                    feedback__category__name__iexact=user.admin_category
                )
            else:
                return FeedbackHistory.objects.filter(feedback_id=feedback_id)
        except Exception as e:
            raise DRFValidationError(f"Error fetching history: {str(e)}")
