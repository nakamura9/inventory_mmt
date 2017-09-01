# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-01 08:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobcards', '0002_auto_20170901_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorder',
            name='actual_labour_time',
            field=models.DurationField(null=True),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='completion_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='downtime',
            field=models.DurationField(null=True),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='resolver_action',
            field=models.TextField(null=True),
        ),
    ]
