# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-09 18:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobcards', '0010_auto_20170609_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='abstractjob',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]
