from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import datetime


def now():
    return datetime.datetime.now().strftime("%H%M")


class Comment(models.Model):
    checklist = models.ForeignKey("checklist")
    author = models.ForeignKey("common_base.Account")
    content = models.CharField(max_length=1024)
    authored_date = models.DateField(default = timezone.now)


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
    estimated_time= models.CharField(max_length=4, choices = [
                ("00%d" % i, "00%d" % i)for i in range(10, 60, 5)] \
                + [("0%d00" % i, "0%d00" % i) for i in range(1, 8)], 
                default = now)
    start_time = models.CharField(max_length = 5, choices = [
                ("0%d00" % i, "%d:00" % i) for i in range(6, 9)] \
                 + [("%d00" % i, "%d:00" % i) for i in range(10, 17)] )
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
    frequency = models.CharField(max_length = 64, 
                        choices = [("daily", "Daily"),
                                    ("weekly", "Weekly"),
                                    ("fortnightly", "Every 2 weeks"),
                                    ("monthly", "Monthly"),
                                    ("quarterly", "Every 3 Months"),
                                    ("bi-annually", "Every 6 Months"), 
                                    ("yearly", "Yearly")])
    on_hold = models.BooleanField(default=False)

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

class Task(models.Model):
    checklist = models.ForeignKey("CheckList")
    task_number = models.IntegerField()
    description = models.CharField(max_length = 1024, unique=True)
    
    