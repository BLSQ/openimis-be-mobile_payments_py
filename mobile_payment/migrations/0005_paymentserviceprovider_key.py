# Generated by Django 3.2.23 on 2023-12-19 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_payment', '0004_mobile_payment_rights'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentserviceprovider',
            name='key',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
