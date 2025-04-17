
from django.utils import timezone
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count

from .models import FeedbackCategory, Feedback, FeedbackComment, FeedbackHistory
from .serializers import (
    FeedbackCategorySerializer, FeedbackListSerializer, 
    FeedbackDetailSerializer, FeedbackCreateSerializer,
    FeedbackUpdateSerializer, FeedbackCommentSerializer,
    FeedbackHistorySerializer
)
from accounts.views import IsAdminUser

class FeedbackCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for feedback categories"""
    
    queryset = FeedbackCategory.objects.filter(active=True)
    serializer_class = FeedbackCategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for feedback management"""
    
    queryset = Feedback.objects.all()
    serializer_class = FeedbackListSerializer
    permission_classes = [IsAuthenticated]
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
    user = self.request.user
    
    # Filter based on user type
    if user.user_type == 'student':
        # Students can only see their own feedback
        return Feedback.objects.filter(submitter=user)
    elif user.user_type == 'admin' and user.admin_category != 'none':
        # Category admins can only see feedback in their category
        return Feedback.objects.filter(
            Q(category_name_iexact=user.admin_category) | 
            Q(assigned_to=user)
        )
    # Superadmins can see all feedback
    return Feedback.objects.all()
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics"""
        user = request.user
        
    # Base queryset based on user type
    # Base queryset based on user type
    if user.user_type == 'student':
        queryset = Feedback.objects.filter(submitter=user)
    elif user.user_type == 'admin' and user.admin_category != 'none':
        queryset = Feedback.objects.filter(
            Q(category_name_iexact=user.admin_category) | 
            Q(assigned_to=user)
    )
    else:
        queryset = Feedback.objects.all()
        
        # Get counts by status
        status_counts = {
            status: queryset.filter(status=status).count() 
            for status in dict(Feedback.STATUS_CHOICES).keys()
        }
        
        # Get counts by priority
        priority_counts = {
            priority: queryset.filter(priority=priority).count() 
            for priority in dict(Feedback.PRIORITY_CHOICES).keys()
        }
        
        # Get counts by category
        category_counts = queryset.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent feedback
        recent = queryset.order_by('-created_at')[:5]
        recent_serializer = FeedbackListSerializer(recent, many=True)
        
        # Urgent feedback
        urgent = queryset.filter(priority='urgent', status__in=['pending', 'in_progress'])
        urgent_serializer = FeedbackListSerializer(urgent, many=True)
        
        return Response({
            'status_counts': status_counts,
            'priority_counts': priority_counts,
            'category_counts': list(category_counts),
            'recent': recent_serializer.data,
            'urgent': urgent_serializer.data,
            'total': queryset.count(),
        })
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark feedback as resolved"""
        feedback = self.get_object()
        
        # Only admins or the assigned user can resolve
        if not (request.user.user_type in ['admin', 'superadmin'] or 
                request.user == feedback.assigned_to):
            return Response(
                {'error': 'You do not have permission to perform this action'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update feedback status
        feedback.status = 'resolved'
        feedback.resolved_at = timezone.now()
        feedback.save()
        
        # Create history record
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
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen a resolved or closed feedback"""
        feedback = self.get_object()
        
        # Check if feedback is eligible for reopening
        if feedback.status not in ['resolved', 'closed', 'rejected']:
            return Response(
                {'error': 'Only resolved, closed or rejected feedback can be reopened'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Only submitter or admins can reopen
        if not (request.user == feedback.submitter or 
                request.user.user_type in ['admin', 'superadmin']):
            return Response(
                {'error': 'You do not have permission to perform this action'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        old_status = feedback.status
        
        # Update feedback status
        feedback.status = 'in_progress'
        feedback.resolved_at = None
        feedback.save()
        
        # Create history record
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
        
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Add user satisfaction rating to feedback"""
        feedback = self.get_object()
        
        # Only submitter can rate
        if request.user != feedback.submitter:
            return Response(
                {'error': 'Only the submitter can rate the feedback'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Get rating from request
        rating = request.data.get('rating')
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except (ValueError, TypeError):
            return Response(
                {'error': 'Rating must be an integer between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Update feedback rating
        feedback.rating = rating
        feedback.save()
        
        return Response({
            'message': 'Rating submitted successfully',
            'feedback': FeedbackDetailSerializer(feedback, context={'request': request}).data
        })

class FeedbackCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for feedback comments"""
    
    queryset = FeedbackComment.objects.all()
    serializer_class = FeedbackCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Filter based on user type and feedback ID
        feedback_id = self.request.query_params.get('feedback_id')
        if feedback_id:
            queryset = FeedbackComment.objects.filter(feedback_id=feedback_id)
            
            # If not admin, filter out internal comments
            if user.user_type not in ['admin', 'superadmin']:
                queryset = queryset.filter(is_internal=False)
                
            return queryset
            
        # Default case
        if user.user_type in ['admin', 'superadmin']:
            return FeedbackComment.objects.all()
        return FeedbackComment.objects.filter(is_internal=False)
    
    def perform_create(self, serializer):
        # Set the user automatically
        serializer.save(user=self.request.user)
        
        # Get the related feedback
        feedback_id = serializer.validated_data.get('feedback').id
        feedback = Feedback.objects.get(id=feedback_id)
        
        # If feedback is pending, update to in_progress
        if feedback.status == 'pending':
            feedback.status = 'in_progress'
            feedback.save()
            
            # Create history record
            FeedbackHistory.objects.create(
                feedback=feedback,
                changed_by=self.request.user,
                old_status='pending',
                new_status='in_progress',
                old_assigned_to=feedback.assigned_to,
                new_assigned_to=feedback.assigned_to,
                notes=f"Status changed to in progress due to new comment by {self.request.user.email}"
            )

class FeedbackHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for feedback history (read-only)"""
    
    queryset = FeedbackHistory.objects.all()
    serializer_class = FeedbackHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filter by feedback ID if provided
        feedback_id = self.request.query_params.get('feedback_id')
        if feedback_id:
            return FeedbackHistory.objects.filter(feedback_id=feedback_id)
        
        # Only admins can see all history
        user = self.request.user
        if user.user_type in ['admin', 'superadmin']:
            return FeedbackHistory.objects.all()
            
        # Students can see history of their own feedback
        return FeedbackHistory.objects.filter(feedback__submitter=user)
