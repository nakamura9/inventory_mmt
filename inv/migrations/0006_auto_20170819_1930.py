# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-19 17:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inv', '0005_auto_20170815_1210'),
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('unique_id', models.CharField(max_length=24, primary_key=True, serialize=False)),
                ('section_name', models.CharField(max_length=64)),
                ('machine', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inv.Machine')),
            ],
        ),
        migrations.AddField(
            model_name='subunit',
            name='section',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inv.Section'),
        ),
    ]
