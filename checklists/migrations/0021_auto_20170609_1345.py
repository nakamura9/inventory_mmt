# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-09 11:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0020_auto_20170609_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='authored_date',
            field=models.DateField(default=datetime.datetime(2017, 6, 9, 11, 45, 3, 90000, tzinfo=utc)),
        ),
    ]
