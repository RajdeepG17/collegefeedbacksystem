
from django.contrib import admin
from .models import FeedbackCategory, Feedback, FeedbackComment, FeedbackHistory

@admin.register(FeedbackCategory)
class FeedbackCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'active')
    search_fields = ('name', 'description')
    list_filter = ('active',)

class FeedbackCommentInline(admin.TabularInline):
    model = FeedbackComment
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('user', 'comment', 'attachment', 'is_internal', 'created_at')

class FeedbackHistoryInline(admin.TabularInline):
    model = FeedbackHistory
    extra = 0
    readonly_fields = ('timestamp', 'changed_by', 'old_status', 'new_status', 'old_assigned_to', 'new_assigned_to', 'notes')
    fields = ('timestamp', 'changed_by', 'old_status', 'new_status', 'old_assigned_to', 'new_assigned_to', 'notes')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'submitter', 'status', 'priority', 'created_at', 'days_open')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('title', 'description', 'submitter__email')
    readonly_fields = ('created_at', 'updated_at', 'days_open')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category', 'submitter', 'assigned_to')
        }),
        ('Status Information', {
            'fields': ('status', 'priority', 'created_at', 'updated_at', 'resolved_at')
        }),
        ('Additional Information', {
            'fields': ('attachment', 'is_anonymous', 'rating', 'days_open')
        }),
    )
    inlines = [FeedbackCommentInline, FeedbackHistoryInline]
    
    def save_model(self, request, obj, form, change):
        """Override save_model to create history entry when status is changed"""
        if change:  # If this is a change to an existing object
            try:
                old_obj = self.model.objects.get(pk=obj.pk)
                # Check if status has changed
                if old_obj.status != obj.status or old_obj.assigned_to != obj.assigned_to:
                    # Create history entry
                    FeedbackHistory.objects.create(
                        feedback=obj,
                        changed_by=request.user,
                        old_status=old_obj.status,
                        new_status=obj.status,
                        old_assigned_to=old_obj.assigned_to,
                        new_assigned_to=obj.assigned_to,
                        notes=f"Status changed by admin {request.user.email}"
                    )
            except self.model.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)

@admin.register(FeedbackComment)
class FeedbackCommentAdmin(admin.ModelAdmin):
    list_display = ('feedback', 'user', 'created_at', 'is_internal')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('feedback_title', 'user_email', 'comment')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(FeedbackHistory)
class FeedbackHistoryAdmin(admin.ModelAdmin):
    list_display = ('feedback', 'timestamp', 'changed_by', 'old_status', 'new_status')
    list_filter = ('timestamp', 'old_status', 'new_status')
    search_fields = ('feedback_title', 'changed_by_email', 'notes')
    readonly_fields = ('timestamp',)