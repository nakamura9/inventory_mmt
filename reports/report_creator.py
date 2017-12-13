import operator
import os
import datetime
import dateutil
from django.db.models import Q
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt

from jobcards.models import PreventativeTask, WorkOrder
from checklists.models import Checklist
from common_base.utilities import filter_by_dates
from inv.models import Machine

class PlotFactory(object):
    pass


def list_jobs(report):
    """applies numerous filters to the data to match the requirements of the report

    The data is first filtered by dates 
    then its filtered by the equipment supplied to the report
    
    Input
    ------
    report object

    Output 
    ------

    3 element tuple of preventative tasks, work_orders and checklists"""

    p_tasks = filter_by_dates(PreventativeTask.objects.all(),
                                report.start_period.strftime("%m/%d/%Y"),
                                report.end_period.strftime("%m/%d/%Y"))
    wos = filter_by_dates(WorkOrder.objects.all(), 
                            report.start_period.strftime("%m/%d/%Y"),
                                report.end_period.strftime("%m/%d/%Y"))
    checks = filter_by_dates(Checklist.objects.all(), 
                            report.start_period.strftime("%m/%d/%Y"),
                                report.end_period.strftime("%m/%d/%Y"))

    q_objs = []

    if report.machine.count() >0:
        q_objs += [Q(machine=mech) for mech in report.machine.all()]

    if report.component.count() >0:
        q_objs += [Q(component=c) for c in report.component.all()]

    if report.subunit.count() >0:
        q_objs += [Q(subunit=s) for s in report.subunit.all()]
    
    if report.subassembly.count() >0:
        q_objs += [Q(subassembly=sa) for sa in report.subassembly.all()]
    
    if report.section.count() >0:
        q_objs += [Q(section=s) for s in report.section.all()]

    if len(q_objs) > 0:
        import copy
        w_objs = copy.deepcopy(q_objs)
        p_tasks = p_tasks.filter(reduce(operator.or_, q_objs))
        
        
        wos = wos.filter(reduce(operator.or_, w_objs))
        checks = checks.filter(reduce(operator.or_, q_objs))

    return p_tasks, wos, checks
    #filter by date
    #filter by equipment
    
def machine_downtime(machine, start, stop):
    """returns downtime in hours"""
    breakdowns = WorkOrder.objects.filter(Q(machine=machine) & Q(completion_date__gte=start) & Q(completion_date__lte=stop))
    if breakdowns.count == 0:
        return 0.0
    return float(sum((i.downtime.seconds for i in breakdowns if i.actual_labour_time))) / 3600.0

def machine_planned_time(machine, start, stop):
    """returns planned time in hours """
    p_tasks = PreventativeTask.objects.filter(Q(machine=machine) & Q(completed_date__gte=start) & Q(completed_date__lte=stop))

    if p_tasks.count() == 0:
        return 0.0
    return float(sum((i.actual_downtime.seconds for i in p_tasks if i.actual_downtime))) / 3600.0

#
def daily_availability(mech, date):
    """returns the availability for the day"""
    down_time = machine_downtime(mech, date, date)
    _run_data = mech.run_on_date(date)
    if _run_data:
        available_time =  _run_data.run_hours
    else:
        #average time !!!
        available_time = 12

    return ((available_time - down_time) / available_time) * 100
    
def monthly_availability(mech, date):
    """supply the first of the month"""
    next_month = date +dateutil.relativedelta.relativedelta(months =1)
    downtime = machine_downtime(mech, date, next_month)
    available_time = mech.total_run_time_over_period(date, next_month)
    
    if available_time ==  0:
        available_time = 240

    return ((available_time - downtime) / available_time) * 100

def weekly_availability(mech, date):
    """supply the first day of the week"""
    next_week = date +dateutil.relativedelta.relativedelta(weeks=1)
    down_time = machine_downtime(mech, date, next_week)
    available_time = mech.total_run_time_over_period(date, next_week)
    
    #so as to avoid zero division errors
    if available_time ==  0:
        available_time = 60

    return ((available_time - down_time) / available_time) * 100


def plot_availability_for_machine_over_period(report, mech):
    duration = report.end_period - report.start_period
    availability = []

    if duration.days < 15:
        days = []
        for i in range(duration.days):
            
            day = report.start_period + datetime.timedelta(days=i)
            availability.append(daily_availability(mech, day))
            days.append(day.strftime("%m/%d/%Y"))
    
        print availability
        plt.title(mech.machine_name)
        plt.xlabel("Days")
        plt.ylabel("Availability")
        x=[i for i in range(duration.days)]
        plt.xticks(x, days, rotation=45)
        plt.bar(x, availability)
        plt.tight_layout()
        path = os.path.join("reports", "static", "report_figs")
        plt.savefig(os.path.join(path, str(report.pk) +"_"+ str(mech.pk) +"days.png"))

    elif duration.days < 56:
        weeks = int(duration.days / 7)
        for i in range(weeks): 
            _week = report.start_period + datetime.timedelta(weeks = i)
            availability.append(weekly_availability(mech, _week))


        print availability
        plt.title(mech.machine_name)
        plt.xlabel("Week #")
        plt.ylabel("Availability")
        x=[i for i in range(weeks)]
        plt.bar(x, availability)
        plt.tight_layout()
        path = os.path.join("reports", "static", "report_figs")
        plt.savefig(os.path.join(path, str(report.pk) +"_"+ str(mech.pk) +"weeks.png"))

    else: 
        months = report.end_period.month - report.start_period.month
        for i in range(months):
            next_month = report.start_period + dateutil.relativedelta.relativedelta(month=i)
            print next_month
            print report.start_period
            try:
                next = report.start_period + next_month
            except:
                next = report.start_period
            availability.append(monthly_availability(mech, next))    

        print availability
        plt.title(mech.machine_name)
        plt.xlabel("Month")
        plt.ylabel("Availability")
        x=[i for i in range(months)]
        plt.bar(x, availability)
        plt.tight_layout()
        path = os.path.join("reports", "static", "report_figs")
        plt.savefig(os.path.join(path, str(report.pk) +"_"+ str(mech.pk) +"months.png"))

def plot_availability_by_machine(report):
    #collect all the machines
    #calculate run time for the period
    #calculate all the planned maintenance on the machines
    #subtract planned from run time
    #calculate ratio of runtime to downtime for each machine
    _set = report.machine.all()

    if _set.count() == 0:
        _set = Machine.objects.all()
        
    mechs = [i.machine_name for i in _set]
    available_time = [i.total_run_time_over_period(report.start_period, report.end_period) for i in _set]
    down_time = [machine_downtime(i, report.start_period, report.end_period) for i in _set]
    x =[i for i in range(len(mechs))]
    
    availability = []
    for i in x:
        if available_time[i] == 0.0:
            availability.append(0)
        else:
            availability.append(((available_time[i]- down_time[i]) / available_time[i]) * 100) 
    
    plt.xlabel("Machine")
    plt.ylabel("Availability")
    plt.xticks(x, mechs, rotation=45)
    plt.bar(x, availability)
    plt.tight_layout()
    path = os.path.join("reports", "static", "report_figs")
    plt.savefig(os.path.join(path, "av.png"))


def plot_downtime_by_machine(report):
    _set = report.machine.all()
    if _set.count() == 0:
        _set = Machine.objects.all()
        
    mechs = [i.machine_name for i in _set]
    down_time = [machine_downtime(i, report.start_period, report.end_period) for i in _set]
    x =[i for i in range(len(mechs))]
    plt.ylabel("Downtime(Hours)")
    plt.xlabel("Machine")
    
    plt.xticks(x, mechs, rotation=45)
    plt.bar(x, down_time)
    plt.tight_layout()
    path = os.path.join( "reports", "static", "report_figs")
    plt.savefig(os.path.join(path, "test.png"))
