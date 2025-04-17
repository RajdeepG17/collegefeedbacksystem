
from rest_framework import serializers
from .models import FeedbackCategory, Feedback, FeedbackComment, FeedbackHistory
from accounts.serializers import UserMinimalSerializer

class FeedbackCategorySerializer(serializers.ModelSerializer):
    """Serializer for feedback categories"""
    
    class Meta:
        model = FeedbackCategory
        fields = ['id', 'name', 'description', 'icon', 'active']
        
class FeedbackCommentSerializer(serializers.ModelSerializer):
    """Serializer for feedback comments"""
    
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = FeedbackComment
        fields = ['id', 'feedback', 'user', 'comment', 'created_at', 
                  'updated_at', 'attachment', 'is_internal']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
        
    def create(self, validated_data):
        # Set the user to the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class FeedbackHistorySerializer(serializers.ModelSerializer):
    """Serializer for feedback history"""
    
    changed_by = UserMinimalSerializer(read_only=True)
    old_assigned_to = UserMinimalSerializer(read_only=True)
    new_assigned_to = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = FeedbackHistory
        fields = ['id', 'feedback', 'changed_by', 'old_status', 'new_status',
                  'old_assigned_to', 'new_assigned_to', 'notes', 'timestamp']
        read_only_fields = fields

class FeedbackListSerializer(serializers.ModelSerializer):
    """Serializer for listing feedback"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    submitter = UserMinimalSerializer(read_only=True)
    assigned_to = UserMinimalSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Feedback
        fields = ['id', 'title', 'category', 'category_name', 'status', 
                  'priority', 'submitter', 'assigned_to', 'created_at', 
                  'updated_at', 'resolved_at', 'comments_count', 'days_open']
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at', 
                           'days_open', 'comments_count']
        
    def get_comments_count(self, obj):
        return obj.comments.count()

class FeedbackDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed feedback view"""
    
    category = FeedbackCategorySerializer(read_only=True)
    submitter = UserMinimalSerializer(read_only=True)
    assigned_to = UserMinimalSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    history = FeedbackHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'title', 'description', 'category', 'status', 'priority',
                  'submitter', 'assigned_to', 'created_at', 'updated_at', 
                  'resolved_at', 'attachment', 'is_anonymous', 'rating', 
                  'comments', 'history', 'days_open']
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at', 
                           'days_open', 'submitter', 'history']
                           
    def get_comments(self, obj):
        # Filter comments based on user type
        user = self.context['request'].user
        comments = obj.comments.all()
        
        # If the user is not an admin, filter out internal comments
        if user.user_type not in ['admin', 'superadmin']:
            comments = comments.filter(is_internal=False)
            
        return FeedbackCommentSerializer(comments, many=True).data

class FeedbackCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating feedback"""
    
    class Meta:
        model = Feedback
        fields = ['title', 'description', 'category', 'priority', 
                  'attachment', 'is_anonymous']
        
    def create(self, validated_data):
        # Set the submitter to the current user
        validated_data['submitter'] = self.context['request'].user
        
        # Try to assign to the appropriate admin based on category
        category = validated_data.get('category')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            admin = User.objects.filter(
                user_type='admin',
                admin_category=category.name.lower(),
                is_active=True
            ).first()
            if admin:
                validated_data['assigned_to'] = admin
        except Exception:
            pass
            
        return super().create(validated_data)

class FeedbackUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating feedback"""
    
    class Meta:
        model = Feedback
        fields = ['status', 'priority', 'assigned_to', 'resolved_at', 'rating']
        
    def update(self, instance, validated_data):
        user = self.context['request'].user
        old_status = instance.status
        old_assigned_to = instance.assigned_to
        
        # Update the instance
        instance = super().update(instance, validated_data)
        
        # Create history record if status or assignment changed
        if old_status != instance.status or old_assigned_to != instance.assigned_to:
            FeedbackHistory.objects.create(
                feedback=instance,
                changed_by=user,
                old_status=old_status,
                new_status=instance.status,
                old_assigned_to=old_assigned_to,
                new_assigned_to=instance.assigned_to,
                notes=f"Status updated by {user.email}"
            )
            
        return instance