# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

roles = [("admin", "Admin"),
        ("artisan", "Artisan"),
        ("operator","Operator")]

class Account(User):
    """Model that represents any user on the site.
    
    Inherits from the user class and its functionality, adds the role field to segregate access to different areas within the application."""

    role = models.CharField(max_length=128, choices= roles)
    def __str__(self):
        return self.username + " -> " + self.role


class Task(models.Model):
    """The task model is used to divide jobs into discrete steps.
    
    It has a foreign key relationship with the job it belongs to.
    Fields: created_for, task_number(within the job), description(max_length 1024)."""

    created_for = models.CharField(max_length=24, choices=[
                            ("checklist", "Checklist"),
                            ("work_order", "Work Order"),
                            ("preventative_task", "Preventative Task")
    ])
    task_number = models.IntegerField()
    description = models.CharField(max_length=1024, unique=True)

class Comment(models.Model):
    """The comment model represents a piece of communication during the execution of some job.

    fields: created_for, author, content, authored_date
    """

    created_for = models.CharField(max_length=24, choices=[
                            ("checklist", "Checklist"),
                            ("work_order", "Work Order"),
                            ("preventative_task", "Preventative Task")
    ])
    author = models.ForeignKey("Account")
    content = models.CharField(max_length = 1024)
    authored_date = models.DateField(default=timezone.now) 

class Category(models.Model):
    """THe category model is used to organize data associated with inventory, jobs and tasks.
    
    fields: created_for, name, description"""
    
    created_for = models.CharField(max_length=24, choices=[
                            ("checklist", "Checklist"),
                            ("work_order", "Work Order"),
                            ("preventative_task", "Preventative Task")
    ])
    name = models.CharField(max_length= 32, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name