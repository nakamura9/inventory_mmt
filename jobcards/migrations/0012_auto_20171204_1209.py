# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-12-04 10:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common_base', '0003_auto_20171130_1106'),
        ('jobcards', '0011_workorder_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workorder',
            name='comments',
        ),
        migrations.AddField(
            model_name='workorder',
            name='comments',
            field=models.ManyToManyField(to='common_base.Comment'),
        ),
    ]
