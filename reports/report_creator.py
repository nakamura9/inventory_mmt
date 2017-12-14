import operator
import os
import datetime
import dateutil
from django.db.models import Q
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
from statistics import mean

from jobcards.models import PreventativeTask, WorkOrder
from checklists.models import Checklist
from common_base.utilities import filter_by_dates
from inv.models import Machine

class PlotFactory(object):
    def __init__(self, report):
        pass


class AbstractAvailabilityPlotFactory(object):
    def __init__(self, report):
        self.report = report        
        self.duration = (self.report.end_period - self.report.start_period).days
        self._base_path = os.path.join(os.getcwd(),"media")

    def preplot(self, *args):
        pass

    def postplot(self, *args):
        pass

    def plot(self):
        self.x = []
        self.xticks = []
        self.y = []
        self.ylabel = "Availability"

        if self.duration < 15:
            self.xlabel = "Days"
            self.plot_daily()
        elif self.duration < 56:
            self.xlabel = "Weeks"
            self.plot_weekly()
        else:
            self.xlabel = "Months"
            self.plot_monthly()

        dynamic_angle = len(self.x) * 4
        plt.title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.xticks(self.x, self.xticks, rotation=dynamic_angle)
        self.preplot()
        plt.plot(self.x, self.y, "-o", linewidth=5, markersize=10)
        plt.bar(self.x, self.y)
        self.postplot()
        plt.tight_layout()
        plt.savefig(self.path)
        plt.clf()
        return "/media/" + self.file_name

    def plot_daily(self):
        raise NotImplementedError()

    def plot_weekly(self):
        raise NotImplementedError()

    def plot_monthly(self):
        raise NotImplementedError()


class MultipleMachineAvailabilityPlotFactory(AbstractAvailabilityPlotFactory):
    def __init__(self, report):
        super(MultipleMachineAvailabilityPlotFactory, self).__init__(report)
        self.machines = self.report.machine.all()
        if self.machines.count() == 0:
            self.machines = Machine.objects.all()
        self.title = "Availability of all machines by machine"
        self.file_name = "machines_availability"+ self.report.end_period.strftime("%Y%m%d") + ".png"
        self.path = os.path.join(self._base_path, self.file_name)

    def preplot(self):
        plt.xlabel("Machine")

    def plot_(self):
        """this method is common between all periods"""
        count = 1
        for mech in self.machines:
            self.xticks.append(mech.machine_name)
            self.x.append(count)
            self.y.append(mech.availability_over_period(self.report.start_period, self.report.end_period))
            count +=1

    def plot_daily(self):
        self.plot_()

    def plot_weekly(self):
        self.plot_()

    def plot_monthly(self):
        self.plot_()

class FactoryEquipmentAvailabilityPlotFactory(AbstractAvailabilityPlotFactory):
    def __init__(self, report):
        super(FactoryEquipmentAvailabilityPlotFactory, self).__init__(report)
        self.machines = self.report.machine.all()
        if self.machines.count() == 0:
            self.machines = Machine.objects.all()
        self.title = "Availability of all machines by date"
        self.file_name = "all_machines_availability"+ self.report.end_period.strftime("%Y%m%d") + ".png"
        self.path = os.path.join(self._base_path, self.file_name)

    def plot_daily(self):
        # maybe can be abstracted further, the only difference is the length of 
        # the y values
        for i in range(self.duration):
            day = self.report.start_period + datetime.timedelta(days=i)
            self.xticks.append(day.strftime("%d/%m/%Y"))
            self.x.append(i+1)
            self.y.append(mean(mech.availability_on_date(day) \
                        for mech in self.machines ))

    def plot_weekly(self):
        weeks = int(self.duration / 7)#make it round up and down!
        curr_date = self.report.start_period
        for i in range(weeks):
            self.x.append(i+1)
            self.xticks.append("Week " + str(i+1))
            next_date = curr_date + datetime.timedelta(days=7)
            self.y.append(mean(mech.availability_over_period(curr_date, next_date) for mech in self.machines ))
            curr_date = next_date
            

    def plot_monthly(self):
        months = self.report.end_period.month - self.report.start_period.month
        curr_date = self.report.start_period
        if not isinstance(curr_date, datetime.date):
            curr_date = curr_date.date()
        for i in range(months):
            self.x.append(i+1)
            self.xticks.append("Month " + str(i+1))
            next_date = curr_date + dateutil.relativedelta.relativedelta(months=1)
            self.y.append(mean(mech.availability_over_period(curr_date, next_date) for mech in self.machines ))
            curr_date = next_date


class MachineAvailabilityPlotFactory(AbstractAvailabilityPlotFactory):
    def __init__(self, report, machine):
        super(MachineAvailabilityPlotFactory, self).__init__(report)
        self.machine = machine
        self.title = self.machine.machine_name
        self.file_name = self.machine.machine_name + "_availability_" +self.report.end_period.strftime("%Y%m%d") + ".png"
        self.path = os.path.join(self._base_path, self.file_name)



    def plot_daily(self):
        for i in range(self.duration):
            day = self.report.start_period + datetime.timedelta(days=i)
            self.xticks.append(day.strftime("%d/%m/%Y"))
            self.x.append(i+1)
            self.y.append(self.machine.availability_on_date(day))

    def plot_weekly(self):
        weeks = int(self.duration / 7)#make it round up and down!
        curr_date = self.report.start_period
        for i in range(weeks):
            self.x.append(i+1)
            self.xticks.append("Week " + str(i+1))
            next_date = curr_date + datetime.timedelta(days=7)
            self.y.append(self.machine.availability_over_period(curr_date, next_date))
            curr_date = next_date
            

    def plot_monthly(self):
        months = self.report.end_period.month - self.report.start_period.month
        curr_date = self.report.start_period
        if not isinstance(curr_date, datetime.date):
            curr_date = curr_date.date()
        for i in range(months):
            self.x.append(i+1)
            self.xticks.append("Month " + str(i+1))
            next_date = curr_date + dateutil.relativedelta.relativedelta(months=1)
            self.y.append(self.machine.availability_over_period(curr_date, next_date))
            curr_date = next_date



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
    