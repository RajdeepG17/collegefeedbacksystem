from django.db import migrations, models
import django.core.validators

def migrate_user_to_submitter(apps, schema_editor):
    # Get the historical model
    Feedback = apps.get_model('feedback', 'Feedback')
    
    # For each feedback, set submitter to user if it exists
    for feedback in Feedback.objects.all():
        # This will only work if both fields exist during migration
        if hasattr(feedback, 'user_id') and feedback.user_id:
            feedback.submitter_id = feedback.user_id
            feedback.save(update_fields=['submitter_id'])

class Migration(migrations.Migration):
    dependencies = [
        ('feedback', '0010_update_feedback_table'),  # Adjust this to your last migration
    ]

    operations = [
        # Add submitter field first
        migrations.AddField(
            model_name='feedback',
            name='submitter',
            field=models.ForeignKey(null=True, on_delete=models.deletion.CASCADE, related_name='submitted_feedbacks', to='accounts.user'),
        ),
        # Run the data migration
        migrations.RunPython(migrate_user_to_submitter),
        # Make submitter required after data is migrated
        migrations.AlterField(
            model_name='feedback',
            name='submitter',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='submitted_feedbacks', to='accounts.user'),
        ),
        # Add the rest of the fields
        migrations.AddField(
            model_name='feedback',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='assigned_feedbacks', to='accounts.user'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='priority',
            field=models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=20),
        ),
        migrations.AddField(
            model_name='feedback',
            name='resolved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='rating',
            field=models.IntegerField(blank=True, help_text='Rating from 1 to 5', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        # Finally remove the old user field
        migrations.RemoveField(
            model_name='feedback',
            name='user',
        ),
    ] 