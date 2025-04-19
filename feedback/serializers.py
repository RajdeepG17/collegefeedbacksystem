from rest_framework import serializers
from django.utils import timezone
from .models import FeedbackCategory, Feedback, FeedbackComment, FeedbackHistory
from accounts.serializers import UserMinimalSerializer

class FeedbackCategorySerializer(serializers.ModelSerializer):
    """Serializer for feedback categories"""
    
    class Meta:
        model = FeedbackCategory
        fields = ['id', 'name', 'description', 'icon', 'active']
        read_only_fields = ['id']

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
    
    category = FeedbackCategorySerializer(read_only=True)
    submitter = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()
    days_open = serializers.SerializerMethodField()
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'title', 'description', 'category', 'submitter',
            'assigned_to', 'status', 'priority', 'created_at',
            'updated_at', 'resolved_at', 'days_open', 'rating'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at']
    
    def get_submitter(self, obj):
        if obj.is_anonymous:
            return 'Anonymous'
        return {
            'id': obj.submitter.id,
            'email': obj.submitter.email,
            'name': obj.submitter.get_full_name()
        }
    
    def get_assigned_to(self, obj):
        if not obj.assigned_to:
            return None
        return {
            'id': obj.assigned_to.id,
            'email': obj.assigned_to.email,
            'name': obj.assigned_to.get_full_name()
        }
    
    def get_days_open(self, obj):
        return obj.days_open

class FeedbackDetailSerializer(FeedbackListSerializer):
    """Serializer for detailed feedback view"""
    
    comments = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()
    
    class Meta(FeedbackListSerializer.Meta):
        fields = FeedbackListSerializer.Meta.fields + ['comments', 'history']
    
    def get_comments(self, obj):
        user = self.context['request'].user
        comments = obj.comments.all()
        
        if user.user_type not in ['admin', 'superadmin']:
            comments = comments.filter(is_internal=False)
        
        return FeedbackCommentSerializer(comments, many=True).data
    
    def get_history(self, obj):
        user = self.context['request'].user
        history = obj.history.all()
        
        if user.user_type == 'student':
            history = history.filter(feedback__submitter=user)
        
        return FeedbackHistorySerializer(history, many=True).data

class FeedbackCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating feedback"""
    
    class Meta:
        model = Feedback
        fields = [
            'title', 'description', 'category', 'priority',
            'is_anonymous', 'attachment'
        ]
    
    def validate_category(self, value):
        if not value.active:
            raise serializers.ValidationError("This category is not active")
        return value
    
    def validate_priority(self, value):
        if value not in dict(Feedback.PRIORITY_CHOICES):
            raise serializers.ValidationError("Invalid priority level")
        return value

class FeedbackUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating feedback"""
    
    class Meta:
        model = Feedback
        fields = [
            'title', 'description', 'category', 'assigned_to',
            'status', 'priority', 'is_anonymous', 'attachment'
        ]
        read_only_fields = ['submitter']
    
    def validate_status(self, value):
        if value not in dict(Feedback.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status")
        return value
    
    def validate_priority(self, value):
        if value not in dict(Feedback.PRIORITY_CHOICES):
            raise serializers.ValidationError("Invalid priority level")
        return value
    
    def validate_category(self, value):
        if not value.active:
            raise serializers.ValidationError("This category is not active")
        return value