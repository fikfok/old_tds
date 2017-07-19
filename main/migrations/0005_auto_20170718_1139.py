# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-18 11:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20170717_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedfiles',
            name='file_upload_date_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uploadedfiles',
            name='upload_into_es_indexing_done',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
