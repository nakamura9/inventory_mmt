# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-08 15:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inv_control', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='unit',
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='min_stock_level',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='reorder_quantity',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='unit',
            field=models.CharField(default=None, max_length=32),
            preserve_default=False,
        ),
    ]
