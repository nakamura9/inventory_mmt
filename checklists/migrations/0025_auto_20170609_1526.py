# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-09 13:26
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0024_auto_20170609_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='authored_date',
            field=models.DateField(default=datetime.datetime(2017, 6, 9, 13, 26, 28, 166000, tzinfo=utc)),
        ),
    ]
