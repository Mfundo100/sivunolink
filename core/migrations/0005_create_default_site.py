from django.db import migrations

def create_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    if not Site.objects.filter(id=1).exists():
        Site.objects.create(
            id=1,
            domain='sivunolink-app.onrender.com',
            name='SivunoLink'
        )

class Migration(migrations.Migration):

    dependencies = [
    ('core', '0004_alter_producelisting_category'), 
    ('sites', '0002_alter_domain_unique'),
]
   
    operations = [
        migrations.RunPython(create_default_site),
    ]

   