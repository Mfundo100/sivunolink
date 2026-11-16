from django.db import migrations, connection

def reset_site_table(apps, schema_editor):
    with connection.cursor() as cursor:
        # 1. Clear the link between SocialApps and Sites (breaks the foreign key constraint)
        cursor.execute("DELETE FROM socialaccount_socialapp_sites;")
        
        # 2. Delete the SocialApps themselves (we will recreate this in Admin later)
        cursor.execute("DELETE FROM socialaccount_socialapp;")
        
        # 3. Now it is safe to delete the Sites
        cursor.execute("DELETE FROM django_site;")
        
        # 4. Insert the perfect Site with ID 1
        cursor.execute("""
            INSERT INTO django_site (id, domain, name) 
            VALUES (1, 'sivunolink-app.onrender.com', 'SivunoLink');
        """)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_producelisting_category'), 
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(reset_site_table),
    ]