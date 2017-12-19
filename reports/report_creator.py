import operator
import os
import json 

from django.template import Context
from django.template.loader import get_template
from django.shortcuts import render

from .report_plot_creator import *
from checklists.models import Checklist
from inv.models import Component, SubAssembly, Section


class ReportFactory(object):
    def __init__(self, report):
        self.report = report
        self.reports = {"maintenance_review": MaintenanceReviewReport,
                        "maintenance_plan": MaintenancePlanReport,
                        "breakdown": BreakdownReport,
                        "weak_point": WeakPointReport,
                        "spares_requirements": SparesRequirementsReport,
                        "spares_usage": SparesUsageReport}
    

    def create_report(self):
        report = self.reports[self.report.scope](self.report)
        return report.generate_report()


class AbstractReport(object):
    def __init__(self, report):
        self.report = report
        self.context = {}

    def get_template(self):
        if not self.template_name:
            raise ValueError("No template was provided to the class")
        self.template = get_template(self.template_name)
        
    def generate_report(self):
        self.get_template()
        self.generate_context()
        return self.template.render(Context(self.context))

    def generate_context(self):
        raise NotImplementedError()

    def create_plots(self):
        pf = PlotCreatorFactory(self.report)
        plotter = pf.create_plotter()
        plotter.generate_plot_urls()
        self.context["graphs"]= plotter.plot_urls


class MaintenancePlanReport(AbstractReport):
    template = template_name = os.path.join("reports", "report_templates", "maintenance_plan_report.html")
    
    def get_checklists(self):
        all_checks = Checklist.objects.filter(reduce(operator.or_, self.report.get_q_filters()))
        valid = [c for c in all_checks \
                    if c.will_be_open_over_period(self.report.start_period,
                                                        self.report.end_period)]

        return valid


    def generate_context(self):
        self.context['object'] = self.report
        self.create_plots()
        checks = self.get_checklists()
        p_tasks = self.report.list_p_tasks()
        self.context["p_task_count"] = p_tasks.count()
        self.context["checks"] = checks
        self.context["check_count"] = len(checks)
        self.context["p_tasks"] = p_tasks
        self.context["p_task_downtime"] = sum((i.estimated_downtime.seconds for i in p_tasks if i.estimated_downtime )) / 3600.0


class MaintenanceReviewReport(AbstractReport):
    template_name = os.path.join("reports", "report_templates", "maintenance_review_report.html")


    def generate_context(self):
        self.context["object"] = self.report
        self.create_plots()
        self.context["p_tasks"], self.context["wos"], self.context["checks"] =\
            self.report.list_jobs()
        self.context["total_downtime"] = sum((t.downtime.seconds  \
            for  t in self.context["wos"] if t.actual_labour_time)) / 3600.0


class BreakdownReport(AbstractReport):
    template_name = os.path.join("reports", "report_templates", "breakdown_report.html")
    
    def generate_context(self):
        self.create_plots()
        self.context["object"] = self.report
        self.context["wos"] = self.report.list_work_orders()
        downtime = sum(( i.downtime.seconds for i in self.report.list_work_orders())) / 3600.0
        self.context["total_downtime"] = downtime


class WeakPointReport(AbstractReport):
    """This report performs weak point analysis of breakdowns over a period
    
    Input
    ======
    report object
    
    Output
    ======
    context - dictionary containing template variables
    
    Methods 
    =======
    create_plots()  - returns a dict of plot urls for insertion in templates
    get_component() - populates the context with the component weak points in   
                    terms of breakdown frequency and length
    get_unit()      - populates the context with the section weak points in   
                    terms of breakdown frequency and length
    analyse_weak_points() - populates the context with the machine weak       
                            points in terms of breakdown frequency and length"""

    
    template_name = os.path.join("reports", "report_templates", "weak_point_report.html")

    def create_plots(self):
        plotter = WeakPointPlotFactory(self.report, self)
        plotter.generate_plot_urls()
        self.context["graphs"]= plotter.plot_urls

    def curr_level(self,level, wo):
        mapping = {"machine":wo.machine,
                    "section":wo.section,
                    "subunit":wo.subunit,
                    "subassembly":wo.subassembly,
                    "component":wo.component}
        return mapping[level]

    def general_weak_points(self, level):
        frequency = {}
        downtime = {}
        for wo in self.wos:
            if self.curr_level(level, wo):
                frequency[self.curr_level(level,wo).pk] = \
                    frequency.get(self.curr_level(level,wo).pk, 0) + 1
                downtime[self.curr_level(level, wo).pk] = \
                    downtime.get(self.curr_level(level, wo).pk, 0) + \
                        (wo.downtime.seconds / 3600.0)

        if len(frequency) == 0 or len(downtime) == 0:
            return

        obj_mapping = {"machine":Machine,
                    "section": Section,
                    "subunit":SubUnit,
                    "subassembly":SubAssembly,
                    "component": Component}

        highest = max(frequency.iteritems(), key=operator.itemgetter(1))[0]
        longest = max(downtime.iteritems(), key=operator.itemgetter(1))[0]
        
        self.context[level] = obj_mapping[level].objects.get(pk=highest)
        self.context[level + "_breakdowns"] =frequency[highest]
        self.context[level + "_downtime"] = obj_mapping[level].objects.get(pk=longest)
        self.context[level + "_downtime_hours"] = downtime[longest]

    def get_component(self):
        """This calculates the overall weak points in the system
        the plotters will plot weak points per machine."""
        self.general_weak_points("component")
        

    def get_unit(self):
        self.general_weak_points("section")

    def analyse_weak_points(self):
        self.wos = self.report.list_work_orders()
        if len(self.report.equipment_list) > 1:
            self.general_weak_points("machine")
        self.get_unit()
        self.get_component()

    def generate_context(self):
        self.analyse_weak_points()
        self.context["object"] = self.report
        self.context["wos"] = self.wos
        downtime = sum(( i.downtime.seconds for i in self.report.list_work_orders())) / 3600.0
        self.context["total_downtime"] =downtime
        self.create_plots()


class SparesRequirementsReport(AbstractReport):
    template_name = os.path.join("reports", "report_templates", "spares_requirements_report.html")
    
    def get_spares_count(self):
        self.p_tasks = self.report.list_p_tasks()
        spares = []
        for task in self.p_tasks:
            spares += [s for s in task.sparesrequest_set.all()]

        return len(spares)

    def generate_context(self):
        self.context["object"] = self.report
        self.context["spares_count"] = self.get_spares_count()
        self.context["p_tasks"] = self.p_tasks


class SparesUsageReport(AbstractReport):
    template_name = os.path.join("reports", "report_templates", "spares_usage_report.html")

    def get_spares_count(self):
        self.wos = self.report.list_work_orders()
        self.p_tasks = self.report.list_p_tasks()
        spares = []
        for wo in self.wos:
            spares += [s for s in wo.spares_issued.all()]
        for task in self.p_tasks:
            spares += [s for s in task.spares_used.all()]

        return len(spares)

    def generate_context(self):
        self.context["object"] = self.report
        self.context["spares_count"] = self.get_spares_count()
        self.context["wos"] = self.wos
        self.context["p_tasks"] = self.p_tasks