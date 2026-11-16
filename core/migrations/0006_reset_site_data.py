from django.db import migrations

def reset_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    
    # 1. Delete all existing site records to clear out duplicates and bad IDs
    Site.objects.all().delete()
    
    # 2. Create the one correct site record with ID=1
    Site.objects.create(
        id=1,
        domain='sivunolink-app.onrender.com',
        name='SivunoLink'
    )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_create_default_site'), # Depends on the previous file
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(reset_site),
    ]