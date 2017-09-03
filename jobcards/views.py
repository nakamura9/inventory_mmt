# coding: utf-8
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import PreventativeTask, WorkOrder
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

class NewWorkOrderView(CreateView):
    form_class = WorkOrderCreateForm
    template_name = os.path.join("jobcards", "newworkorder.html")
    success_url = reverse_lazy("inventory:inventory-home")

class EditNewWorkOrderView(UpdateView):
    model = WorkOrder
    form_class = WorkOrderCreateForm
    template_name = os.path.join("jobcards", "newworkorder.html")
    success_url = reverse_lazy("inventory:inventory-home")

class CompleteWorkOrderView(UpdateView):
    model = WorkOrder
    form_class = WorkOrderCompleteForm
    template_name = os.path.join("jobcards", "completeworkorder.html")
    success_url = reverse_lazy("inventory:inventory-home")

class NewPreventativeTaskView(CreateView):
    form_class = PreventativeTaskCreateForm
    template_name = os.path.join("jobcards", "newpreventativetask.html")
    success_url = reverse_lazy("inventory:inventory-home")

    def get(self, *args, **kwargs):
        """The list of tasks that will be populated by Ajax requests"""
        self.request.session["tasks"] = []
        return super(NewPreventativeTaskView, self).get(*args, **kwargs)

    
    def post(self, *args, **kwargs):
        resp = super(NewPreventativeTaskView, self).post(*args, **kwargs)
        #makes sure there is at least one task in the session
        if len(self.request.session.get("tasks")) == 0:
            return HttpResponseRedirect(reverse("jobcards:new-preventative-task"))
        
        p_task = PreventativeTask.objects.get(description=self.request.POST["description"])# need to find another unique identifier
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
    form_class = PreventativeTaskCreateForm
    model = PreventativeTask
    template_name = os.path.join("jobcards", "newpreventativetask.html")
    success_url = reverse_lazy("inventory:inventory-home")

class CompletePreventativeTaskView(UpdateView):
    form_class = PreventativeTaskCompleteForm
    model = PreventativeTask
    template_name = os.path.join("jobcards", "completepreventativetask.html")
    success_url = reverse_lazy("inventory:inventory-home")


class WorkOrderList(ListView):
        """
        List of all unplanned Jobs in the works summary
        """
        model = WorkOrder
        template_name = os.path.join("jobcards", "work_order_list.html")

        def get_context_data(self, *args, **kwargs):
            context = super(WorkOrderList, self).get_context_data(*args, **kwargs)
            context["form"] = WorkOrderListFilterForm()
            """
            context["machine"] = widgets.Select(attrs= {"class": "form-control"},
                                    choices= ((m.unique_id, m.machine_name) for m in Machine.objects.all())).render("machine", "None")
            context["resolver"] = widgets.Select(attrs= {"class": "form-control"},
                                        choices= ((r.id, r.username) for r in Account.objects.all())).render("resolver", "None")"""
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
        

@csrf_exempt
def get_resolvers(request):
    resolvers = [[acc.username, acc.id] for acc in Account.objects.all()]
    return HttpResponse(json.dumps(
        {"resolvers": resolvers}
    ), content_type="application/json")