# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-11 18:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobcards', '0013_auto_20170611_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abstractjob',
            name='component',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Component'),
        ),
        migrations.AlterField(
            model_name='abstractjob',
            name='machine',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Machine'),
        ),
        migrations.AlterField(
            model_name='abstractjob',
            name='subassembly',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.SubAssembly'),
        ),
        migrations.AlterField(
            model_name='abstractjob',
            name='subunit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.SubUnit'),
        ),
    ]
