# Generated by Django 3.2.18 on 2023-08-30 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_payment', '0013_auto_20230830_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentserviceprovider',
            name='is_external_api_user',
            field=models.BooleanField(default=False),
        ),
    ]
