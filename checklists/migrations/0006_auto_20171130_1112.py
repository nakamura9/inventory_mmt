# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-30 09:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common_base', '0003_auto_20171130_1106'),
        ('checklists', '0005_auto_20171127_1444'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checklist',
            name='comments',
        ),
        migrations.AddField(
            model_name='checklist',
            name='comments',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='common_base.Comment'),
        ),
        migrations.RemoveField(
            model_name='checklist',
            name='tasks',
        ),
        migrations.AddField(
            model_name='checklist',
            name='tasks',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='common_base.Task'),
            preserve_default=False,
        ),
    ]
