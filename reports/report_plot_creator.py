"""
Contains all the plotting related classes used in reports

PlotCreatorFactory  - class that selects which plot factory will create plots
                      for a given report

PlotFactory Objects - these classes use report information to select execute 
                      plotting operations on the report object supplied. can create one or more graphs and store their urls in a plot_urls dict 

Plotter Objects     - these are responsible for plotting one and only one graph 
                      based on the report and parameters supplied by the plot factory
"""
import os
import datetime
import dateutil
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
from statistics import mean

from inv.models import Machine,Section, SubAssembly, SubUnit, Component
from jobcards.models import WorkOrder, PreventativeTask
from django.db.models import Q


class PlotCreatorFactory(object):
    """Class that returns a plotting object for a report based on the scope of a report provided"""
    def __init__(self, report):
        self.report = report

    def create_plotter(self):
        """uses a scopes mapping to return an appropriate PlotFactory instance"""
        scopes = {"maintenance_review": MaintenanceReviewPlotFactory,
                "breakdown": BreakdownPlotFactory,
                "maintenance_plan": MaintenancePlanPlotFactory,
                "weak_point": WeakPointPlotFactory,
                "spares_usage": SparesUsagePlotFactory,
                "spares_requirements": SparesRequirementsPlotFactory,
                }
        
        return scopes[self.report.scope](self.report)


class AbstractPlotFactory(object):
    """abstract class for defining the PlotFactory interface
    Input
    ======
    Report Object
    
    Output
    =======
    plot_urls - dictionary of report plot strings
    
    Methods
    ========
    generate_plot_urls() - uses the report object to select which plots to create and what quantity"""

    def __init__(self, report, *args):
        self.report = report
        self.plot_urls = {}

    def generate_plot_urls(self):
        raise NotImplementedError()


class WeakPointPlotFactory(AbstractPlotFactory):
    """Weak point analysis report plot factory"""
    def __init__(self, report, reporter):
        self.report = report
        self.reporter = reporter
        self.plot_urls = {}
        
    def machine_plot(self):
        plotter = MachineBreakdownFrequencyDowntimePlotter(self.report)
        self.plot_urls['machine'] = plotter.plot()

    def section_plot(self, mech):
        plotter =BreakdownFrequencyDowntimePlotter(self.report, "section",mech)
        return plotter.plot()

    def component_plot(self, mech):
        plotter =BreakdownFrequencyDowntimePlotter(self.report, "component", mech)
        return plotter.plot()


    def generate_plot_urls(self):
        if len(self.report.equipment_list) > 1:
            self.machine_plot()
    
        sections = []
        components = []
        for mech in self.report.machine.all():
            sections.append(self.section_plot(mech))
            components.append(self.component_plot(mech))
        self.plot_urls["sections"] = sections
        self.plot_urls["components"] = components


class SparesRequirementsPlotFactory(AbstractPlotFactory):
    def generate_plot_urls(self):
        pass


class SparesUsagePlotFactory(AbstractPlotFactory):
    def generate_plot_urls(self):
        pass


class BreakdownPlotFactory(AbstractPlotFactory):

    def combined_frequency_plot(self):
        plotter = CombinedBreakdownFrequencyPlotter(self.report)
        self.plot_urls["breakdowns"] = plotter.plot()

    def combined_downtime_plot(self):
        plotter = CombinedDowntimePlotter(self.report)
        self.plot_urls["downtime"] = plotter.plot()
    
    def individual_frequency_plot(self, e):
        plotter = IndividualBreakdownFrequencyPlotter(self.report, e)
        return plotter.plot()

    def comparative_plot(self, e):
        plotter = PreventativeVsBreakdownMaintenancePlotter(self.report, e)
        return plotter.plot()
        

    def generate_plot_urls(self):
        if len(self.report.equipment_list) > 1:
            self.combined_frequency_plot()
            self.combined_downtime_plot()

        self.plot_urls.update({"breakdowns_epoch": [],"comparative_plots": []})
        for e in self.report.equipment_list:
            self.plot_urls["breakdowns_epoch"].append(
                self.individual_frequency_plot(e))
            self.plot_urls["comparative_plots"].append(
                self.comparative_plot(e))


class MaintenanceReviewPlotFactory(AbstractPlotFactory):
    """Takes a report and returns a dictionary of media urls based on the context of the report"""

    def machines_availability_plot(self, machine):
        plotter = MachineAvailabilityPlotter(self.report, machine)
        return plotter.plot()
    
    def multiple_machines_plot(self):
        plotter = MultipleMachineAvailabilityPlotter(self.report)
        self.plot_urls["all_machines_by_machine"] = plotter.plot()

    def combined_availability_plot(self):
        plotter = CombinedEquipmentAvailabilityPlotter(self.report)
        self.plot_urls["combined_availability"] = plotter.plot()

    def generate_plot_urls(self):
        if self.report.machine.count() == 1:
            self.plot_urls["machine"] = self.machines_availability_plot(
                                            self.report.machine.first())

        else:
            self.multiple_machines_plot()
            self.combined_availability_plot()
            
            if self.report.machine.count() == 0:
                mechs = Machine.objects.all()
            else:
                mechs = self.report.machine.all()
            
            self.plot_urls["each_machine"] = []  

            for mech in mechs:
                self.plot_urls["each_machine"].append(
                    self.machines_availability_plot(mech))


class MaintenancePlanPlotFactory(AbstractPlotFactory):
    def machine_tasks_plot(self, e):
        plotter = PreventativeMaintenanceFrequencyPlotter(self.report, e)
        self.plot_urls["each"].append(plotter.plot())

    def combined_tasks_plot(self):
        plotter = CombinedPreventativeMaintenancePlotter(self.report)
        self.plot_urls["combined"] = plotter.plot()

    def generate_plot_urls(self):
        if len(self.report.equipment_list) > 1:
            self.plot_urls["each"] = []
            for e in self.report.equipment_list:
                self.machine_tasks_plot(e)

            self.combined_tasks_plot()
        else:
            self.plot_urls["one"] = self.machine_tasks_plot(self.report.equipment_list[0])


class EquipmentMappingMixin(object):
    """class that abstracts the mapping of pk length to model query"""
    def get_equipment_from_pk(self, pk):
        mapping = {2: Machine,
                    4:Section,
                    6:SubUnit,
                    8:SubAssembly,
                    10:Component}
        return mapping[len(str(pk))].objects.get(pk=pk)

    def equipment_map(self, equipment):
        mapping = {2:Q(machine=equipment),
                    4:Q(section=equipment),
                    6:Q(subunit=equipment),
                    8:Q(subassembly=equipment),
                    10:Q(component=equipment)}
    
        
        return mapping[len(equipment.pk)]


class AbstractPlotter(object):
    """creates graphs for stated parameters
    
    Input
    ========
    report

    Output
    =======
    media url
    .png image of the plotted graph

    This class is an abstract implementation of all common functionality
    structured to allow customization in various points.
    All subclasses must implement these properties
        * ylabel
        * file_name
        * title 
    """

    def __init__(self, report):
        self.report = report
        self.duration = (self.report.end_period - self.report.start_period).days
        self._base_path = os.path.join(os.getcwd(),"media")
        self.x = []
        self.xticks = []
        self.y = []
    
    def preplot(self):
        """implemented where some variables need to be overridden before plotting a graph""" 
        pass

    def postplot(self):
        """implemented where some variables need to be overridden after plotting a graph"""
        pass

    def y_axis_daily(self, *args):
        """abstracts the different functionality in the plot classes"""
        raise NotImplementedError()

    def y_axis_weekly(self, *args):
        """abstracts the different functionality in the plot classes"""
        raise NotImplementedError()

    def y_axis_monthly(self, *args):
        """abstracts the different functionality in the plot classes"""
        raise NotImplementedError()

    def plot_duration(self):
        """plotting method that also chooses how the duration will be represented on the graph"""
        if self.duration < 15:
            self.xlabel = "Date"
            self.plot_daily()
        elif self.duration < 56:
            self.xlabel = "Week Starting:"
            self.plot_weekly()
        else:
            self.xlabel = "Month"
            self.plot_monthly()

    def plot_features(self):
        plt.plot(self.x, self.y, "-o", color="b", linewidth=4, markersize=12)
        plt.bar(self.x, self.y, width=0.8)

    def plot(self):
        """plots the graph"""
        # The angle of the data changes based on the number of items in the 
        # x axis
        
        self.plot_duration()

        if len(self.x) < 2:
            return None
        if max(self.y) == 0:
            return None
        plt.title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        
        dynamic_angle = len(self.x) * 4
        plt.xticks(self.x, self.xticks, rotation=dynamic_angle)
        
        self.preplot()
        self.plot_features()
        self.postplot()
        
        plt.tight_layout()
        plt.savefig(self.path)
        plt.clf()
        return "/media/" + self.file_name

    def plot_daily(self):
        """populates x axis values by each day."""
        for i in range(self.duration):
            day = self.report.start_period + datetime.timedelta(days=i)
            self.xticks.append(day.strftime("%d/%m/%Y"))
            self.x.append(i+1)
            self.y.append(self.y_axis_daily(day))

    def plot_weekly(self):
        """populates x axis values by the number of weeks"""
        weeks = int(self.duration / 7)#make it round up and down!
        curr_date = self.report.start_period
        for i in range(weeks):
            self.x.append(i+1)
            self.xticks.append(str(curr_date))
            next_date = curr_date + datetime.timedelta(days=7)
            self.y.append(self.y_axis_weekly(curr_date, next_date))
            curr_date = next_date

    def plot_monthly(self):
        """populates the x axis values by number of weeks"""
        months = abs(self.report.end_period.month - self.report.start_period.month)
        curr_date = self.report.start_period
        if not isinstance(curr_date, datetime.date):
            curr_date = curr_date.date()
        for i in range(months):
            self.x.append(i+1)
            month_string = curr_date.strftime("%b '%y")
            self.xticks.append(month_string)
            next_date = curr_date + dateutil.relativedelta.relativedelta(months=1)
            self.y.append(self.y_axis_monthly(curr_date, next_date))
            curr_date = next_date


class PreventativeMaintenanceFrequencyPlotter(AbstractPlotter, EquipmentMappingMixin):
    ylabel = "Prevenative Task Frequency"
    def __init__(self, report, equipment, *args, **kwargs):
        super(PreventativeMaintenanceFrequencyPlotter, self).__init__(report, *args, **kwargs)
        self.equipment = equipment
        self.title = equipment
        self.file_name = str(equipment) +"_task_frequency.png"
        self.path = os.path.join(self._base_path, self.file_name)

    def preplot(self):
        plt.ylim(0, max(self.y) + 2)

    def y_axis_daily(self, day):
        return PreventativeTask.objects.filter(Q(scheduled_for=day) & \
                            self.equipment_map(self.equipment)).count() 

    def y_axis_weekly(self, curr, next):
        return PreventativeTask.objects.filter(Q(scheduled_for__gte=curr) & \
                    Q(scheduled_for__lte=next) & \
                    self.equipment_map(self.equipment)).count()

    def y_axis_monthly(self, curr, next):
        return self.y_axis_weekly(curr, next)


class CombinedPreventativeMaintenancePlotter(AbstractPlotter, EquipmentMappingMixin):
    ylabel = "Prevenative Task Frequency"
    def __init__(self, *args, **kwargs):
        super(CombinedPreventativeMaintenancePlotter, self).__init__(*args, **kwargs)
        self.title = "Combined preventative tasks"
        self.file_name =  "combineds_task_count_.png"
        self.path = os.path.join(self._base_path, self.file_name)

    def preplot(self):
        plt.ylim(0, max(self.y) + 2)

    def plot_duration(self):
        count = 1
        self.xlabel ="Equipment"
        for e in self.report.equipment_list:
            self.xticks.append(str(e))
            self.x.append(count)
            total_tasks = PreventativeTask.objects.filter(
                Q(scheduled_for__gte=self.report.start_period) & \
                    Q(scheduled_for__lte=self.report.end_period) & \
                    self.equipment_map(e)).count()
            self.y.append(total_tasks)
            count += 1


class IndividualBreakdownFrequencyPlotter(AbstractPlotter, EquipmentMappingMixin):
    """Plots the frequency of breakdowns for a period of time for a single
    piece of equipment"""

    ylabel="No. of Breakdowns"
    def __init__(self, report, equipment, *args, **kwargs):
        super(IndividualBreakdownFrequencyPlotter, self).__init__(report, *args, **kwargs)
        self.title = str(equipment) + ": Breakdows per Epoch"
        self.equipment = equipment
        self.file_name = str(equipment) + "_breakdowns_per_epoch.png"
        self.path = os.path.join(self._base_path, self.file_name)

    def preplot(self):
        plt.ylim(0, max(self.y) + 2)

    def y_axis_daily(self, day):
        wos = WorkOrder.objects.filter(completion_date=day).filter(
            self.equipment_map(self.equipment))
        
        return wos.count()   

    def y_axis_weekly(self, curr_date, next_date):
        wos = WorkOrder.objects.filter(
            Q(completion_date__gte=curr_date) & Q(
                completion_date__lte=next_date
            )).filter(self.equipment_map(self.equipment))

        return wos.count()

    def y_axis_monthly(self, curr_date, next_date):
        return self.y_axis_weekly(curr_date, next_date)


class BaseBreakdownPlotter(AbstractPlotter, EquipmentMappingMixin):
    """Abstracts the functionality of breakdown plots"""
    def __init__(self, report, *args, **kwargs):
        super(BaseBreakdownPlotter, self).__init__(report, *args, **kwargs)
        self.equipment = self.report.equipment_list
        self.work_orders = self.report.list_work_orders()
    
    def y_value(self, e):
        raise NotImplementedError()

    def preplot(self):
        plt.ylim(0, max(self.y) + 2)

    def plot_duration(self):
        """this method overrides the period based axis values"""
        count = 1
        self.xlabel ="Equipment"
        for e in self.equipment:
            self.xticks.append(str(e))
            self.x.append(count)
            self.y.append(self.y_value(e))
            count += 1

    def match_equipment_to_wos(self, equipment):
        return self.work_orders.filter(self.equipment_map(equipment))


class BreakdownFrequencyDowntimePlotter(BaseBreakdownPlotter):
    
    def __init__(self,report,level, machine):
        super(BreakdownFrequencyDowntimePlotter, self).__init__(report)
        self.ylabel = "No. of breakdowns"
        self.frequency = {}
        self.downtime = {}
        self.level = level
        self.machine = machine
        self.wos = self.report.list_work_orders()
        
        self.title = level.capitalize() + ": breakdown frequency and hours"
        self.file_name = datetime.datetime.strftime(datetime.datetime.now(),"%H%M%S%f") + "breakdown_frequency_plot.png"
        self.path = os.path.join(self._base_path, self.file_name)
        
    
    def curr_level(self, wo):
        mapping = {"section":wo.section,
                            "subunit":wo.subunit,
                            "subassembly":wo.subassembly,
                            "component":wo.component}
        if mapping[self.level]:
            return mapping[self.level].pk
        return None

    def get_dicts(self):
        for wo in self.wos.filter(machine=self.machine):
            if self.curr_level(wo):
                
                self.frequency[self.curr_level(wo)] = self.frequency.get(
                                        self.curr_level(wo), 0) +1
                self.downtime[self.curr_level(wo)] =self.downtime.get(
                                    self.curr_level(wo), 0) + \
                                        (wo.downtime.seconds /3600.0)


    def plot_duration(self):
        count = 1
        self.y_dt = []
        self.xlabel = "Equipment"
        for e, f in self.frequency.iteritems():
            obj = self.get_equipment_from_pk(e)
            self.xticks.append(str(obj))
            self.x.append(count)
            count += 1
            self.y.append(f)
            self.y_dt.append(self.downtime[e])

    def plot(self):
        """plots the graph"""
        # The angle of the data changes based on the number of items in the 
        # x axis
        self.get_dicts()
        self.plot_duration()

        if len(self.x) < 2:
            return None

        if max(self.y) == 0 and max(self.y_dt) == 0:
            return None
        
        dynamic_angle = len(self.x) * 4
        fig, ax1 = plt.subplots()
        plt.xticks(self.x, self.xticks, rotation=dynamic_angle)
        ax1.set_title(self.title)
        ax1.set_xlabel("Equipment")
        ax1.set_ylabel("No. of breakdowns")
        ax1.set_ylim(0, max(self.y) + 2)
        ax1.bar(self.x, self.y, width=0.8, color="#6666ff")
        ax2 = ax1.twinx()
        ax2.set_ylim(0, max(self.y_dt)+2)
        #legend
        blue_patch = matplotlib.patches.Patch(color="blue", label="downtime hrs")
        bar_patch = matplotlib.patches.Patch(color="#6666ff", label="# breakdowns")
        plt.legend(handles = [blue_patch, bar_patch])
        ax2.plot(self.x, self.y_dt, "-o", color="b", linewidth=4, markersize=12)
        ax2.set_ylabel("Downtime Hours")
        plt.tight_layout()
        plt.savefig(self.path)
        plt.clf()
        return "/media/" + self.file_name


class MachineBreakdownFrequencyDowntimePlotter(BaseBreakdownPlotter):
    
    def __init__(self,report):
        super(MachineBreakdownFrequencyDowntimePlotter, self).__init__(report)
        self.ylabel = "No. of breakdowns"
        self.title = "Equipment against breakdown frequency and hours"
        self.file_name = datetime.datetime.strftime(datetime.datetime.now(),"%H%M%S%f") + "breakdown_frequency_plot.png"
        self.path = os.path.join(self._base_path, self.file_name)

    def get_breakdowns_and_downtime(self):
        self.frequency = {}
        self.downtime = {}
        for mech in self.report.machine.all():
            self.frequency[mech.pk] = self.report.list_work_orders().filter(
                                        machine=mech).count()
            self.downtime[mech.pk] = mech.unplanned_downtime_over_period(
                            self.report.start_period, self.report.end_period)
    
    def plot_duration(self):
        self.get_breakdowns_and_downtime()
        count = 1
        self.y_f = []
        self.y_dt = []
        self.xlabel = "Equipment"
        for e, f in self.frequency.iteritems():
            obj = self.get_equipment_from_pk(e)
            self.xticks.append(str(obj))
            self.x.append(count)
            count += 1
            self.y_f.append(f)
            self.y_dt.append(self.downtime[e])

    def plot(self):
        """plots the graph"""
        # The angle of the data changes based on the number of items in the 
        # x axis
        self.plot_duration()
        if len(self.x) < 2:
            return None
        
        if max(self.y_dt) == 0 and max(self.y_f) == 0:
            return None
        
        plt.title(self.title)
        dynamic_angle = len(self.x) * 4
        fig, ax1 = plt.subplots()
        plt.xticks(self.x, self.xticks, rotation=dynamic_angle)
        ax1.set_xlabel("Equipment")
        ax1.set_ylabel("No. of breakdowns")
        ax1.set_ylim(0, max(self.y_f) + 2)
        ax1.bar(self.x, self.y_f, width=0.8)
        ax2 = ax1.twinx()
        ax2.set_ylim(0, max(self.y_dt)+2)
        blue_patch = matplotlib.patches.Patch(color="blue", label="downtime hrs")
        bar_patch = matplotlib.patches.Patch(color="#6666ff", label="# breakdowns")
        plt.legend(handles = [blue_patch, bar_patch])
        ax2.plot(self.x, self.y_dt, "-o", color="b", linewidth=4, markersize=12)
        ax2.set_ylabel("Downtime Hours")
        plt.tight_layout()
        plt.savefig(self.path)
        plt.clf()
        return "/media/" + self.file_name


class CombinedBreakdownFrequencyPlotter(BaseBreakdownPlotter):
    """Plots each piece of equipment that makes the length of the report to the number of work orders raised against it over the entire period"""
    ylabel = "No. of breakdowns"
    title = "Breakdowns over entire period"
    
    def __init__(self, report):
        super(CombinedBreakdownFrequencyPlotter, self).__init__(report)    
        self.file_name = "breakdowns.png"
        self.path = os.path.join(self._base_path, self.file_name)

    def y_value(self, e):
        return self.match_equipment_to_wos(e).count()


class CombinedDowntimePlotter(BaseBreakdownPlotter):
    """Plots each piece of equipment that makes the length of the report to the number of work orders raised against it over the entire period"""
    ylabel = "Downtime hours"
    title = "Downtime hours over entire period per equipment"
    def __init__(self, report):
        super(CombinedDowntimePlotter, self).__init__(report)    
        self.file_name = "downtime" + ".png"
        self.path = os.path.join(self._base_path, self.file_name)

    
    def preplot(self):
        plt.ylim(0, max(self.y) + 2)

    def y_value(self, e):
        return sum((i.downtime.seconds \
            for i in self.match_equipment_to_wos(e))) / 3600.0


class PreventativeVsBreakdownMaintenancePlotter(AbstractPlotter, EquipmentMappingMixin):
    """plots two graphs on the x axis"""
    ylabel = "No. of events"
    

    def __init__(self, report, equipment):
        super(PreventativeVsBreakdownMaintenancePlotter, self).__init__(report)
        self.title = str(equipment) + ": Breakdown vs Preventative maintenance frequency"
        self.file_name = str(equipment) + "_breakdowns_vs_p_tasks.png"
        self.path = os.path.join(self._base_path, self.file_name)
        self.equipment = equipment

    def y_axis_daily(self, day):
        breakdowns =WorkOrder.objects.filter(completion_date=day).filter(
            self.equipment_map(self.equipment)).count()
        p_tasks = PreventativeTask.objects.filter(completed_date=day).filter(
            self.equipment_map(self.equipment)).count()
        return (breakdowns, p_tasks)

    def y_axis_weekly(self, curr, next):
        
        breakdowns = WorkOrder.objects.filter(
            Q(completion_date__gte=curr) & Q(
                completion_date__lte=next
            )).filter(self.equipment_map(
                self.equipment)).count()
        
        p_tasks = PreventativeTask.objects.filter(
            Q(completed_date__gte=curr) & Q(
                completed_date__lte=next
            )).count()
        return (breakdowns, p_tasks)

    def y_axis_monthly(self, curr, next):
        return self.y_axis_weekly(curr, next)

    def plot_features(self):
        """overriding with multiple bar chart"""
        y1 = [i[0] for i in self.y]
        y2 = [i[1] for i in self.y]
        
        plt.ylim(0, max(y1 + y2) + 2)
        plt.bar([x-0.2 for x in self.x], y1, width=0.2, color='r', align='center')
        plt.bar(self.x, y2, width=0.2, color='b', align='center')


class MultipleMachineAvailabilityPlotter(AbstractPlotter):
    title = "Availability of all machines by machine"
    ylabel = "Availability"
    
    def __init__(self, report):
        super(MultipleMachineAvailabilityPlotter, self).__init__(report)
        self.machines = self.report.machine.all()
        if self.machines.count() == 0:
            self.machines = Machine.objects.all()
        
        self.file_name = "machines_availability.png"
        self.path = os.path.join(self._base_path, self.file_name)

    def preplot(self):
        plt.xlabel("Machine")

    def plot_duration(self):
        """this method is common between all periods"""
        count = 1
        self.xlabel="Machine"
        for mech in self.machines:
            self.xticks.append(mech.machine_name)
            self.x.append(count)
            self.y.append(mech.availability_over_period(self.report.start_period, self.report.end_period))
            count +=1


class CombinedEquipmentAvailabilityPlotter(AbstractPlotter):
    """Plots a graph of equipment availability for all equipment in the report"""
    title = "Availability of all machines by date"
    ylabel = "Availability"

    def __init__(self, report):
        super(CombinedEquipmentAvailabilityPlotter, self).__init__(report)
        self.machines = self.report.machine.all()
        if self.machines.count() == 0:
            self.machines = Machine.objects.all()
        
        self.file_name = "all_machines_availability.png"
        self.path = os.path.join(self._base_path, self.file_name)

    def y_axis_daily(self, *args):
        day = args[0]
        return mean(mech.availability_on_date(day) \
                        for mech in self.machines )

    def y_axis_weekly(self, *args):
        curr_date = args[0]
        next_date = args[1]
        return mean(mech.availability_over_period(curr_date, next_date) for mech in self.machines )

    def y_axis_monthly(self, *args):
        curr_date = args[0]
        next_date = args[1]
        return mean(mech.availability_over_period(curr_date, next_date) for mech in self.machines )


class MachineAvailabilityPlotter(AbstractPlotter):
    """Plots the availability for a single machine."""
    ylabel = "Availability"
    
    def __init__(self, report, machine):
        super(MachineAvailabilityPlotter, self).__init__(report)
        self.machine = machine
        self.title = self.machine.machine_name
        self.file_name = self.machine.machine_name + "_availability.png"
        self.path = os.path.join(self._base_path, self.file_name)

    def preplot(self):
        plt.ylim(0, max(self.y) + 2)

    def y_axis_daily(self, day):
        return self.machine.availability_on_date(day)
    
    def y_axis_weekly(self, curr_date, next_date):
        return self.machine.availability_over_period(curr_date, next_date)
            
    def y_axis_monthly(self, curr_date, next_date):
        return self.machine.availability_over_period(curr_date, next_date)