from __future__ import unicode_literals
import time 
import datetime
from itertools import chain

from django.utils import timezone
from django.db import models

from inv.models import *
from common_base.models import Account
from common_base.utilities import time_choices

time_duration = [] + time_choices("00:05:00", "00:30:00", "00:05:00",
            delta=True) + time_choices("00:30:00", "02:00:00", "00:15:00",
            delta=True) + time_choices("02:00:00", "08:00:00", "00:30:00",
            delta=True)  

class WorkOrder(models.Model):
    """Model that represents a job assigned ad-hoc i.e. a breakdown.

    Fields: type, machine, section, subunit, subassembly, component,
            description, execution_date,estimated_labour_time,assigned_to, 
            priority, costing, status, resolver_action, actual_labour_time,
            downtime,completion_date, spares_issued, spares_returned"""


    type = models.ForeignKey("common_base.Category")
    machine = models.ForeignKey("inv.Machine", null=True)
    section = models.ForeignKey("inv.Section", null=True)
    subunit = models.ForeignKey("inv.SubUnit", null=True, blank=True)
    subassembly = models.ForeignKey("inv.SubAssembly", null=True, blank=True)
    component = models.ForeignKey("inv.Component", null=True, blank=True)
    description = models.TextField(unique=False)
    execution_date = models.DateField(default=datetime.date.today)
    estimated_labour_time = models.DurationField(choices = time_duration)
    assigned_to = models.ForeignKey("common_base.Account")
    priority = models.CharField(max_length=4,
                                choices=[("high", "High"), ("low", "Low")])
    costing = models.ForeignKey("Costing", null=True)
    status = models.CharField(max_length=16, choices=[
                            ("requested", "Requested"),
                        ("accepted", "Accepted"),
                        ("completed", "Completed"),
                        ("approved", "Approved"),
                        ("declined", "Declined"),
    ], default="requested")
    
    resolver_action= models.TextField(null=True)
    actual_labour_time = models.DurationField(null=True, choices=time_duration)
    downtime = models.DurationField(null=True, choices=time_duration)
    completion_date = models.DateField(null=True)
    spares_issued = models.ManyToManyField("inv.Spares", related_name="%(class)s_spares_issued")
    spares_returned = models.ManyToManyField("inv.Spares",related_name="%(class)s_spares_returned")
    comments = models.TextField(null =True)


class PreventativeTask(models.Model):
    """Model representing preventatitve maintenance jobs.

    May be once off or recurring 
    Fields: machine, section, subunit, subassembly, component,
            description, tasks, frequency, scheduled_for, estimated_labour_time,assignments, feedback, actual_downtime,completed_date, spares_issued, spares_returned

    Properties: is_open-> Boolean"""
    
    mapping =  {"daily": 1,
        "weekly": 7,
        "fortnightly": 14,
        "monthly": 30,
        "quarterly": 90,
        "bi-annually": 180,
        "yearly": 360}
    @property
    def get_type(self):
        return "job"

    def __str__(self):
        return self.description

    machine = models.ForeignKey("inv.Machine", null=True, blank=True)
    section = models.ForeignKey("inv.Section", null=True, blank=True)
    subunit = models.ForeignKey("inv.SubUnit", null=True, blank=True)
    subassembly = models.ForeignKey("inv.SubAssembly", null=True, blank=True)
    component = models.ForeignKey("inv.Component", null=True, blank=True)
    description = models.TextField(unique=False)
    tasks = models.ManyToManyField("common_base.Task")
    frequency = models.CharField(max_length = 16, 
                        choices = [("once", "Once off"),
                                    ("daily", "Daily"),
                                    ("weekly", "Weekly"),
                                    ("fortnightly", "Every 2 weeks"),
                                    ("monthly", "Monthly"),
                                    ("quarterly", "Every 3 Months"),
                                    ("bi-annually", "Every 6 Months"), 
                                    ("yearly", "Yearly")])

    estimated_labour_time = models.DurationField(choices=time_duration)
    estimated_downtime = models.DurationField(choices=time_duration)
    scheduled_for = models.DateField()
    required_spares = models.ManyToManyField("inv.Spares", related_name="%(class)s_required_spares")
    assignments = models.ManyToManyField("common_base.Account")
    feedback = models.TextField(null=True)
    actual_downtime = models.DurationField(null=True,choices=time_duration)
    completed_date = models.DateField(null=True)
    spares_used = models.ManyToManyField("inv.Spares", related_name="%(class)s_spares_used")
    comments  = models.TextField(null=True)
    
    @property
    def is_open(self):
        if self.completed_date is None:
            return True
        else:
            if self.frequency == "once":
                return False
            
            delta = datetime.date.today() - self.completed_date

        if delta.days > self.mapping[self.frequency]:
            return True
        else:
            return False

class Costing(models.Model):
    """Model used when planning the budget of a preventative task."""
    id= models.CharField(max_length=32, primary_key=32)
