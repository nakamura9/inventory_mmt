# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-12-13 08:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inv', '0009_auto_20171213_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rundata',
            name='friday',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='rundata',
            name='monday',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='rundata',
            name='saturday',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='rundata',
            name='sunday',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='rundata',
            name='thursday',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='rundata',
            name='tuesday',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='rundata',
            name='wednesday',
            field=models.BooleanField(),
        ),
    ]
