# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-17 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20170717_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfiles',
            name='upload_into_es_task_id',
            field=models.CharField(db_index=True, max_length=50, null=True, unique=True),
        ),
    ]