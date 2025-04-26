from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0012_merge_20250426_1457'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='priority',
        ),
    ] 