from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_alter_feedback_attachment_alter_feedback_rating_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedbackcategory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ] 