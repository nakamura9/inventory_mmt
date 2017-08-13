# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-25 11:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='id',
            field=models.AutoField(auto_created=True, default=0, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='task',
            name='checklist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checklists.Checklist'),
        ),
    ]
