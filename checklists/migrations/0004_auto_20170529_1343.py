# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-29 11:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0003_auto_20170427_1343'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checklist',
            name='id',
        ),
        migrations.RemoveField(
            model_name='task',
            name='completed',
        ),
        migrations.AlterField(
            model_name='checklist',
            name='title',
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
    ]
