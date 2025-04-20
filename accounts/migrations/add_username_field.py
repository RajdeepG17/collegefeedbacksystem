from django.db import migrations, models
from django.utils.translation import gettext_lazy as _

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_add_is_staff_member_field'),  # Updated to the last migration
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(_('username'), max_length=150, blank=True, null=True),
        ),
    ] 