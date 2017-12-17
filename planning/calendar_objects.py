import datetime
import calendar
from django.db.models import Q
from inv.models import Order, Machine
from jobcards.models import PreventativeTask
from checklists.models import Checklist


class Day(object):
    def __init__(self, date, filters = {}, include = []):
        """Day object that stores a reference of its date as well as 
        other features
        The filters are used to narrow database queries and the included argument limits. 
        The classes used to construct the queries."""

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        assert(isinstance(date, datetime.date))
        self.date = date
        self.filters = {}
        for filter in filters:
            if filters[filter]:
                self.filters[filter] = filters[filter]#makes sure no filter passes None to a query
        
        self.include = [i.lower() for i in include]
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
        
class ProductionElement(object):
    def __init__(self, machine, date):
        """instantiated with a machine and a date abstraction used to
        facilitate advanced functionality within the calendar"""
        self.machine = machine
        if isinstance(date, datetime.datetime):
            self.date = date.date()
        else:
            self.date = date

        self.run_data = self.machine.run_on_date(self.date)

    @property
    def planned_downtime(self):
        p_tasks = self.machine.preventativetask_set.filter(scheduled_for=self.date)
        if p_tasks.count() > 0:
            return sum((i.estimated_downtime.seconds for i in p_tasks)) / 3600.0 

        return 0.0


    @property
    def running_hours(self):
        return self.run_data.run_hours

    @property
    def net_up_time(self):
        return self.running_hours - self.planned_downtime

class ProductionDay(Day):
    """Lists events associated with orders"""

    def get_agenda(self):
        """Production days look out for manufacture days and 
        delivery dates. 
        NB Production day ignores include as there is only one model involved"""
        self.agenda = [ProductionElement(mech, self.date) for mech in Machine.objects.all() if mech.is_running_on_date(self.date)]
        
                
        
    @property
    def run_count(self):
        return len(self.agenda)

class MaintenanceDay(Day):
    """Lists events based on preventativeTasks and Checklists"""
    

    @property
    def checklist_count(self):
        return len([item for item in self.agenda if isinstance(item, Checklist)])

    @property
    def job_count(self):
        return len([item for item in self.agenda if isinstance(item, PreventativeTask)])
    
    def get_agenda(self):
        """Maintenance days look out for planned jobs and checklists"""
        self.agenda = []
        if "checks" in self.include:
            for check in Checklist.objects.all().filter(**self.filters):
                if check.is_open and (self.date > check.creation_date):
                    if check.frequency == "daily" and not self.is_weekend:
                        self.agenda.append(check)
                    
                    if check.frequency != "daily" and check.creation_date.weekday() == \
                        self.weekday[0]:
                        self.agenda.append(check)
        
        
        if "jobs" in self.include:
            if self.filters.get("resolver", None):
                self.filters["assignments"] = self.filters["resolver"]
                del self.filters["resolver"]
        
            self.agenda += [job for job in \
                        PreventativeTask.objects.filter(
                            scheduled_for = self.date).filter(
                                **self.filters
                            )]
                    

class Week(object):
    """
    A generic week class that takes a year month and week of the ni\\month 
    and returns a 7 day week starting from moday. It is generic in the sense
    that it can handle production or maintenance weeks by specifying the type
    of day the object deals with
    """
    def __init__(self, year, month, week, day, filters={}, include=[]):
        self.days = []
        self.day_type = day
        self.week_agenda = []
        self.year = year
        self.month = month
        self.week = week
        self.filters = filters
        self.include = include


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
            _day =self.day_type(day, filters = self.filters,
                                include = self.include)
            _day.get_agenda()
            self.week_agenda.append(_day)        
        

class Month(object):
    """
    A generic month class that takes a year and month 
    and returns a month agenda as a 2 dimensional matrix of individual days. 
    It is generic in the sense that it can handle production or maintenance 
    months by specifying the type of day the object deals with
    """
    def __init__(self, year, month, day, filters={}, include=[]):
        self.days = None
        self.day_type = day
        self.month_agenda = []
        self.year = year
        self.filters = filters
        self.include = include
        self.month = month


    def get_dates(self):
        _calendar = calendar.Calendar()
        self.days=_calendar.monthdatescalendar(self.year, self.month)


    def get_month_agenda(self):
        if self.days == None:
            self.get_dates()

        
        for row in self.days:
            self.month_agenda.append([])
            for col in row:
                day = self.day_type(col, filters = self.filters, 
                                        include = self.include)
                day.get_agenda()
                self.month_agenda[-1].append(day)

        

                