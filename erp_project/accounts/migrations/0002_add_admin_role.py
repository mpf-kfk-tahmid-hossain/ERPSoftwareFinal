from django.db import migrations


def create_admin_role(apps, schema_editor):
    Role = apps.get_model('accounts', 'Role')
    Role.objects.get_or_create(name='Admin', defaults={'description': 'Default admin role'})

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin_role, migrations.RunPython.noop),
    ]
