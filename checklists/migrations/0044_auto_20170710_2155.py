# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-10 19:55
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0043_auto_20170707_0917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='authored_date',
            field=models.DateField(default=datetime.datetime(2017, 7, 10, 19, 55, 6, 419000, tzinfo=utc)),
        ),
    ]
