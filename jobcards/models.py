from __future__ import unicode_literals

from django.db import models
from inv.models import *
from common_base.models import Account
from django.utils import timezone
import time 
import datetime


# Create your models here.

#people = [(a.username,a.username) for a in Account.objects.all()]
class AbstractJob(models.Model):
    description = models.TextField()
    creation_epoch = models.DateTimeField(default = timezone.now)
    number = models.CharField(max_length = 12 )
    resolver = models.ForeignKey("common_base.Account")
    estimated_time = models.CharField(max_length=4)
    completed = models.BooleanField(default = False)
    machine = models.ForeignKey("inv.Machine", null=True)
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
    scheduled_for = models.DateTimeField()



class JobCard(models.Model):
    completion_epoch = models.DateTimeField()
    on_hold = models.BooleanField(default = False)
    job_execution_time = models.CharField(max_length=4)
    # create response time fields
    breakdown = models.OneToOneField("Breakdown", null=True)
    planned_job = models.OneToOneField("PlannedJob", null=True)
    number = models.CharField(max_length = 12, primary_key=True)
    components_requested = models.CharField(max_length = 128)
    resolver_action = models.TextField()
    root_cause = models.TextField()
    notes = models.TextField()
    recommended_pm = models.TextField()


    

class Job(models.Model):
    breakdown = models.OneToOneField("Breakdown")
    jobcard = models.OneToOneField("JobCard")
