# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-31 06:13
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('artisan', 'Artisan'), ('operator', 'Operator')], max_length=128)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_for', models.CharField(choices=[('checklist', 'Checklist'), ('work_order', 'Work Order'), ('preventative_task', 'Preventative Task')], max_length=24)),
                ('name', models.CharField(max_length=32, unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_for', models.CharField(choices=[('checklist', 'Checklist'), ('work_order', 'Work Order'), ('preventative_task', 'Preventative Task')], max_length=24)),
                ('content', models.CharField(max_length=1024)),
                ('authored_date', models.DateField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common_base.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_for', models.CharField(choices=[('checklist', 'Checklist'), ('work_order', 'Work Order'), ('preventative_task', 'Preventative Task')], max_length=24)),
                ('task_number', models.IntegerField()),
                ('description', models.CharField(max_length=1024)),
            ],
        ),
    ]
