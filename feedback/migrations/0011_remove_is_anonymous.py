from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0010_update_feedback_table'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='is_anonymous',
        ),
    ] 