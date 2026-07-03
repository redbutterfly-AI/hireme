from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_default_admin(apps, schema_editor):
    User = apps.get_model('users', 'User')
    if not User.objects.filter(username='Thoko').exists():
        User.objects.create(
            username='Thoko',
            password=make_password('thoko123#'),
            email='thoko@hireme.local',
            role='admin',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_verified=True,
        )


def remove_default_admin(apps, schema_editor):
    User = apps.get_model('users', 'User')
    User.objects.filter(username='Thoko').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_user_company_name'),
    ]

    operations = [
        migrations.RunPython(create_default_admin, remove_default_admin),
    ]