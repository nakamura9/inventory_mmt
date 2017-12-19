# coding: utf-8
import os
import json
import datetime
import pytz

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.forms import widgets
from django import forms
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin

from common_base.utilities import role_test, filter_by_dates
from common_base.models import Task, Account, Comment
from common_base.forms import LoginForm
from inv.models import *
from .forms import *
from .models import PreventativeTask, WorkOrder, SparesRequest
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

    def get_context_data(self, *args, **kwargs):
        context = super(CompleteWorkOrderView, self).get_context_data(*args, **kwargs)
        context["spares_form"] = SparesForm()
        context["login_form"] = LoginForm()
        return context

    def post(self, *args, **kwargs):
        resp = super(CompleteWorkOrderView, self).post(*args, **kwargs)

        wo = self.get_object()
        for si in self.request.POST.getlist("spares_issued[]"):
            wo.spares_issued.add(Spares.objects.get(stock_id=si))

        for sr in self.request.POST.getlist("spares_returned[]"):
            wo.spares_returned.add(Spares.objects.get(stock_id=sr))

        wo.status = "completed"
        wo.save()

        return resp

class NewPreventativeTaskView(UserPassesTestMixin ,CreateView):
    """New preventative task view.
    
    Uses sessions to store the list of tasks."""

    form_class = PreventativeTaskCreateForm
    template_name = os.path.join("jobcards", "newpreventativetask.html")
    success_url = reverse_lazy("inventory:inventory-home")
    login_url = "/login/"

    def test_func(self):
        return role_test(self.request.user)
    
    def get_context_data(self, *args, **kwargs):
        context = super(NewPreventativeTaskView, self).get_context_data(*args, **kwargs)
        context["spares_form"] = SparesForm()
        return context

    def post(self, *args, **kwargs):
        resp = super(NewPreventativeTaskView, self).post(*args, **kwargs)
        p_task = PreventativeTask.objects.latest("pk")


        n = 0
        for t in self.request.POST.getlist("tasks[]"):
            n += 1
            p_task.tasks.create(created_for="preventative_task",
                                task_number=n,
                                description=t)

        for pk in self.request.POST.getlist("requested_spares[]"):
            sr = SparesRequest.objects.get(pk=pk)
            sr.preventative_task = p_task
            sr.save()
            
        for i in self.request.POST.getlist("assignments[]"): #LIFE SAVER!!!
            p_task.assignments.add(Account.objects.get(username=i))

        for i in self.request.POST.getlist("spares[]"): #LIFE SAVER!!!
            p_task.required_spares.add(Spares.objects.get(stock_id=i))

        p_task.save()
        return resp

class EditNewPreventativeTaskView(UserPassesTestMixin, UpdateView):
    """Edits a new preventative task """

    form_class = PreventativeTaskEditForm
    model = PreventativeTask
    template_name = os.path.join("jobcards", "edit_preventative_task.html")
    success_url = reverse_lazy("maintenance:inbox")
    login_url = "/login/"
    
    def test_func(self):
        return role_test(self.request.user)
    
    def get_context_data(self, *args, **kwargs):
        context = super(EditNewPreventativeTaskView, self).get_context_data(*args, **kwargs)
        context["spares_form"] = SparesForm()
        return context

    def post(self, *args, **kwargs):
        resp = super(EditNewPreventativeTaskView, self).post(*args, **kwargs)

        p_task = self.get_object()

        if self.request.POST.get("removed_tasks[]", None):
            for t in self.request.POST.getlist("removed_tasks[]"):
                p_task.tasks.get(task_number=t).delete()

        if self.request.POST.get("removed_spares[]", None):
            for s in self.request.POST.getlist("removed_spares[]"):
                p_task.required_spares.remove(Spares.objects.get(stock_id=s))

        for pk in self.request.POST.getlist("requested_spares[]"):
            sr = SparesRequest.objects.get(pk=pk)
            sr.preventative_task = p_task
            sr.save()
        
        if self.request.POST.get("removed_resolvers[]", None):
            for r in self.request.POST.getlist("removed_resolvers[]"):
                p_task.assignments.remove(Account.objects.get(username=r))
                
        for s in self.request.POST.getlist("spares[]"):
            p_task.required_spares.add(Spares.objects.get(stock_id=s))

        for i in self.request.POST.getlist("assignments[]"): #LIFE SAVER!!!
            p_task.assignments.add(Account.objects.get(username=i))

        n = p_task.tasks.all().count()
        for t in self.request.POST.getlist("tasks[]"):
            n += 1
            p_task.tasks.create(created_for="preventative_task",
                                task_number=n,
                                description=t)

        p_task.save()
        return resp


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

    def post(self, *args, **kwargs):
        resp = super(CompletePreventativeTaskView, self).post(*args, **kwargs)

        p_task = self.get_object()
        for s in self.request.POST.getlist("spares[]"):
            p_task.spares_used.add(Spares.objects.get(stock_id=s))

        p_task.save()
        return resp

class WorkOrderList(ListView):
        """
        List of all unplanned Jobs in the works summary.
        """
        paginate_by = 10
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
            status = self.request.GET.get("status", None)
            
            queryset = filter_by_dates(queryset, start_date, end_date)

            if machine:
                queryset = queryset.filter(machine= machine)

            if resolver:
                queryset = queryset.filter(assigned_to = resolver)

            if status:
                queryset = queryset.filter(status = status)

            return queryset

class PreventativeTaskDetailView(DetailView):
    template_name = os.path.join("jobcards", "preventatitve_task_detail.html")
    model = PreventativeTask
        

class WorkOrderDetailView(DetailView):
    template_name = os.path.join("jobcards", "workorder_detail.html")
    model = WorkOrder

    def get_context_data(self, *args, **kwargs):
        context = super(WorkOrderDetailView, self).get_context_data(*args, **kwargs)
        context["admin_user"] = True if Account.objects.get(pk=self.request.user.pk).role == "admin" else False
        return context


@user_passes_test(role_test, "/login/")
def delete_preventative_task(request, pk=None):
    PreventativeTask.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse_lazy("maintenance:planned-maintenance"))

@csrf_exempt
def get_resolvers(request):
    """Returns a json representation of all the accounts in the application for instances where the resovler might change"""

    resolvers = [[acc.username, acc.id] for acc in Account.objects.all()]
    return HttpResponse(json.dumps(
        {"resolvers": resolvers}
    ), content_type="application/json")


@csrf_exempt
def accept_p_task(request):
    pk = request.POST.get("pk")
    resolver = request.POST.get("resolver")
    p_task = PreventativeTask.objects.get(pk=pk)
    p_task.assignments_accepted.add(Account.objects.get(username=resolver))
    p_task.save()
    return HttpResponse(json.dumps({'accepted': 'True'}), content_type="application/json")


@csrf_exempt
def accept_job(request):
    pk = request.POST.get("pk")
    wo = WorkOrder.objects.get(pk=pk)
    wo.status = 'accepted'
    wo.save() 

    return HttpResponse(json.dumps({'accepted': 'True'}), content_type="application/json")

def approve_job(request, pk=None):
    job = WorkOrder.objects.get(pk=pk)
    job.status="approved"
    job.save()
    return HttpResponseRedirect(reverse_lazy("jobcards:work-order-list"))

def decline_job(request):
    job = WorkOrder.objects.get(pk=request.POST.get("job"))
    job.status = "requested"
    user = Account.objects.get(pk= request.user.pk)
    job.comments.create(created_for="work_order",
                        author= user,
                        content = "JOB DECLINED BY:  %s. REASON:" % request.user.username +request.POST.get("reason"))
    job.save()

    return HttpResponse(json.dumps({"success": True}), content_type="application/json")

def transfer_job(request):
    job = WorkOrder.objects.get(pk=request.POST.get("job"))
    job.assigned_to = Account.objects.get(pk = request.POST.get("resolver"))
    job.status = "requested"
    user = Account.objects.get(pk= request.user.pk)
    job.comments.create(created_for="work_order",
                        author= user,
                        content = "Job Transferred from %s to %s" %(request.user.username, job.assigned_to.username))
    job.save()
    return HttpResponse(json.dumps({"success": True}), content_type="application/json")
