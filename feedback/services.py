from django.db.models import Q
from .models import Notification, Feedback, FeedbackComment
from accounts.models import User
from utils.logging import logger

class NotificationService:
    @staticmethod
    def create_notification(feedback, notification_type, message, users=None):
        """
        Create notifications for specified users or all relevant users
        """
        try:
            if users is None:
                # Default users to notify
                users = set()
                users.add(feedback.submitter)
                if feedback.assigned_to:
                    users.add(feedback.assigned_to)
                # Add department heads if department is specified
                if hasattr(feedback, 'department') and feedback.department:
                    department_users = User.objects.filter(
                        Q(user_type='admin') & 
                        Q(department=feedback.department)
                    )
                    users.update(department_users)

            notifications = []
            for user in users:
                notification = Notification.objects.create(
                    user=user,
                    feedback=feedback,
                    notification_type=notification_type,
                    message=message
                )
                notifications.append(notification)

            logger.info(
                "notifications_created",
                count=len(notifications),
                feedback_id=feedback.id,
                notification_type=notification_type
            )
            return notifications

        except Exception as e:
            logger.error(
                "notification_creation_failed",
                error=str(e),
                feedback_id=feedback.id,
                notification_type=notification_type
            )
            return []

    @staticmethod
    def notify_feedback_created(feedback):
        message = f"New feedback created: {feedback.title}"
        return NotificationService.create_notification(
            feedback,
            'feedback_created',
            message
        )

    @staticmethod
    def notify_feedback_updated(feedback, changes):
        message = f"Feedback updated: {feedback.title}\nChanges: {changes}"
        return NotificationService.create_notification(
            feedback,
            'feedback_updated',
            message
        )

    @staticmethod
    def notify_status_changed(feedback, old_status, new_status):
        message = f"Feedback status changed from {old_status} to {new_status}: {feedback.title}"
        return NotificationService.create_notification(
            feedback,
            'feedback_status_changed',
            message
        )

    @staticmethod
    def notify_assignment_changed(feedback, old_assignee, new_assignee):
        message = f"Feedback assigned to {new_assignee.email if new_assignee else 'unassigned'}: {feedback.title}"
        return NotificationService.create_notification(
            feedback,
            'feedback_assigned',
            message,
            users={new_assignee} if new_assignee else None
        )

    @staticmethod
    def notify_comment_added(comment):
        message = f"New comment on feedback: {comment.feedback.title}"
        return NotificationService.create_notification(
            comment.feedback,
            'feedback_comment',
            message
        )

    @staticmethod
    def get_user_notifications(user, unread_only=False):
        """
        Get notifications for a user, optionally filtered by read status
        """
        query = Q(user=user)
        if unread_only:
            query &= Q(is_read=False)
        
        return Notification.objects.filter(query).select_related(
            'feedback',
            'feedback__submitter',
            'feedback__assigned_to'
        )

    @staticmethod
    def mark_notifications_as_read(notification_ids, user):
        """
        Mark specific notifications as read for a user
        """
        try:
            updated = Notification.objects.filter(
                id__in=notification_ids,
                user=user,
                is_read=False
            ).update(is_read=True)
            
            logger.info(
                "notifications_marked_read",
                count=updated,
                user=user.email
            )
            return updated
        except Exception as e:
            logger.error(
                "mark_notifications_read_failed",
                error=str(e),
                user=user.email
            )
            return 0 