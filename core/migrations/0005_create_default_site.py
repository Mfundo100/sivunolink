from django.db import migrations, connection

def reset_site_table(apps, schema_editor):
    with connection.cursor() as cursor:
        # 1. Delete everything in the site table to clear out any duplicate domains
        cursor.execute("DELETE FROM django_site;")
        
        # 2. Insert the correct site with ID 1
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