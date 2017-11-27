# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.forms import widgets
from django.contrib.auth import authenticate

from checklists.models import Checklist
from common_base.models import Account
from common_base.utilities import filter_by_dates
from jobcards.models import PreventativeTask, WorkOrder
from inv.models import Machine
from .forms import PlannedMaintenanceFilterForm


class MachineOverView(ListView):            
    """Page that provides a summary of all the machines."""

    model = Machine
    template_name = os.path.join("inv", "plantview.html")

    def get_context_data(self, *args, **kwargs):
        context = super(MachineOverView, self).get_context_data(*args, **kwargs)
        context["work_orders"] = WorkOrder.objects.all()
        return context


class PlannedMaintenanceView(TemplateView):
    """Page responsible for displaying all the checklists and preventative tasks.

    Cannot use a ListView because 2 models are involved.
    Filter present.
    """
    template_name = os.path.join("maintenance", "planned_maintenance_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(PlannedMaintenanceView, self).get_context_data(*args, **kwargs)
        jobs = self.request.GET.get("planned_jobs", None)
        checks  = self.request.GET.get("checklists", None)
        resolver  = self.request.GET.get("resolver", None)
        machine  = self.request.GET.get("machine", None)
        start  = self.request.GET.get("start_date", None)
        stop  = self.request.GET.get("end_date", None)

        context["form"] = PlannedMaintenanceFilterForm(initial={
            "checklists": "True",
            "planned_jobs": "True",
        })

        """if not resolver:
            context["checklists"] = Checklist.objects.all()
            context["planned_jobs"] =PreventativeTask.objects.all()
        """    
        if checks:
            checklist_queryset = Checklist.objects.all()
            if resolver:
                checklist_queryset = checklist_queryset.filter(
                                                        resolver=resolver)
            if machine:
                checklist_queryset = checklist_queryset.filter(
                                                        machine=machine)
            checklist_queryset = filter_by_dates(checklist_queryset, start, 
                                                stop)
            context["checklists"] = checklist_queryset

        if jobs:
            jobs_queryset = PreventativeTask.objects.all()
            if resolver:
                jobs_queryset = jobs_queryset.filter(resolver = resolver)
            if machine:
                jobs_queryset = jobs_queryset.filter(machine = machine)
            jobs_queryset = filter_by_dates(jobs_queryset, start, stop)
            context["planned_jobs"] = jobs_queryset
        
        return context


class MaintenanceInbox(ListView):
    """
    The List view acts as an inbox for artisans which divides maintenance tasks
    into checklists, planned and unplanned jobs.
    The page has a login form for resolvers as well as a welcome and login status message 
    The inbox is divided into:
        Work Orders
        Preventative Tasks
        Checklists
    """

    model = Checklist
    template_name = os.path.join("maintenance","inbox.html")

    def get_context_data(self, *args, **kwargs):
        context = super(MaintenanceInbox, self).get_context_data(*args, **kwargs)
        context["message"] = ""
        context["users"] =widgets.Select(attrs= {"class": "form-control"},
                                    choices= ((u.username, u.username) \
                                    for u in Account.objects.all())).render(
                                        "username", "None")
                                        
        user =self.request.GET.get("username", None)
        
        if not user:
            context["message"] = "No user logged in" 
            return context

        if not authenticate(username=user, password=self.request.GET["pwd"]):
            context["message"] = "Wrong password"
            return context

        user = Account.objects.get(username= user)
        context["message"] = "Hello %s." % user.username
        context["jobs"] = [order for order in WorkOrder.objects.all() if user in order.assigned_to.all()]
        context["planned"] = [task  for task in PreventativeTask.objects.all() if user in task.assignments.all()]
        context["checklists"] = Checklist.objects.filter(resolver = user)

        return context