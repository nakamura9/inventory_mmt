# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-08 14:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0013_auto_20170606_2204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='authored_date',
            field=models.DateField(default=datetime.datetime(2017, 6, 8, 14, 45, 28, 219000, tzinfo=utc)),
        ),
    ]
