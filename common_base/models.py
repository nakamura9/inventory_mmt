# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

roles = [("admin", "Admin"),
        ("artisan", "Artisan"),
        ("operator","Operator")]

class Account(User):
    role = models.CharField(max_length=128, choices= roles)
    def __str__(self):
        return self.username + " -> " + self.role
