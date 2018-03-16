# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-08 15:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replayer', '0006_auto_20180307_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='config',
            field=models.CharField(default='', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='log',
            name='config',
            field=models.CharField(default='', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='trace',
            name='config',
            field=models.CharField(default='', max_length=500, null=True),
        ),
    ]
