from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Feedback, FeedbackComment

@receiver(post_save, sender=Feedback)
def notify_feedback_update(sender, instance, created, **kwargs):
    """Send email notifications for feedback updates"""
    if created:
        # New feedback created
        subject = f'New Feedback Submitted: {instance.title}'
        template = 'emails/new_feedback.html'
        recipients = [instance.assigned_to.email] if instance.assigned_to else []
    else:
        # Feedback updated
        subject = f'Feedback Updated: {instance.title}'
        template = 'emails/feedback_updated.html'
        recipients = [instance.submitter.email]
        if instance.assigned_to:
            recipients.append(instance.assigned_to.email)
    
    # Prepare email content
    context = {
        'feedback': instance,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    }
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)
    
    # Send email
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=True,
    )

@receiver(post_save, sender=FeedbackComment)
def notify_new_comment(sender, instance, created, **kwargs):
    """Send email notifications for new comments"""
    if created and not instance.is_internal:
        feedback = instance.feedback
        subject = f'New Comment on Feedback: {feedback.title}'
        
        # Prepare email content
        context = {
            'feedback': feedback,
            'comment': instance,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
        }
        html_message = render_to_string('emails/new_comment.html', context)
        plain_message = strip_tags(html_message)
        
        # Determine recipients
        recipients = [feedback.submitter.email]
        if feedback.assigned_to:
            recipients.append(feedback.assigned_to.email)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=True,
        )

@receiver(pre_delete, sender=Feedback)
def cleanup_feedback_files(sender, instance, **kwargs):
    """Clean up files when feedback is deleted"""
    if instance.attachment:
        instance.attachment.delete(save=False)
    
    # Clean up comment attachments
    for comment in instance.comments.all():
        if comment.attachment:
            comment.attachment.delete(save=False) 