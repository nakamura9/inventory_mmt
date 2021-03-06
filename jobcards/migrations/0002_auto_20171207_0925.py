# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-12-07 07:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common_base', '0001_initial'),
        ('jobcards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='preventativetask',
            name='assignments_accepted',
            field=models.ManyToManyField(related_name='preventativetask_assignments_accepted', to='common_base.Account'),
        ),
        migrations.AlterField(
            model_name='preventativetask',
            name='assignments',
            field=models.ManyToManyField(related_name='preventativetask_assignments_made', to='common_base.Account'),
        ),
    ]
