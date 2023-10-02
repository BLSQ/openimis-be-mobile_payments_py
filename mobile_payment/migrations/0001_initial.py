# Generated by Django 3.2.20 on 2023-08-10 16:10

import core.fields
import core.models
import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0016_add_last_login_on_interactive_user'),
        ('contribution', '0015_auto_20230810_1610'),
        ('insuree', '0003_insureepolicy'),
    ]

    operations = [
        migrations.CreateModel(
            name='Api_Utilities',
            fields=[
                ('id', models.AutoField(db_column='Api_Id', primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, db_column='Name', max_length=50, null=True)),
                ('access_token', models.TextField(blank=True, db_column='access_token', null=True)),
                ('access_TokenExpiry', models.DateTimeField(blank=True, db_column='ExpiryDate', null=True)),
            ],
            options={
                'db_table': 'tblApi_Utilities',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom', default=datetime.datetime.now)),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('id', models.AutoField(db_column='TransactionId', primary_key=True, serialize=False)),
                ('uuid', models.CharField(db_column='TransactionUUID', default=uuid.uuid4, max_length=36, unique=True)),
                ('amount', models.DecimalField(db_column='Amount', decimal_places=2, max_digits=18)),
                ('transaction_id', models.CharField(blank=True, db_column='transaction_id', max_length=125)),
                ('otp', models.CharField(blank=True, db_column='OTP', max_length=10, null=True)),
                ('status', models.BooleanField(blank=True, db_column='transaction_status', default=False)),
                ('datetime', models.DateTimeField(blank=True, db_column='Datetime', default=django.utils.timezone.now)),
                ('Insuree', models.ForeignKey(blank=True, db_column='InsureeUUID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='transactions', to='insuree.insuree')),
                ('PaymentServiceProvider', models.ForeignKey(blank=True, db_column='PSPUUID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='transactions', to='contribution.paymentserviceprovider')),
            ],
            options={
                'db_table': 'tblTransactions',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TransactionMutation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('mutation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='transactions', to='core.mutationlog')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='mutations', to='mobile_payment.transactions')),
            ],
            options={
                'db_table': 'TransactionMutation',
                'managed': True,
            },
            bases=(models.Model, core.models.ObjectMutation),
        ),
    ]
