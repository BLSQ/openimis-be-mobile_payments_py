# Generated by Django 3.2.18 on 2023-08-31 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_payment', '0016_auto_20230831_0233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentserviceprovider',
            name='access_token',
            field=models.CharField(blank=True, db_column='Api_client_access_token', max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='paymentserviceprovider',
            name='psp_password',
            field=models.CharField(blank=True, db_column='Psp_Password', max_length=128, null=True),
        ),
    ]
