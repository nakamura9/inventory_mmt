# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from itertools import chain

from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.forms import widgets
from django.contrib.auth import authenticate
from django.core import paginator
from django.contrib.auth import login as auth_login

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
    paginate_by = 1

    def get_context_data(self, *args, **kwargs):
        context = super(MachineOverView, self).get_context_data(*args, **kwargs)
        context["work_orders"] = WorkOrder.objects.all()
        return context


class PlannedMaintenanceView(ListView):
    """Page responsible for displaying all the checklists and preventative tasks.

    Cannot use a ListView because 2 models are involved.
    Filter present.
    """
    model = PreventativeTask
    template_name = os.path.join("maintenance", "planned_maintenance_view.html")
    paginate_by =20

    def get_queryset(self):
        if len(self.request.GET.items()) < 2:
            jobs_queryset = PreventativeTask.objects.all()
            checklist_queryset = Checklist.objects.all()
        else:
            jobs = self.request.GET.get("planned_jobs", None)
            checks = self.request.GET.get("checklists", None)
            resolver  = self.request.GET.get("resolver", None)
            machine  = self.request.GET.get("machine", None)
            start  = self.request.GET.get("start_date", None)
            stop  = self.request.GET.get("end_date", None)
            if jobs:
                jobs_queryset = PreventativeTask.objects.all()
                if resolver:
                    jobs_queryset = jobs_queryset.filter(resolver = resolver)
                if machine:
                    jobs_queryset = jobs_queryset.filter(machine = machine)
                jobs_queryset = filter_by_dates(jobs_queryset, start, stop)
            else:
                jobs_queryset = [] 
            if checks:
                checklist_queryset = Checklist.objects.all()
                if resolver:
                    checklist_queryset = checklist_queryset.filter(
                                                            resolver=resolver)
                if machine:
                    checklist_queryset = checklist_queryset.filter(
                                                            machine=machine)
                
                checklist_queryset = filter_by_dates(checklist_queryset, start, stop)
            else:
                checklist_queryset = []
        
        queryset = list(chain(jobs_queryset, checklist_queryset))
        
        return queryset
            
    def get_context_data(self, *args, **kwargs):
        context = super(PlannedMaintenanceView, self).get_context_data(*args, **kwargs)

        context["form"] = PlannedMaintenanceFilterForm(initial={
            "checklists": "True",
            "planned_jobs": "True",
        })
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

    def post(self, request, *args,**kwargs):
        context = {}
        context["users"] =widgets.Select(attrs= {"class": "form-control"},
                                    choices= ((u.username, u.username) \
                                    for u in Account.objects.all())).render(
                                        "username", "None")
        user =self.request.POST.get("username", None)
        pwd = self.request.POST.get("pwd", None)
        auth = authenticate(username=user, password=pwd)
        if not auth:
            context["message"] = "Wrong password"
            
        else:
            auth_login(request, auth)
            user = Account.objects.get(username= user)
            context["message"] = "%s:Hello %s." % (user.role, user.username)
            context["jobs"] = [order for order in WorkOrder.objects.all() if user == order.assigned_to]
            context["planned"] = [task  for task in PreventativeTask.objects.all() if user in task.assignments.all()]
            context["checklists"] = Checklist.objects.filter(resolver = user)

        return render(self.request, self.template_name, context)


    def get_context_data(self, *args, **kwargs):
        context = super(MaintenanceInbox, self).get_context_data(*args, **kwargs)
        context["message"] = ""
        context["users"] =widgets.Select(attrs= {"class": "form-control"},
                                    choices= ((u.username, u.username) \
                                    for u in Account.objects.all())).render(
                                        "username", "None")
        # if a user is already logged in

        
        if self.request.user:
            try:
                user = Account.objects.get(pk= self.request.user.pk)
                context["message"] = "%s:Hello %s." % (user.role, user.username)
            except:
                return context
            
            context["jobs"] = [order for order in WorkOrder.objects.all() if user == order.assigned_to]
            context["planned"] = [task  for task in PreventativeTask.objects.all() if user in task.assignments.all()]
            context["checklists"] = Checklist.objects.filter(resolver = user)

            return context