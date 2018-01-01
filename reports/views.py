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
from django.core import serializers
from django.http import JsonResponse

from .models import Report
from jobcards.models import PreventativeTask, WorkOrder
from checklists.models import Checklist
from inv.models import Machine, Section, SubUnit, SubAssembly, Component
from common_base.utilities import filter_by_dates
from common_base.models import Account
from .report_creator import *
from report_pdf_creator import report_contexts

"""Abstract the report form views"""


class ReportingHome(ListView):
    template_name = os.path.join("reports", "home.html")
    model = Report
    paginate_by = 10

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
            reverse_lazy("reports:report", kwargs={"pk": r.pk}))


class ReportView(View):
    def get(self, request, pk):
        report = Report.objects.get(pk=pk)
        report_creator = ReportFactory(report)
        resp, report_contexts[pk] = report_creator.create_report()
        return HttpResponse(resp)


def delete_report(request, pk=None):
    r= get_object_or_404(Report, pk=pk)
    r.delete()
    return HttpResponseRedirect(reverse_lazy("reports:home"))