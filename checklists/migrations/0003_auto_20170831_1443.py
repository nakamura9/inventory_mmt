# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-31 12:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0002_auto_20170831_0813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklist',
            name='estimated_time',
            field=models.DurationField(choices=[(b'00:05:00', b'00:05:00'), (b'00:10:00', b'00:10:00'), (b'00:15:00', b'00:15:00'), (b'00:20:00', b'00:20:00'), (b'00:25:00', b'00:25:00'), (b'00:30:00', b'00:30:00'), (b'01:00:00', b'01:00:00'), (b'02:00:00', b'02:00:00'), (b'03:00:00', b'03:00:00'), (b'04:00:00', b'04:00:00'), (b'05:00:00', b'05:00:00'), (b'06:00:00', b'06:00:00'), (b'07:00:00', b'07:00:00'), (b'08:00:00', b'08:00:00')]),
        ),
        migrations.AlterField(
            model_name='checklist',
            name='start_time',
            field=models.TimeField(choices=[(b'06:30:00', b'06:30:00'), (b'07:00:00', b'07:00:00'), (b'07:30:00', b'07:30:00'), (b'08:00:00', b'08:00:00'), (b'08:30:00', b'08:30:00'), (b'09:00:00', b'09:00:00'), (b'09:30:00', b'09:30:00'), (b'10:00:00', b'10:00:00'), (b'10:30:00', b'10:30:00'), (b'11:00:00', b'11:00:00'), (b'11:30:00', b'11:30:00'), (b'12:00:00', b'12:00:00'), (b'12:30:00', b'12:30:00'), (b'13:00:00', b'13:00:00'), (b'13:30:00', b'13:30:00'), (b'14:00:00', b'14:00:00'), (b'14:30:00', b'14:30:00'), (b'15:00:00', b'15:00:00'), (b'15:30:00', b'15:30:00'), (b'16:00:00', b'16:00:00'), (b'16:30:00', b'16:30:00'), (b'17:00:00', b'17:00:00')]),
        ),
    ]
