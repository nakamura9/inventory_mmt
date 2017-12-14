from __future__ import unicode_literals
from __future__ import division



from datetime import timedelta
import datetime

from django.utils import timezone
from django.db import models
from django.db.models import Q



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
    
    name = models.CharField(max_length = 32)#make unique
    description = models.CharField(max_length= 128, null=True, blank=True)
    stock_id = models.CharField(max_length=32, unique=True)
    category = models.ForeignKey("common_base.Category", null = True)
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



class RunData(models.Model):
    start_date = models.DateField()
    run_days = models.IntegerField()
    run_hours = models.FloatField()
    
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    #override save method to specify run days
    #add specific days

    #write property that gets total run hours  for a given period
    
    def is_running(self, day):
        if isinstance(day, datetime.datetime):
            day = day.date()
        if not day >= self.start_date:
            return False

        run_days = {1:self.monday,
                    2:self.tuesday,
                    3:self.wednesday,
                    4:self.thursday,
                    5:self.friday,
                    6:self.saturday,
                    0:self.sunday}
        
        try:
            #Slow and dirty!
            filter = RunData.objects.filter(machine=self.machine_set.first()).order_by("start_date")
            next =self.get_next_by_start_date()
            if not next in filter:
                next = None 
        except:
            next = None
            
        if not next:
            return run_days[day.weekday()]

        else:
            if day <= next.start_date:
                return run_days[day.weekday()]
        
        return False

    @property
    def total_run_hours(self):
        try:
            next = self.get_next_by_start_date().start_date
            if next > datetime.date.today():
                next = datetime.date.today()
        except:
            next = datetime.date.today()

        if next > self.start_date:
            delta = next - self.start_date
        else: 
            return 0

        weeks = int(delta.days / 7)

        rem = delta.days - (weeks * 7) 

        if rem > self.run_days: 
            days  = self.run_days
        else:
            days = rem

        return (weeks * self.run_days * self.run_hours) + (days * self.run_hours)


    

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

    Methods:
    ========
    availability_over_period
    planned_downtime_over_period
    unplanned_downtime_over_period
    run_hours_over_period
    ***
    """

    machine_name = models.CharField(max_length=128)
    unique_id = models.CharField(max_length=24, primary_key=True)
    manufacturer = models.CharField(max_length=128)
    asset_data = models.ForeignKey("Asset", null=True, blank=True, verbose_name="Linked Asset Data")
    commissioning_date = models.DateField(blank = True, null=True)
    run_data = models.ManyToManyField("RunData")

    def availability_over_period(self, start, stop=datetime.date.today()):
        """used to calculate the machines availability over a given period"""
        downtime = self.unplanned_downtime_over_period(start, stop)
        available_time = self.run_hours_over_period(start, stop)

        return ((available_time-downtime)/ available_time) * 100

    def planned_downtime_over_period(self, start, stop=datetime.date.today()):
        """used to calculate downtime over a period of time"""
        p_tasks = self.preventativetask_set.filter(Q(completed_date__gte=start) & Q(completed_date__lte=stop))
        if p_tasks.count() > 0:
            return sum((i.actual_downtime.seconds for i in p_tasks)) / 3600.0 

        return 0.0

    def unplanned_downtime_over_period(self, start, stop=datetime.date.today()):
        """used to calculate downtime over a period due to breakdowns"""
        wos = self.workorder_set.filter(Q(completion_date__gte=start) & Q(completion_date__lte=stop))
        if wos.count() > 0:
            return sum((i.downtime.seconds for i in wos)) / 3600.0
        return 0

    def run_hours_over_period(self, start, end):
        """calculate run data for a period of time.
        NB Very inefficient!
        """
        period = (end - start).days
        if period == 0:
            raise ValueError("The period is less than one day use 'run_on_date' instead")
        curr_day = start
        total_hours = 0
        for i in range(period):
            curr_day = curr_day + datetime.timedelta(days=i)
            curr_run = self.run_on_date(curr_day)
            if curr_run:
                if curr_run.is_running(curr_day):
                    total_hours += curr_run.run_hours
        #need to come up with way of approximating run_time
        if total_hours == 0:
            return 24 * period
        
        return total_hours

    def availability_on_date(self, date):
        """Returns the machine availability for that date"""
        breakdowns = self.workorder_set.filter(execution_date=date)
        if breakdowns.count() > 0:
            downtime = sum(i.downtime.seconds for i in breakdowns) /3600.0
        else: 
            downtime = 0.0
        run_data = self.run_on_date(date)
        
        if run_data:
            available_time = run_data.run_hours
            return ((available_time - downtime)/ available_time) * 100
        
        else:
            return 100

    def run_on_date(self, date):
        """returns the run data for the stated date
        
        Input
        -----
        date object
        
        Output
        RunData object or None.
        
        """
        _run_data = self.run_data.filter(start_date__lte=date)
        if _run_data.count() > 0:
            return _run_data.latest("start_date")
        return None

    def is_running_on_date(self, date):
        data = self.run_on_date(date)
        if data:
            return data.is_running(date)
        else: return False

    @property
    def current_run(self):
        self.run_on_date(datetime.date.today())

    @property
    def total_time(self):
        if self.run_data.count() == 0:
            return 0.0
        first = self.run_data.all().order_by("start_date")[0]
        return self.total_run_time_over_period(first.start_date)

    def total_run_time_over_period(self, start, end=datetime.date.today()):
       #for time defined within the period
        _run_data = self.run_data.filter(models.Q(start_date__gte=start) & \
                                            models.Q(start_date__lte=end)).order_by("start_date")

        #for time defined before the period but continuing through it 
        def initial_run_times(obj, start):
            older = obj.run_data.filter(start_date__lt=start)
            if older.count() > 0:
                closest = older.latest("start_date")
                next = closest.get_next_by_start_date()
                days = (start - next.start_date).days
                
                weeks = int(days/ 7)
                rem_days = days % 7
                if rem_days > closest.run_days:
                    rem_hours = closest.run_days * closest.run_hours
                else:
                    rem_hours = rem_days * closest.run_hours
            
                return (weeks * closest.run_days * closest.run_hours) + rem_hours

            else: return 0

        first_hours = initial_run_times(self, start)
        
        if _run_data.count() == 0:
            total = 0
        else: 
            total = sum((r.total_run_hours for r in _run_data))
        
        return first_hours + total


    def __str__(self):
        return self.machine_name

    @property
    def recent_run_data(self):
        return self.run_data.all().order_by("start_date")[:5]

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
    spares_data=models.ManyToManyField("Spares",verbose_name="linked spares")

    
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