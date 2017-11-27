# coding: utf-8
import os
import json
import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.forms import widgets
from django import forms
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import UpdateView
import pytz

from common_base.utilities import filter_by_dates
from common_base.models import Task
from common_base.models import Account
from inv.models import *
from .forms import *
from .models import PreventativeTask, WorkOrder
from inv.forms import SparesForm


class NewWorkOrderView(CreateView):
    """Work order create view"""

    form_class = WorkOrderCreateForm
    template_name = os.path.join("jobcards", "newworkorder.html")
    success_url = reverse_lazy("inventory:inventory-home")

class EditNewWorkOrderView(UpdateView):
    """Edit work order view"""
    
    model = WorkOrder
    form_class = WorkOrderCreateForm
    template_name = os.path.join("jobcards", "newworkorder.html")
    success_url = reverse_lazy("inventory:inventory-home")

class CompleteWorkOrderView(UpdateView):
    """Complete work order view"""

    model = WorkOrder
    form_class = WorkOrderCompleteForm
    template_name = os.path.join("jobcards", "completeworkorder.html")
    success_url = reverse_lazy("inventory:inventory-home")

    

class NewPreventativeTaskView(CreateView):
    """New preventative task view.
    
    Uses sessions to store the list of tasks."""

    form_class = PreventativeTaskCreateForm
    template_name = os.path.join("jobcards", "newpreventativetask.html")
    success_url = reverse_lazy("inventory:inventory-home")

    def get(self, *args, **kwargs):
        """The list of tasks that will be populated by Ajax requests"""
        self.request.session["tasks"] = []
        return super(NewPreventativeTaskView, self).get(*args, **kwargs)

    
    def post(self, *args, **kwargs):
        resp = super(NewPreventativeTaskView, self).post(*args, **kwargs)
        if len(self.request.session.get("tasks")) == 0:
            return HttpResponseRedirect(reverse("jobcards:new-preventative-task"))
        
        p_task = PreventativeTask.objects.get(
                            description=self.request.POST["description"])
        for id, task in enumerate(self.request.session["tasks"]):
            _task = Task(created_for="preventative_task",
                task_number = id,
                description=task)
            _task.save()
            p_task.tasks.add(_task)
            p_task.save()
        self.request.session["tasks"] = []
        self.request.session.modified = True
        return resp

class EditNewPreventativeTaskView(UpdateView):
    """Edits a new preventative task """

    form_class = PreventativeTaskCreateForm
    model = PreventativeTask
    template_name = os.path.join("jobcards", "newpreventativetask.html")
    success_url = reverse_lazy("inventory:inventory-home")

class CompletePreventativeTaskView(UpdateView):
    """Complete view for preventative tasks."""

    form_class = PreventativeTaskCompleteForm
    model = PreventativeTask
    template_name = os.path.join("jobcards", "completepreventativetask.html")
    success_url = reverse_lazy("inventory:inventory-home")

    def get_context_data(self, *args, **kwargs):
        context = super(CompletePreventativeTaskView, self).get_context_data(*args, **kwargs)
        context["spares_form"] = SparesForm()
        return context

class WorkOrderList(ListView):
        """
        List of all unplanned Jobs in the works summary.
        """
        model = WorkOrder
        template_name = os.path.join("jobcards", "work_order_list.html")

        def get_context_data(self, *args, **kwargs):
            context = super(WorkOrderList, self).get_context_data(*args, **kwargs)
            context["form"] = WorkOrderListFilterForm()
            return context

        
        def get_queryset(self, *args, **kwargs):
            """This method is overridden for the sake of the filter functionality incorporated into the page"""
            queryset = self.model.objects.all()
            start_date = self.request.GET.get("start_date", None)
            end_date = self.request.GET.get("end_date", None)
            machine = self.request.GET.get("machine", None)
            resolver = self.request.GET.get("resolver", None)
            
            queryset = filter_by_dates(queryset, start_date, end_date)

            if machine:
                queryset = queryset.filter(machine= machine)

            if resolver:
                queryset = queryset.filter(assigned_to = resolver)

            return queryset
        

@csrf_exempt
def get_resolvers(request):
    """Returns a json representation of all the accounts in the application for instances where the resovler might change"""

    resolvers = [[acc.username, acc.id] for acc in Account.objects.all()]
    return HttpResponse(json.dumps(
        {"resolvers": resolvers}
    ), content_type="application/json")