# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-01 08:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inv', '0004_auto_20170901_0154'),
        ('common_base', '0002_auto_20170831_1443'),
        ('jobcards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='preventativetask',
            name='actual_downtime',
            field=models.DurationField(null=True),
        ),
        migrations.AddField(
            model_name='preventativetask',
            name='completed_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='preventativetask',
            name='component',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Component'),
        ),
        migrations.AddField(
            model_name='preventativetask',
            name='description',
            field=models.TextField(default='none'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='preventativetask',
            name='feedback',
            field=models.ManyToManyField(to='common_base.Comment'),
        ),
        migrations.AddField(
            model_name='preventativetask',
            name='machine',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Machine'),
        ),
        migrations.AddField(
            model_name='preventativetask',
            name='section',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Section'),
        ),
        migrations.AddField(
            model_name='preventativetask',
            name='spares_used',
            field=models.ManyToManyField(related_name='preventativetask_spares_used', to='inv.Spares'),
        ),
        migrations.AddField(
            model_name='preventativetask',
            name='subassembly',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.SubAssembly'),
        ),
        migrations.AddField(
            model_name='preventativetask',
            name='subunit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.SubUnit'),
        ),
        migrations.AlterField(
            model_name='preventativetask',
            name='required_spares',
            field=models.ManyToManyField(related_name='preventativetask_required_spares', to='inv.Spares'),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='execution_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]