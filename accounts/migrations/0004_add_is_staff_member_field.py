# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_add_bio_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_staff_member',
            field=models.BooleanField(default=False),
        ),
    ] 