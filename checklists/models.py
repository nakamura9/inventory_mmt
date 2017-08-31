from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import datetime
from common_base.utilities import time_choices


def now():
    return datetime.datetime.now().strftime("%H%M")

class Checklist(models.Model):

    def __str__(self):
        return self.title
    
    mapping =  {"daily": 1,
        "weekly": 7,
        "fortnightly": 14,
        "monthly": 30,
        "quarterly": 90,
        "bi-annually": 180,
        "yearly": 360}


    title = models.CharField(max_length= 64, 
                            unique=True, primary_key=True)
    creation_date = models.DateField()
    last_completed_date = models.DateField(blank = True, null=True)
    estimated_time= models.DurationField(choices = [] \
                         + time_choices("00:05:00", "00:35:00", "00:05:00") \
                         + time_choices("01:00:00", "08:01:00", "01:00:00"))
    start_time = models.TimeField(choices=time_choices(
                                            "06:30:00", "17:30:00", "00:30:00"))
    machine = models.ForeignKey("inv.Machine")
    section = models.ForeignKey("inv.Section", 
                null=True, on_delete=models.SET_NULL)
    subunit = models.ForeignKey("inv.SubUnit", 
                null=True, on_delete=models.SET_NULL)
    subassembly = models.ForeignKey("inv.SubAssembly", 
                null=True, on_delete=models.SET_NULL)
    resolver = models.ForeignKey("common_base.Account")
    category = models.CharField(max_length = 64,
                    choices=[("electrical", "Electrical"),
                    ("mechanical", "Mechanical")])
    frequency = models.CharField(max_length = 16, 
                        choices = [("daily", "Daily"),
                                    ("weekly", "Weekly"),
                                    ("fortnightly", "Every 2 weeks"),
                                    ("monthly", "Monthly"),
                                    ("quarterly", "Every 3 Months"),
                                    ("bi-annually", "Every 6 Months"), 
                                    ("yearly", "Yearly")])
    on_hold = models.BooleanField(default=False)
    comments = models.ManyToManyField("common_base.Comment")
    tasks = models.ManyToManyField("common_base.Task")
    
    @property
    def is_open(self):
        if self.on_hold:
            return False
        
        if self.last_completed_date is None:
            return True
        else:
            delta = datetime.date.today() - self.last_completed_date

        if delta.days > self.mapping[self.frequency]:
            return True
        else:
            return False
    
    @property
    def next(self):
        "determine the next date for a checklist"
        return self.last_completed_date + \
            datetime.timedelta(days=self.mapping[self.frequency])

    @property
    def get_type(self):
        return "checklist"
