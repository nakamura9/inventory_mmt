import datetime
from inv.models import Order
from jobcards.models import PlannedJob
from checklists.models import Checklist
import calendar


class Day(object):
    def __init__(self, date):
        """Day object that stores a reference of its date as week as 
        other features"""
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        assert(isinstance(date, datetime.date))
        
        self.date = date
        self.weekday = (date.weekday(), day_names[date.weekday()])
        self.agenda = []
    

    @property
    def is_weekend(self):
        #dont add checklists over the weekend
        if self.date.weekday() not in [5, 6]:
            return False
        else: return True 


    def get_agenda(self):
        """performed by subclasses"""
        raise NotImplementedError()


    def sort_agenda(self):
        raise NotImplementedError()
        

class ProductionDay(Day):
    def get_agenda(self):
        """Production days look out for manufacture days and 
        delivery dates"""
        self.agenda = ["%s: %s" %(order.order_number, order.description) \
                     for order in Order.objects.filter(manufacture_date = self.date)]
        
        for order in Order.objects.filter(delivery_date = self.date):
            self.agenda.append("%s: %s" %(order.order_number, order.description))


class MaintenanceDay(Day):
    def get_agenda(self):
        """Maintenance days look out for planned jobs and checklists"""

        self.agenda = ["%s: %s" %(job.resolver, job.description) \
                        for job in PlannedJob.objects.filter(scheduled_for = self.date)]
        for check in Checklist.objects.all():
            if check.is_open:
                if check.frequency == "daily" and not self.is_weekend:
                    self.agenda.append("%s: %s" %(check.resolver, check.title))
                
                if check.frequency != "daily" and check.creation_date.weekday() == \
                    self.weekday[0]:
                    self.agenda.append("%s: %s" %(check.resolver, check.title))
                    

class Week(object):
    def __init__(self, year, month, week, day):
        self.days = []
        self.Day = day
        self.week_agenda = []
        self.year = year
        self.month = month
        self.week = week


    @property
    def first(self):
        """first day of the month"""
        return datetime.date(self.year, self.month, 1)
    

    def get_week_days(self):
        
        _calendar = calendar.Calendar()
        self.days=_calendar.monthdatescalendar(self.year, self.month)[self.week]
        

    def get_week_agenda(self):
        if self.days == []:
            self.get_week_days()
        for day in self.days:
            _day =self.Day(day)
            _day.get_agenda()
            self.week_agenda.append(_day)        
        

class Month(object):
    def __init__(self, year, month, day):
        self.days = None
        self.Day = day
        self.month_matrix = []
        self.year = year
        self.month = month


    def get_days(self):
        _calendar = calendar.Calendar()
        self.days=_calendar.monthdatescalendar(self.year, self.month)


    def get_month_agenda(self):
        if self.days == None:
            self.get_days()

        
        for row in self.days:
            self.month_matrix.append([])
            for col in row:
                day = self.Day(col)
                day.get_agenda()
                self.month_matrix[-1].append(day)
