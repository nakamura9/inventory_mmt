from __future__ import unicode_literals
from __future__ import division

from django.db import models

from datetime import timedelta
from django.utils import timezone

        
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

class Section(models.Model):
    unique_id = models.CharField(max_length=24, primary_key=True)
    section_name = models.CharField(max_length=64)
    machine= models.ForeignKey("Machine", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self. section_name


class SubUnit(models.Model):
    unique_id = models.CharField(max_length=24, primary_key=True)
    unit_name = models.CharField(max_length=128)
    machine = models.ForeignKey("Machine", null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey("Section", null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.unit_name
    
class SubAssembly(models.Model):
    unique_id = models.CharField(max_length=24, primary_key=True)
    unit_name = models.CharField(max_length=128, verbose_name="Sub-Assembly")
    subunit = models.ForeignKey("SubUnit", null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey("Section", null=True, on_delete=models.SET_NULL)
    machine = models.ForeignKey("Machine", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.unit_name

class Component(models.Model):
    unique_id = models.CharField(max_length=24, primary_key=True)
    component_name = models.CharField(max_length = 128)
    machine = models.ForeignKey("Machine", null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey("Section", null=True, on_delete=models.SET_NULL)
    subunit = models.ForeignKey("SubUnit", null=True, on_delete=models.SET_NULL)
    subassembly = models.ForeignKey("SubAssembly", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.component_name


class InventoryItem(models.Model):
    serial_number = models.CharField(max_length= 32, primary_key=True)
    name = models.CharField(max_length= 32)
    order_number = models.CharField(max_length=32)
    quantity = models.IntegerField()
    unit = models.CharField(max_length= 32)
    order_date = models.DateField()
    category = models.ForeignKey("inv.Category")
    supplier = models.CharField(max_length= 32)
    unit_price = models.FloatField()
    min_stock_level = models.IntegerField()
    reorder_quantity = models.IntegerField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length= 32, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class Order(models.Model):
    def __init__(self, *args, **kwargs):
        self.actual_delivery_epoch = None
        super(Order,self).__init__(*args,**kwargs)

    order_number = models.CharField(max_length= 32, primary_key=True)
    description = models.CharField(max_length=64)
    quantity =models.IntegerField()
    unit_price = models.FloatField()
    manufacture_date = models.DateField()
    flute_profile = models.CharField(max_length=1, choices=[
        ("a", "A Flute"),
        ("b", "B Flute"),
        ("c", "C Flute"),
    ])
    liner = models.CharField(max_length=32, choices=[
        ("kraft", "Kraft"),
    ])
    layers = models.IntegerField(choices = [
        (1, "Single Wall Board"),
        (2, "Double Wall Board"),
    ]) 
    delivery_date = models.DateField()
    customer = models.CharField(max_length= 32)
    production_status = models.CharField(max_length=32, choices=[
        ("planned", "Planned"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed")
    ])
    delivery_status = models.CharField(max_length=16, choices = (
        ("storage", "In Storage"),
        ("transit", "In Transit"),
        ("delivered", "Delivered")
    ))

    def save(self, *args, **kwargs):
        if self.delivery_status == "delivered":
            self.actual_delivery_epoch = timezone.now().date()
        super(Order, self).save(*args, **kwargs)

    @property
    def actual_delivery_date(self):
        if self.delivery_status != "delivered":
            return "Undelivered"
        else:
            return self.actual_delivery_epoch.strftime("%d/%m/%Y")

    def __str__(self):
        return "%s: %s" % (self.order_number, self.description)