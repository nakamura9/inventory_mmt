# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-08 15:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0047_auto_20170807_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='authored_date',
            field=models.DateField(default=datetime.datetime(2017, 8, 8, 15, 34, 9, 260000, tzinfo=utc)),
        ),
    ]
