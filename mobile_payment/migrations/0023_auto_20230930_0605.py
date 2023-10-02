# Generated by Django 3.2.21 on 2023-09-30 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_payment', '0022_paymentserviceprovider_interactive_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='api_records',
            name='request_date',
            field=models.TextField(blank=True, db_column='requested_data', null=True),
        ),
        migrations.AlterField(
            model_name='api_records',
            name='response_date',
            field=models.TextField(blank=True, db_column='response_data', null=True),
        ),
    ]
