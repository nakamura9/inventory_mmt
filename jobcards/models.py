from __future__ import unicode_literals

from django.db import models
from inv.models import *
from common_base.models import Account
from django.utils import timezone
import time 
import datetime


class WorkOrder(models.Model):
    type = models.ForeignKey("common_base.Category")
    machine = models.ForeignKey("inv.Machine", null=True)
    section = models.ForeignKey("inv.Section", null=True)
    subunit = models.ForeignKey("inv.SubUnit", null=True)
    subassembly = models.ForeignKey("inv.SubAssembly", null=True)
    component = models.ForeignKey("inv.Component", null=True)
    description = models.TextField()
    execution_date = models.DateField(auto_now=True)
    estimated_labour_time = models.DurationField()
    assigned_to = models.ManyToManyField("common_base.Account")
    priority = models.CharField(max_length=4,
                                choices=[("high", "High"), ("low", "Low")])
    costing = models.ForeignKey("Costing", null=True)
    status = models.CharField(max_length=16, choices=[
                            ("requested", "Requested"),
                        ("accepted", "Accepted"),
                        ("completed", "Completed"),
                        ("approved", "Approved")
    ], default="requested")
    resolver_action= models.TextField()
    actual_labour_time = models.DurationField()
    downtime = models.DurationField()
    completion_date = models.DateField()
    spares_issued = models.ManyToManyField("inv.Spares", related_name="%(class)s_spares_issued")
    spares_returned = models.ManyToManyField("inv.Spares",related_name="%(class)s_spares_returned")


class PreventativeTask(models.Model):
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

    estimated_labour_time = models.DurationField()
    estimated_downtime = models.DurationField()
    required_spares = models.ManyToManyField("inv.Spares")
    assignments = models.ManyToManyField("common_base.Account")

class Costing(models.Model):
    id= models.CharField(max_length=32, primary_key=32)


class AbstractJob(models.Model):
    def __str__(self):
        return self.description

    
    description = models.TextField()
    creation_epoch = models.DateTimeField(default = timezone.now)
    number = models.AutoField(primary_key=True)
    resolver = models.ForeignKey("common_base.Account")
    estimated_time = models.CharField(max_length=4)
    completed = models.BooleanField(default = False)
    machine = models.ForeignKey("inv.Machine", null=True)
    section = models.ForeignKey("inv.Section", null=True)
    subunit = models.ForeignKey("inv.SubUnit", null=True)
    subassembly = models.ForeignKey("inv.SubAssembly", null=True)
    component = models.ForeignKey("inv.Component", null=True)

class Breakdown(AbstractJob):
    requested_by = models.ForeignKey("common_base.Account")
    


    #used when completing the Jobcard
     
    def save(self, *args, **kwargs):
        self.creation_epoch = timezone.now()
        super(Breakdown, self).save(*args, **kwargs)

    @property
    def people(self):
        ret_value = []
        for user in Account.objects.all():
            ret_calue.append((user.user_name, user.user_name))
        return ret_value

class PlannedJob(AbstractJob):
    scheduled_for = models.DateField()

    @property
    def get_type(self):
        return "job"

class JobCard(models.Model):
    completion_epoch = models.DateTimeField()
    on_hold = models.BooleanField(default = False)
    job_execution_time = models.CharField(max_length=4)
    # create response time fields
    breakdown = models.OneToOneField("Breakdown", null=True)
    planned_job = models.OneToOneField("PlannedJob", null=True)
    number = models.AutoField(primary_key=True)
    components_requested = models.CharField(max_length = 128)
    resolver_action = models.TextField()
    root_cause = models.TextField()
    notes = models.TextField()
    recommended_pm = models.TextField()


    

class Job(models.Model):
    breakdown = models.OneToOneField("Breakdown")
    jobcard = models.OneToOneField("JobCard")
