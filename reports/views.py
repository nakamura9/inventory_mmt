import os
import json
import datetime
from xhtml2pdf import pisa

from django.conf import settings

from django.shortcuts import render,get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.views.generic import TemplateView, ListView, DetailView, View
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
from .report_creator import *

"""Abstract the report form views"""


class ReportingHome(ListView):
    template_name = os.path.join("reports", "home.html")
    model = Report
    paginate_by = 20

class ReportSelection(TemplateView):
    template_name = os.path.join("reports", "report_selection.html")

class ReportForm(TemplateView):
    template_name = os.path.join("reports", "report_forms", "generic_report_form.html")

    def get_context_data(self, type):
        context = super(ReportForm, self).get_context_data()
        context.update({"report_name": type.replace("_", " ").capitalize(),
            "machine_field": Machine.objects.all(),
                    "users": Account.objects.all(),
                    "type": type})
        
        return context

    def post(self, request, type=None):
        scope = request.POST.get("scope")
        equipment = request.POST.getlist("equipment[]")
        print type
        if scope == "custom":
            start = datetime.datetime.strptime(request.POST.get("start"),"%m/%d/%Y")
            end = datetime.datetime.strptime(request.POST.get("end"), "%m/%d/%Y")

        else:
            delta =datetime.timedelta(days = int(scope))
            #planning
            if type in ["maintenance_plan", "spares_requirements"]:
                start = datetime.date.today()
                end = start + delta
            #review
            else:
                end = datetime.date.today()
                start = end - delta

        author =request.POST.get("author")
        Report(author=Account.objects.get(username=author),
                start_period=start,
                end_period=end,
                scope=type).save()
        r = Report.objects.latest("pk")

        mapping= {2: Machine,
                    4:Section,
                    6:SubUnit,
                    8:SubAssembly,
                    10:Component}

        if len(equipment) == 0:
            for m in Machine.objects.all():
                r.machine.add(m)
        else:
            for i in equipment:
                r.add_equipment(mapping[len(i)].objects.get(pk=i))

        r.save()


        return HttpResponseRedirect(
                reverse_lazy("reports:report", kwargs={"pk": r.pk})
                )

class ReportView(View):
    def get(self, request, pk):
        report = Report.objects.get(pk=pk)
        report_creator = ReportFactory(report)
    
        return HttpResponse(report_creator.create_report())

        
class MaintenanceReportForm(TemplateView):
    template_name = os.path.join("reports", "report_forms", "maintenance_report_form.html")

    def report_url(self, r):
        return reverse_lazy("reports:maintenance-report", kwargs={"pk": r.pk})

    def get_context_data(self, *args, **kwargs):
        context = super(MaintenanceReportForm, self).get_context_data(*args, **kwargs)
        context.update({"machine_field": Machine.objects.all(),
                    "users": Account.objects.all()})
        return context

    def post(self, request):
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
                scope="maintenance review").save()
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

            else: pass

        r.save()

        
        return HttpResponseRedirect(self.report_url(r))


def delete_report(request, pk=None):
    r= get_object_or_404(Report, pk=pk)
    r.delete()
    return HttpResponseRedirect(reverse_lazy("reports:home"))





def get_maintenance_report_context(report):
    context = {}
    context["object"] = report
    context["p_tasks"], context["wos"], context["checks"] = report.list_jobs()
    time= sum((t.downtime.seconds  for  t in context["wos"] if t.actual_labour_time))
    graphs = []
    factory_availability = FactoryEquipmentAvailabilityPlotFactory(report)
    graphs.append(factory_availability.plot())
    machine_availability = MultipleMachineAvailabilityPlotFactory(report)
    graphs.append(machine_availability.plot())
        
    mechs = report.machine.all()
        
    if mechs.count() == 0:
        mechs = Machine.objects.all()
        
    for mech in mechs:
        graphs.append(MachineAvailabilityPlotFactory(report, mech).plot())

    context["graph_images"] = graphs
    context["total_downtime"] = round(float(time) / 3600.0 ,2) 
    return context