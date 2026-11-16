from django.db import migrations

def create_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    
    # 1. Check if a site with the correct domain already exists (regardless of ID)
    existing_site = Site.objects.filter(domain='sivunolink-app.onrender.com').first()
    
    if existing_site:
        # If it exists, just make sure its ID is 1 and the name is correct
        existing_site.id = 1
        existing_site.name = 'SivunoLink'
        existing_site.save()
    else:
        # 2. If the domain doesn't exist, check if ID 1 is taken by 'example.com'
        site_id_1 = Site.objects.filter(id=1).first()
        if site_id_1:
            # Update example.com to our domain
            site_id_1.domain = 'sivunolink-app.onrender.com'
            site_id_1.name = 'SivunoLink'
            site_id_1.save()
        else:
            # 3. If neither exists, create it fresh
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