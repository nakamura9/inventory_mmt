# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

roles = [("admin", "Admin"),
        ("artisan", "Artisan"),
        ("operator","Operator")]

class Account(User):
    role = models.CharField(max_length=128, choices= roles)
    def __str__(self):
        return self.username + " -> " + self.role


class Task(models.Model):
    created_for = models.CharField(max_length=24, choices=[
                            ("checklist", "Checklist"),
                            ("work_order", "Work Order"),
                            ("preventative_task", "Preventative Task")
    ])
    task_number = models.IntegerField()
    description = models.CharField(max_length=1024, unique=True)

class Comment(models.Model):
    created_for = models.CharField(max_length=24, choices=[
                            ("checklist", "Checklist"),
                            ("work_order", "Work Order"),
                            ("preventative_task", "Preventative Task")
    ])
    author = models.ForeignKey("Account")
    content = models.CharField(max_length = 1024)
    authored_date = models.DateField(default=timezone.now) 

class Category(models.Model):
    created_for = models.CharField(max_length=24, choices=[
                            ("checklist", "Checklist"),
                            ("work_order", "Work Order"),
                            ("preventative_task", "Preventative Task")
    ])
    name = models.CharField(max_length= 32, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name