from __future__ import unicode_literals
from __future__ import division

from django.db import models

from datetime import timedelta
from django.utils import timezone

class Asset(models.Model):
    """
    Model that represents a company asset.

    #Should act as the Machine model base class
    Has a spares list relationship via a foreign key

    """
    asset_unique_id = models.CharField(max_length=32, unique=True)
    category = models.ForeignKey("common_base.Category")
    spares_list = models.ManyToManyField("Spares")

    def __str__(self):
        return self.asset_unique_id

class Spares(models.Model):
    """
    Represents an item that can replace some piece of equipment and can be retrieved from stores.

    Linked to spares using stock_id
    #relationship, all spares are machine components but not all components are spares.

    Fields: name, description, stock_id, category, quantity, reorder_level, reorder_quanity, last_order_price
    """
    
    name = models.CharField(max_length = 32)
    description = models.CharField(max_length= 128, null=True, blank=True)
    stock_id = models.CharField(max_length=32)
    category = models.ForeignKey("common_base.Category")
    quantity = models.IntegerField( default = 0)
    reorder_level = models.IntegerField(default = 0)
    reorder_quantity = models.IntegerField( default = 0)
    last_order_price = models.FloatField(default = 0.0)
    
    def __str__(self):
        return self.stock_id

class Plant(models.Model):
    """Used to distinguish main plant from sheet plant
    
    Might be deprecated soon. 
    """
    plant_name= models.CharField(max_length = 128)
    
    def __str__(self):
        return self.plant_name

class Machine(models.Model):
    """
    Will be related to an asset and use its attributes.
    Level one equipment.
    Parent : Plant
    Child  : Section

    Example:
    ========
    Topra                                 <-Machine
        +--Feed Section
            +--Vacuum system
                +--Vacuum pump assembly
                    +--10 kW Motor

    Properties:
    ===========
    n_units -returns the number of units
    n_breakdowns(today/weekly/monthly/sixmonths) - returns number of breakdowns over the period
    checklist_coverage - how many units and sections are covered by a checklist versus the total number of units and sections
    """
    machine_name = models.CharField(max_length=128)
    unique_id = models.CharField(max_length=24, primary_key=True)
    manufacturer = models.CharField(max_length=128)
    asset_data = models.ForeignKey("Asset", null=True, blank=True, verbose_name="Linked Asset Data")
    commissioning_date = models.DateField(blank = True, null=True)

    def __str__(self):
        return self.machine_name

    @property
    def n_units(self):
        return self.subunit_set.all().count()

    @property
    def n_breakdowns_today(self):
        yesterday = timezone.now() - timedelta(days=1)
        return self.workorder_set.filter(execution_date__gt = yesterday).count()


    @property
    def n_breakdowns_weekly(self):
        week = timezone.now() - timedelta(days=7)
        return self.workorder_set.filter(execution_date__gt = week).count()


    @property
    def n_breakdowns_monthly(self):
        month = timezone.now() - timedelta(days=30)
        return self.workorder_set.filter(execution_date__gt = month).count()


    @property
    def n_breakdowns_sixmonths(self):
        bi_ann = timezone.now() - timedelta(days=182)
        return self.workorder_set.filter(execution_date__gt = bi_ann).count()


    @property
    def checklist_coverage(self):
        checklists = self.checklist_set.all()
        n_units = self.subunit_set.all().count()
        n_sections = self.section_set.all().count()
        n_units_covered = 0
        n_sections_covered = 0
        
        for section in self.section_set.all():
            if section.checklist_set.all().count() > 0:
                n_sections_covered += 1
        for unit in self.subunit_set.all():
            if unit.checklist_set.all().count() > 0:
                n_units_covered += 1


        if n_sections + n_units  != 0:
            return ((n_sections_covered + n_units_covered) / (n_sections + n_units)) * 100

class Section(models.Model):
    """
    Level 2
    parent: Machine
    child : Subunit
    
    Example:
    =======
    Topra                                 
        +--Feed Section                 <-Section
            +--Vacuum system
                +--Vacuum pump assembly
                    +--10 kW Motor
    """
    
    unique_id = models.CharField(max_length=24, primary_key=True)
    section_name = models.CharField(max_length=64)
    machine= models.ForeignKey("Machine", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self. section_name


class SubUnit(models.Model):
    """
    Level 3
    parent : Section
    child  : SubAssembly

    Example:
    =======
    Topra                                 
        +--Feed Section                 
            +--Vacuum system            <-SubUnit
                +--Vacuum pump assembly
                    +--10 kW Motor
    """
    
    unique_id = models.CharField(max_length=24, primary_key=True)
    unit_name = models.CharField(max_length=128)
    machine = models.ForeignKey("Machine", null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey("Section", null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.unit_name
    
class SubAssembly(models.Model):
    """
    Level 4
    parent : Subunit
    child  : Component

    Example:
    =======
    Topra                                 
        +--Feed Section                 
            +--Vacuum system            
                +--Vacuum pump assembly <-Sub Assembly
                    +--10 kW Motor

    """
    unique_id = models.CharField(max_length=24, primary_key=True)
    unit_name = models.CharField(max_length=128, verbose_name="Sub-Assembly")
    subunit = models.ForeignKey("SubUnit", null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey("Section", null=True, on_delete=models.SET_NULL)
    machine = models.ForeignKey("Machine", null=True, on_delete=models.SET_NULL)
    

    def __str__(self):
        return self.unit_name

class Component(models.Model):
    """
    Level 5
    parent : SubAssembly
    child  : None
    
    closely related to spares

    Example:
    =======
    Topra                                 
        +--Feed Section                 
            +--Vacuum system
                +--Vacuum pump assembly
                    +--10 kW Motor      <-Component
    """
    unique_id = models.CharField(max_length=24, primary_key=True)
    component_name = models.CharField(max_length = 128)
    machine = models.ForeignKey("Machine", null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey("Section", null=True, on_delete=models.SET_NULL)
    subunit = models.ForeignKey("SubUnit", null=True, on_delete=models.SET_NULL)
    subassembly = models.ForeignKey("SubAssembly", null=True, on_delete=models.SET_NULL)
    spares_data=models.ForeignKey("Spares", null=True, blank=True, verbose_name="linked spares")

    
    def __str__(self):
        return self.component_name


class InventoryItem(models.Model):
    """
    Represents items retained in stock.

    Fields: serial_number, name, order_number, quantity, unit, order_date, category, supplier, unit_price, min_stock_level, reorder_quantity
    """

    serial_number = models.CharField(max_length= 32, primary_key=True)
    name = models.CharField(max_length= 32)
    order_number = models.CharField(max_length=32)
    quantity = models.IntegerField()
    unit = models.CharField(max_length= 32)
    order_date = models.DateField()
    category = models.ForeignKey("common_base.Category")
    supplier = models.CharField(max_length= 32)
    unit_price = models.FloatField()
    min_stock_level = models.IntegerField()
    reorder_quantity = models.IntegerField()

    def __str__(self):
        return self.name

class Order(models.Model):
    """
    Model representing customer order on which production calender is based.

    Fields: order_number, description, quantity, unit_price, manufacture_date, flute_profile(enum), liner(enum), layers(enum), delivery_date, customer, production_status(enum),delivery_status(enum)`
    
    """
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