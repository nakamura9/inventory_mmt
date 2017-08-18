# coding: utf-8
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Breakdown, JobCard, PlannedJob
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.views.decorators.csrf import csrf_exempt
from inv.models import *
import os
from django.urls import reverse, reverse_lazy
import json
from .forms import DateInput, TimeInput, UnplannedJobForm, PlannedJobForm
from common_base.models import Account
from django import forms
import datetime
from django.forms import widgets
from django.utils import timezone
import pytz
from django.views.generic.edit import UpdateView

class NewUnplannedJobView(CreateView): 
    form_class = UnplannedJobForm
    template_name = os.path.join("jobcards", "breakdown.html")
    success_url = reverse_lazy("inventory:inventory-home")

    

    def form_valid(self, form, *args, **kwargs):
        obj = form.save(commit = False)
        obj.component_id = self.request.POST["component"]
        obj.subassembly_id = self.request.POST["subassembly"]
        obj.subunit_id = self.request.POST["units"]
        obj.save()
        return super(NewUnplannedJobView, self).form_valid(form, *args, **kwargs)
        
def delete_unplanned_job(request, pk=None):
    job = get_object_or_404(Breakdown, pk=pk)
    job.delete()
    return HttpResponseRedirect(reverse("jobcards:jobs"))

class EditUnPlannedJob(UpdateView):
    template_name = os.path.join("jobcards", "breakdown.html")
    form_class = UnplannedJobForm
    model = Breakdown
    success_url = reverse_lazy("maintenance:planned-maintenance")


class NewPlannedJobView(CreateView):
    template_name = os.path.join("jobcards", "planned_job.html")
    form_class = PlannedJobForm
    
    success_url = reverse_lazy("maintenance:planned-maintenance")

class JobCardsList(ListView):
        model = Breakdown
        template_name = os.path.join("jobcards", "jobs.html")

        def get_context_data(self, *args, **kwargs):
            context = super(JobCardsList, self).get_context_data(*args, **kwargs)
            context["machine"] = widgets.Select(attrs= {"class": "form-control"},
                                    choices= ((m.unique_id, m.machine_name) for m in Machine.objects.all())).render("machine", "None")
            context["resolver"] = widgets.Select(attrs= {"class": "form-control"},
                                        choices= ((r.id, r.username) for r in Account.objects.all())).render("resolver", "None")
            return context

        
        def get_queryset(self, *args, **kwargs):
            self.request.GET
            queryset = self.model.objects.all()
            start_date = self.request.GET.get("start_date", None)
            end_date = self.request.GET.get("end_date", None)
            end_date = self.request.GET.get("end_date", None)
            machine = self.request.GET.get("machine", None)
            resolver = self.request.GET.get("resolver", None)
            date_format = "%m/%d/%Y"
            if start_date:
                start_date = datetime.datetime.strptime(start_date, date_format)
                start_date = pytz.timezone("Africa/Harare").localize(start_date)
                queryset = queryset.filter(creation_epoch__lte = start_date)
            if end_date:
                end_date = datetime.datetime.strptime(end_date, date_format)
                end_date = pytz.timezone("Africa/Harare").localize(end_date)
                queryset = queryset.filter(creation_epoch__gte = end_date)

            if machine:
                queryset = queryset.filter(machine= Machine.objects.get(unique_id=machine))

            if resolver:
                queryset = queryset.filter(resolver = Account.objects.get(id= resolver))
            return queryset
        
def delete_planned_job(request, pk=None):
    job = get_object_or_404(PlannedJob, pk=pk)
    job.delete()
    return HttpResponseRedirect(reverse("maintenance:planned-maintenance"))

class EditPlannedJob(UpdateView):
    template_name = os.path.join("jobcards", "planned_job.html")
    form_class = PlannedJobForm
    model = PlannedJob
    
    success_url = reverse_lazy("maintenance:planned-maintenance")


class JobActionView(DetailView):
    model = Breakdown
    template_name = os.path.join("jobcards", "job_action_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(JobActionView, self).get_context_data(*args, **kwargs)
        delta = self.get_object().creation_epoch - \
        timezone.now()
        
        context["interval"] = "%d day(s), %d hour(s)" % (delta.days, delta.seconds/3600)

        return context

def complete_job(request, breakdown):
    form_data = request.POST.copy().dict()
    form_data.pop("resolver")
    form_data.pop("csrfmiddlewaretoken")
    obj = JobCard(**form_data)
    obj.breakdown = Breakdown.objects.get(pk=breakdown)
    obj.number = obj.breakdown.pk
    obj.breakdown.completed = True
    obj.completion_epoch = timezone.now()
    obj.save()
    return HttpResponseRedirect(reverse("maintenance:planned-maintenance")) 


class PlannedJobActionView(DetailView):
    model = PlannedJob
    template_name = os.path.join("jobcards", "job_action_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(PlannedJobActionView, self).get_context_data(*args, **kwargs)
       
        delta = self.get_object().scheduled_for - datetime.date.today()
        context["interval"] = "%d day(s)" % (delta.days)

        return context

def complete_job(request, planned):
    form_data = request.POST.copy().dict()
    form_data.pop("resolver")
    form_data.pop("csrfmiddlewaretoken")
    obj = JobCard(**form_data)
    obj.planned_job = PlannedJob.objects.get(pk=planned)
    obj.number = obj.planned_job.pk
    obj.planned_job.completed = True
    obj.completion_epoch = timezone.now()
    obj.save()
    return HttpResponseRedirect(reverse("maintenance:planned-maintenance"))



@csrf_exempt
def get_resolvers(request):
    resolvers = [[acc.username, acc.id] for acc in Account.objects.all()]
    return HttpResponse(json.dumps(
        {"resolvers": resolvers}
    ), content_type="application/json")