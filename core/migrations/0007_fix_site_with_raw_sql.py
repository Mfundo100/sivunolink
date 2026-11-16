from django.db import migrations, connection

def fix_site_sql(apps, schema_editor):
    with connection.cursor() as cursor:
        # 1. Wipe the entire site table to clear out all duplicates and weird IDs
        cursor.execute("DELETE FROM django_site;")
        
        # 2. Insert the one correct site with ID 1
        cursor.execute("""
            INSERT INTO django_site (id, domain, name) 
            VALUES (1, 'sivunolink-app.onrender.com', 'SivunoLink');
        """)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_reset_site_data'), # Depends on the previous migration
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(fix_site_sql),
    ]