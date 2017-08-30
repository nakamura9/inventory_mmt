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
from .forms import *
from common_base.models import Account
from django import forms
import datetime
from django.forms import widgets
from django.utils import timezone
import pytz
from django.views.generic.edit import UpdateView
from common_base.utilities import filter_by_dates
from common_base.models import Task

class NewUnplannedJobView(CreateView):
    """
    The view for creating unplanned jobs a.k.a work orders
    """
    form_class = UnplannedJobForm
    template_name = os.path.join("jobcards", "breakdown.html")
    success_url = reverse_lazy("inventory:inventory-home")

        
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
    """
    View for creating planned jobs with a description and task list
    a.k.a scheduled maintenance.
    """
    template_name = os.path.join("jobcards", "planned_job.html")
    form_class = PlannedJobForm
    
    success_url = reverse_lazy("maintenance:planned-maintenance")

    def get(self, *args, **kwargs):
        self.request.session["tasks"] = []

        return super(NewPlannedJobView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        resp = super(NewPlannedJobView,self).post(*args, **kwargs)
        if len(self.request.session.get("tasks")) == 0:
            return HttpResponseRedirect("jobcards:new_planned_job")

        for id, task in enumerate(self.request.session.get("tasks")):
            Task(task_number=id,
            description=task).save()

        self.request.session["tasks"] = []
        self.request.session.modified = True
        
        return resp

class JobCardsList(ListView):
        """
        List of all unplanned Jobs in the works summary
        """
        model = Breakdown
        template_name = os.path.join("jobcards", "jobs.html")

        def get_context_data(self, *args, **kwargs):
            context = super(JobCardsList, self).get_context_data(*args, **kwargs)
            context["form"] = JobListFilterForm()
            context["machine"] = widgets.Select(attrs= {"class": "form-control"},
                                    choices= ((m.unique_id, m.machine_name) for m in Machine.objects.all())).render("machine", "None")
            context["resolver"] = widgets.Select(attrs= {"class": "form-control"},
                                        choices= ((r.id, r.username) for r in Account.objects.all())).render("resolver", "None")
            return context

        
        def get_queryset(self, *args, **kwargs):
            queryset = self.model.objects.all()
            start_date = self.request.GET.get("start_date", None)
            end_date = self.request.GET.get("end_date", None)
            machine = self.request.GET.get("machine", None)
            resolver = self.request.GET.get("resolver", None)
            
            queryset = filter_by_dates(queryset, start_date, end_date)

            if machine:
                queryset = queryset.filter(machine= machine)

            if resolver:
                queryset = queryset.filter(resolver = resolver)

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