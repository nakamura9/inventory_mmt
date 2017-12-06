# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-12-05 09:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inv', '0001_initial'),
        ('common_base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Costing',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=32, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='PreventativeTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('frequency', models.CharField(choices=[('once', 'Once off'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('fortnightly', 'Every 2 weeks'), ('monthly', 'Monthly'), ('quarterly', 'Every 3 Months'), ('bi-annually', 'Every 6 Months'), ('yearly', 'Yearly')], max_length=16)),
                ('estimated_labour_time', models.DurationField(choices=[(datetime.timedelta(0, 300), b'00:05'), (datetime.timedelta(0, 600), b'00:10'), (datetime.timedelta(0, 900), b'00:15'), (datetime.timedelta(0, 1200), b'00:20'), (datetime.timedelta(0, 1500), b'00:25'), (datetime.timedelta(0, 1800), b'00:30'), (datetime.timedelta(0, 2700), b'00:45'), (datetime.timedelta(0, 3600), b'01:00'), (datetime.timedelta(0, 4500), b'01:15'), (datetime.timedelta(0, 5400), b'01:30'), (datetime.timedelta(0, 6300), b'01:45'), (datetime.timedelta(0, 7200), b'02:00'), (datetime.timedelta(0, 9000), b'02:30'), (datetime.timedelta(0, 10800), b'03:00'), (datetime.timedelta(0, 12600), b'03:30'), (datetime.timedelta(0, 14400), b'04:00'), (datetime.timedelta(0, 16200), b'04:30'), (datetime.timedelta(0, 18000), b'05:00'), (datetime.timedelta(0, 19800), b'05:30'), (datetime.timedelta(0, 21600), b'06:00'), (datetime.timedelta(0, 23400), b'06:30'), (datetime.timedelta(0, 25200), b'07:00'), (datetime.timedelta(0, 27000), b'07:30')])),
                ('estimated_downtime', models.DurationField(choices=[(datetime.timedelta(0, 300), b'00:05'), (datetime.timedelta(0, 600), b'00:10'), (datetime.timedelta(0, 900), b'00:15'), (datetime.timedelta(0, 1200), b'00:20'), (datetime.timedelta(0, 1500), b'00:25'), (datetime.timedelta(0, 1800), b'00:30'), (datetime.timedelta(0, 2700), b'00:45'), (datetime.timedelta(0, 3600), b'01:00'), (datetime.timedelta(0, 4500), b'01:15'), (datetime.timedelta(0, 5400), b'01:30'), (datetime.timedelta(0, 6300), b'01:45'), (datetime.timedelta(0, 7200), b'02:00'), (datetime.timedelta(0, 9000), b'02:30'), (datetime.timedelta(0, 10800), b'03:00'), (datetime.timedelta(0, 12600), b'03:30'), (datetime.timedelta(0, 14400), b'04:00'), (datetime.timedelta(0, 16200), b'04:30'), (datetime.timedelta(0, 18000), b'05:00'), (datetime.timedelta(0, 19800), b'05:30'), (datetime.timedelta(0, 21600), b'06:00'), (datetime.timedelta(0, 23400), b'06:30'), (datetime.timedelta(0, 25200), b'07:00'), (datetime.timedelta(0, 27000), b'07:30')])),
                ('scheduled_for', models.DateField()),
                ('feedback', models.TextField(null=True)),
                ('actual_downtime', models.DurationField(choices=[(datetime.timedelta(0, 300), b'00:05'), (datetime.timedelta(0, 600), b'00:10'), (datetime.timedelta(0, 900), b'00:15'), (datetime.timedelta(0, 1200), b'00:20'), (datetime.timedelta(0, 1500), b'00:25'), (datetime.timedelta(0, 1800), b'00:30'), (datetime.timedelta(0, 2700), b'00:45'), (datetime.timedelta(0, 3600), b'01:00'), (datetime.timedelta(0, 4500), b'01:15'), (datetime.timedelta(0, 5400), b'01:30'), (datetime.timedelta(0, 6300), b'01:45'), (datetime.timedelta(0, 7200), b'02:00'), (datetime.timedelta(0, 9000), b'02:30'), (datetime.timedelta(0, 10800), b'03:00'), (datetime.timedelta(0, 12600), b'03:30'), (datetime.timedelta(0, 14400), b'04:00'), (datetime.timedelta(0, 16200), b'04:30'), (datetime.timedelta(0, 18000), b'05:00'), (datetime.timedelta(0, 19800), b'05:30'), (datetime.timedelta(0, 21600), b'06:00'), (datetime.timedelta(0, 23400), b'06:30'), (datetime.timedelta(0, 25200), b'07:00'), (datetime.timedelta(0, 27000), b'07:30')], null=True)),
                ('completed_date', models.DateField(null=True)),
                ('comments', models.TextField(null=True)),
                ('assignments', models.ManyToManyField(to='common_base.Account')),
                ('component', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Component')),
                ('machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Machine')),
                ('required_spares', models.ManyToManyField(related_name='preventativetask_required_spares', to='inv.Spares')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Section')),
                ('spares_used', models.ManyToManyField(related_name='preventativetask_spares_used', to='inv.Spares')),
                ('subassembly', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.SubAssembly')),
                ('subunit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.SubUnit')),
                ('tasks', models.ManyToManyField(to='common_base.Task')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('execution_date', models.DateField(default=datetime.date.today)),
                ('estimated_labour_time', models.DurationField(choices=[(datetime.timedelta(0, 300), b'00:05'), (datetime.timedelta(0, 600), b'00:10'), (datetime.timedelta(0, 900), b'00:15'), (datetime.timedelta(0, 1200), b'00:20'), (datetime.timedelta(0, 1500), b'00:25'), (datetime.timedelta(0, 1800), b'00:30'), (datetime.timedelta(0, 2700), b'00:45'), (datetime.timedelta(0, 3600), b'01:00'), (datetime.timedelta(0, 4500), b'01:15'), (datetime.timedelta(0, 5400), b'01:30'), (datetime.timedelta(0, 6300), b'01:45'), (datetime.timedelta(0, 7200), b'02:00'), (datetime.timedelta(0, 9000), b'02:30'), (datetime.timedelta(0, 10800), b'03:00'), (datetime.timedelta(0, 12600), b'03:30'), (datetime.timedelta(0, 14400), b'04:00'), (datetime.timedelta(0, 16200), b'04:30'), (datetime.timedelta(0, 18000), b'05:00'), (datetime.timedelta(0, 19800), b'05:30'), (datetime.timedelta(0, 21600), b'06:00'), (datetime.timedelta(0, 23400), b'06:30'), (datetime.timedelta(0, 25200), b'07:00'), (datetime.timedelta(0, 27000), b'07:30')])),
                ('priority', models.CharField(choices=[('high', 'High'), ('low', 'Low')], max_length=4)),
                ('status', models.CharField(choices=[('requested', 'Requested'), ('accepted', 'Accepted'), ('completed', 'Completed'), ('approved', 'Approved'), ('declined', 'Declined')], default='requested', max_length=16)),
                ('resolver_action', models.TextField(null=True)),
                ('actual_labour_time', models.DurationField(choices=[(datetime.timedelta(0, 300), b'00:05'), (datetime.timedelta(0, 600), b'00:10'), (datetime.timedelta(0, 900), b'00:15'), (datetime.timedelta(0, 1200), b'00:20'), (datetime.timedelta(0, 1500), b'00:25'), (datetime.timedelta(0, 1800), b'00:30'), (datetime.timedelta(0, 2700), b'00:45'), (datetime.timedelta(0, 3600), b'01:00'), (datetime.timedelta(0, 4500), b'01:15'), (datetime.timedelta(0, 5400), b'01:30'), (datetime.timedelta(0, 6300), b'01:45'), (datetime.timedelta(0, 7200), b'02:00'), (datetime.timedelta(0, 9000), b'02:30'), (datetime.timedelta(0, 10800), b'03:00'), (datetime.timedelta(0, 12600), b'03:30'), (datetime.timedelta(0, 14400), b'04:00'), (datetime.timedelta(0, 16200), b'04:30'), (datetime.timedelta(0, 18000), b'05:00'), (datetime.timedelta(0, 19800), b'05:30'), (datetime.timedelta(0, 21600), b'06:00'), (datetime.timedelta(0, 23400), b'06:30'), (datetime.timedelta(0, 25200), b'07:00'), (datetime.timedelta(0, 27000), b'07:30')], null=True)),
                ('downtime', models.DurationField(choices=[(datetime.timedelta(0, 300), b'00:05'), (datetime.timedelta(0, 600), b'00:10'), (datetime.timedelta(0, 900), b'00:15'), (datetime.timedelta(0, 1200), b'00:20'), (datetime.timedelta(0, 1500), b'00:25'), (datetime.timedelta(0, 1800), b'00:30'), (datetime.timedelta(0, 2700), b'00:45'), (datetime.timedelta(0, 3600), b'01:00'), (datetime.timedelta(0, 4500), b'01:15'), (datetime.timedelta(0, 5400), b'01:30'), (datetime.timedelta(0, 6300), b'01:45'), (datetime.timedelta(0, 7200), b'02:00'), (datetime.timedelta(0, 9000), b'02:30'), (datetime.timedelta(0, 10800), b'03:00'), (datetime.timedelta(0, 12600), b'03:30'), (datetime.timedelta(0, 14400), b'04:00'), (datetime.timedelta(0, 16200), b'04:30'), (datetime.timedelta(0, 18000), b'05:00'), (datetime.timedelta(0, 19800), b'05:30'), (datetime.timedelta(0, 21600), b'06:00'), (datetime.timedelta(0, 23400), b'06:30'), (datetime.timedelta(0, 25200), b'07:00'), (datetime.timedelta(0, 27000), b'07:30')], null=True)),
                ('completion_date', models.DateField(null=True)),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common_base.Account')),
                ('comments', models.ManyToManyField(to='common_base.Comment')),
                ('component', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Component')),
                ('costing', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobcards.Costing')),
                ('machine', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Machine')),
                ('section', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.Section')),
                ('spares_issued', models.ManyToManyField(related_name='workorder_spares_issued', to='inv.Spares')),
                ('spares_returned', models.ManyToManyField(related_name='workorder_spares_returned', to='inv.Spares')),
                ('subassembly', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.SubAssembly')),
                ('subunit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inv.SubUnit')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common_base.Category')),
            ],
        ),
    ]
