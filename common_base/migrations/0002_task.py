# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-29 13:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common_base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_number', models.IntegerField()),
                ('description', models.CharField(max_length=1024)),
            ],
        ),
    ]
