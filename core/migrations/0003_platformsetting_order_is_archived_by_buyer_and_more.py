from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_order_payment_method'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlatformSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commission_rate', models.DecimalField(decimal_places=2, default=10.0, help_text='Percentage e.g. 10.00', max_digits=5)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='is_archived_by_buyer',
            field=models.BooleanField(default=False),
        ),
    ]