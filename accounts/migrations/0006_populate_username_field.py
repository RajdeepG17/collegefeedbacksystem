from django.db import migrations

def populate_username(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    for user in User.objects.all():
        if not user.username:
            user.username = user.email
            user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_add_username_field'),
    ]

    operations = [
        migrations.RunPython(populate_username),
    ] 