from __future__ import unicode_literals
from __future__ import division

from django.db import models

from datetime import timedelta
from django.utils import timezone

# Create your models here.
from django.contrib.auth.models import User


# Create your models here.
roles = [("admin", "Admin"),
        ("artisan", "Artisan"),
        ("operator","Operator")]

class Account(User):
    role = models.CharField(max_length=128, choices= roles)
    def __str__(self):
        return self.username

        
class Plant(models.Model):
    plant_name= models.CharField(max_length = 128)
    
    def __str__(self):
        return self.plant_name

class Machine(models.Model):
    machine_name = models.CharField(max_length=128)
    unique_id = models.CharField(max_length=24, primary_key=True)
    manufacturer = models.CharField(max_length=128)
    estimated_value = models.CharField(max_length=128)
    #documentation = models.FileField()
    commissioning_date = models.DateField()

    def __str__(self):
        return self.machine_name

    @property
    def n_units(self):
        return self.subunit_set.all().count()

    @property
    def n_breakdowns_today(self):
        yesterday = timezone.now() - timedelta(days=1)
        return self.abstractjob_set.filter(creation_epoch__gt = yesterday).count()


    @property
    def n_breakdowns_weekly(self):
        week = timezone.now() - timedelta(days=7)
        return self.abstractjob_set.filter(creation_epoch__gt = week).count()


    @property
    def n_breakdowns_monthly(self):
        month = timezone.now() - timedelta(days=30)
        return self.abstractjob_set.filter(creation_epoch__gt = month).count()


    @property
    def n_breakdowns_sixmonths(self):
        bi_ann = timezone.now() - timedelta(days=182)
        return self.abstractjob_set.filter(creation_epoch__gt = bi_ann).count()


    @property
    def checklist_coverage(self):
        checklists = self.checklist_set.all()
        n_units = self.subunit_set.all().count()
        n_assys = self.subassembly_set.all().count()
        n_units_covered = 0
        n_assys_covered = 0
        
        for unit in self.subunit_set.all():
            if unit.checklist_set.all().count() > 0:
                n_units_covered += 1
        for assy in self.subassembly_set.all():
            if assy.checklist_set.all().count() > 0:
                n_assys_covered += 1


        if n_assys + n_units  != 0:
            return ((n_assys_covered + n_units_covered) / (n_assys + n_units)) * 100

        
class SubUnit(models.Model):
    unique_id = models.CharField(max_length=24, primary_key=True)
    unit_name = models.CharField(max_length=128)
    machine = models.ForeignKey("Machine", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.unit_name
    
class SubAssembly(models.Model):
    unique_id = models.CharField(max_length=24, primary_key=True)
    unit_name = models.CharField(max_length=128, verbose_name="Sub-Assembly")
    subunit = models.ForeignKey("SubUnit", null=True, on_delete=models.SET_NULL)
    machine = models.ForeignKey("Machine", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.unit_name

class Component(models.Model):
    unique_id = models.CharField(max_length=24, primary_key=True)
    component_name = models.CharField(max_length = 128)
    inventory_number = models.IntegerField(unique =True)
    machine = models.ForeignKey("Machine", null=True, on_delete=models.SET_NULL)
    subunit = models.ForeignKey("SubUnit", null=True, on_delete=models.SET_NULL)
    subassembly = models.ForeignKey("SubAssembly", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.component_name
