# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-19 17:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inv', '0006_auto_20170819_1930'),
        ('jobcards', '0005_auto_20170818_1305'),
    ]

    operations = [
        migrations.AddField(
            model_name='abstractjob',
            name='section',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Section'),
        ),
    ]