# Generated by Django 3.2.18 on 2023-09-07 16:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_payment', '0018_paymentserviceprovider_technical_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentserviceprovider',
            name='technical_user',
        ),
    ]
