# Generated by Django 3.2.16 on 2023-07-07 13:38

import core.fields
import datetime
from django.db import migrations, models

from core.utils import insert_role_right_for_system


def add_rights(apps, schema_editor):

    insert_role_right_for_system(64, 125000)  # search
    insert_role_right_for_system(64, 125001)  # create
    insert_role_right_for_system(64, 125002)  # update
    insert_role_right_for_system(64, 125003)  # search
    insert_role_right_for_system(64, 125004)  # create
    insert_role_right_for_system(64, 125005)  # search
    insert_role_right_for_system(64, 125006)  # create
    insert_role_right_for_system(64, 125007)  # update
    insert_role_right_for_system(64, 125008)  # delete
    
class Migration(migrations.Migration):

    dependencies = [
        ('mobile_payment', '0003_alter_paymenttransaction_json_content'),
    ]

    operations = [
        migrations.RunPython(add_rights),
    ]