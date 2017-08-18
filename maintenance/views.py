# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from inv.models import Machine
from checklists.models import Checklist
from django.forms import widgets
from common_base.models import Account
from django.contrib.auth import authenticate
from jobcards.models import Breakdown, PlannedJob


import os

class PlantOverView(ListView):            
    model = Machine
    template_name = os.path.join("inv", "plantview.html")


class PlannedMaintenanceView(TemplateView):
    template_name = os.path.join("maintenance", "planned_maintenance_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(PlannedMaintenanceView, self).get_context_data(*args, **kwargs)
        
        context["checklists"] = Checklist.objects.all()
        context["planned_jobs"] = PlannedJob.objects.all()
        return context


class MaintenanceInbox(ListView):
    """
    The List view acts as an inbox for artisans which divides maintenance tasks
    into checklists, planned and unplanned jobs.
    The page has a login form for resolvers as well as a welcome and login status message 
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
        context["jobs"] = Breakdown.objects.filter(resolver = user)
        context["planned"] = PlannedJob.objects.filter(resolver = user)
        context["checklists"] = Checklist.objects.filter(resolver = user)

        return context