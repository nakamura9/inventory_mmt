# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-26 11:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobcards', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('number', models.CharField(max_length=12)),
                ('resolver', models.CharField(max_length=128)),
                ('estimated_time', models.TimeField()),
            ],
        ),
        migrations.RemoveField(
            model_name='breakdown',
            name='date',
        ),
        migrations.RemoveField(
            model_name='breakdown',
            name='id',
        ),
        migrations.RemoveField(
            model_name='breakdown',
            name='number',
        ),
        migrations.RemoveField(
            model_name='breakdown',
            name='resolver',
        ),
        migrations.RemoveField(
            model_name='breakdown',
            name='time',
        ),
        migrations.RemoveField(
            model_name='jobcard',
            name='id',
        ),
        migrations.AddField(
            model_name='jobcard',
            name='planned',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='jobcard',
            name='number',
            field=models.CharField(max_length=12, primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='PlannedJob',
            fields=[
                ('abstractjob_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jobcards.AbstractJob')),
                ('recurring', models.BooleanField()),
                ('description', models.CharField(max_length=1024)),
            ],
            bases=('jobcards.abstractjob',),
        ),
        migrations.AddField(
            model_name='breakdown',
            name='abstractjob_ptr',
            field=models.OneToOneField(auto_created=True, default=None, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jobcards.AbstractJob'),
            preserve_default=False,
        ),
    ]
