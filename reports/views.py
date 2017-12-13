import os
import json
import datetime

from django.shortcuts import render,get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView
from formtools.wizard.views import SessionWizardView
from django.core import serializers
from django.http import JsonResponse

from .models import Report
from jobcards.models import PreventativeTask, WorkOrder
from checklists.models import Checklist
from inv.models import Machine, Section, SubUnit, SubAssembly, Component
from .forms import *
from common_base.utilities import filter_by_dates
from common_base.models import Account
from .report_creator import list_jobs, plot_downtime_by_machine, plot_availability_by_machine, plot_availability_for_machine_over_period


class ReportingHome(ListView):
    template_name = os.path.join("reports", "home.html")
    model = Report
    paginate_by = 20

def maintenance(wizard):
    data = wizard.get_cleaned_data_for_step("0") or {}
    c = data.get("category", None)
    if c:
        return str(c) == "maintenance" 
   
def spares(wizard):
    data = wizard.get_cleaned_data_for_step("0") or {}
    c = data.get("category", None)
    if c:
        return str(c) == "inventory" 


class ReportWizard(SessionWizardView):
    template_name = os.path.join("reports", "wizard.html")
    form_list = [FormWizardOne, MaintenanceReportForm, InventoryReportForm]
    condition_dict = {"1": maintenance, "2": spares}

    
    def done(self, form_list, form_dict, **kwargs):
        first = form_list[0].cleaned_data
        sec = form_list[1].cleaned_data
        report = Report()
        report.author = first["author"]
        report.start_period  = first["start_period"]
        report.end_period = first["end_period"]
        report.category = first["category"]
        report.scope = sec["scope"]
        report.save()
        report.target.add(first["target"])
        if first["category"].name== "maintenance":
            report.machine.add(sec["machine"])
            if sec["section"]:
                report.section.add(sec["section"])
            if sec["subassembly"]:
                report.subassembly.add(sec["subassembly"])
            if sec["subunit"]:
                report.subunit.add(sec["subunit"])
            if sec["component"]:
                report.component.add(sec["component"])

        else:
            report.scope = sec["scope"]
            report.spares_category.add(sec["spares_category"])
            for s in sec["spares_chosen"]:
                report.spares.add(Spares.objects.get(stock_id=s))

        report.save()
        return HttpResponseRedirect(reverse_lazy("reports:home"))

class ReportSelection(TemplateView):
    template_name = os.path.join("reports", "report_selection.html")

class MaintenanceReport(DetailView):
    template_name = os.path.join("reports", "report_templates", "maintenance_report.html")
    model = Report 

    def get_context_data(self, *args, **kwargs):
        context = super(MaintenanceReport, self).get_context_data(*args, **kwargs)
        context["p_tasks"], context["wos"], context["checks"] = list_jobs(self.object)
        time= sum((t.downtime.seconds  for  t in context["wos"] if t.actual_labour_time))
        plot_downtime_by_machine(self.object)
        plot_availability_by_machine(self.object)
        for mech in Machine.objects.all():
            plot_availability_for_machine_over_period(self.object, mech)
        

      
        context["total_downtime"] = round(float(time) / 3600.0 ,2) 
        return context 

class MaintenanceReportForm(TemplateView):
    template_name = os.path.join("reports", "report_forms", "maintenance_report_form.html")

    def get_context_data(self, *args, **kwargs):
        context = super(MaintenanceReportForm, self).get_context_data(*args, **kwargs)
        context.update({"machine_field": Machine.objects.all(),
                    "users": Account.objects.all()})
        return context

    def post(self, request):
        data = request.POST.items()
        scope = request.POST.get("scope")
        equipment = request.POST.getlist("equipment[]")

        if scope == "custom":
            start = datetime.datetime.strptime(request.POST.get("start"),"%m/%d/%Y")
            end = datetime.datetime.strptime(request.POST.get("end"), "%m/%d/%Y")

        else:
            delta =datetime.timedelta(days = int(scope))
            end = datetime.date.today()
            start = end - delta

        author =request.POST.get("author")
        Report(author=Account.objects.get(username=author),
                start_period=start,
                end_period=end,
                scope="maintenance plan").save()
        r = Report.objects.latest("pk")

    
        for i in equipment:
            if len(i) == 2:
                r.machine.add(Machine.objects.get(pk=i))
            elif len(i) == 4:
                r.section.add(Section.objects.get(pk=i))

            elif len(i) == 6:
                r.subunit.add(SubUnit.objects.get(pk=i))

            elif len(i) == 8:
                r.subassembly.add(SubAssembly.objects.get(pk=i))

            elif len(i) == 10:
                r.component.add(Component.objects.get(pk=i))

            else: print  "not found"

        r.save()

        
        return HttpResponseRedirect(reverse_lazy("reports:maintenance-report", kwargs={"pk": r.pk}))

def delete_report(request, pk=None):
    r= get_object_or_404(Report, pk=pk)
    r.delete()
    return HttpResponseRedirect(reverse_lazy("reports:home"))