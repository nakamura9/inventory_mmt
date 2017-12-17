import operator
import os
from django.template import Context
from django.template.loader import get_template
from django.shortcuts import render

from .report_plot_creator import *
from checklists.models import Checklist

class ReportFactory(object):
    def __init__(self, report):
        self.report = report
        self.reports = {"maintenance_review": MaintenanceReviewReport,
                        "maintenance_plan": MaintenancePlanReport,
                        "breakdown": BreakdownReport,
                        "component_failure": ComponentFailureReport,
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

class ComponentFailureReport(AbstractReport):
    pass

class SparesRequirementsReport(AbstractReport):
    pass

class SparesUsageReport(AbstractReport):
    pass
    