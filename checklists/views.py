from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils import timezone
from .models import *
from jobcards.models import Breakdown, PlannedJob
import inv
import os
import datetime
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from .forms import CheckListCreateForm
from django.forms import widgets
from  common_base.models import  Account, Task
from django.contrib.auth import authenticate
import json




class ChecklistDetailView(DetailView):
    """
    Page for viewing the details of a checklist without being able to complete it
    """


    template_name = os.path.join("checklists","checklist_detailview.html")
    model = Checklist

class ChecklistCompleteView(DetailView):
    """"
    If a checklist is open the page is available to the appropriate artisan for 
    completion. The model uses a custom form as very few fields are needed and 
    the page updates an existing checklist, hence the length of the post method.
    """
    
    template_name = os.path.join("checklists","checklist_actionview.html")
    model = Checklist

    def get_context_data(self, *args, **kwargs):
        context = super(ChecklistCompleteView, self).get_context_data(*args, **kwargs)
        context["users"] = Account.objects.all()# might filter by artisan later
        return context

    def post(self, *args, **kwargs):
        checklist = self.get_object()

        if checklist.resolver.username != self.request.POST["user"]:
            return HttpResponse(render(self.request, self.template_name,
                     context={"message":"The authenticated user is not the checklist resovler.",
            "object": self.get_object(),
            "users":Account.objects.all()}))

        user = authenticate(username= \
                self.request.POST["user"],
                password= self.request.POST["password"])
        
        if user:
            checklist.last_completed_date = datetime.date.today()
            checklist.save()
            if self.request.POST["comment"] != "":
                auth =self.get_object().resolver
                chk = self.get_object()
                Comment(author=auth,
                created_for="checklist",
                content=self.request.POST["comment"]).save()
            return HttpResponseRedirect(reverse("inventory:inventory-home"))

        else:
            return HttpResponse(render(self.request, self.template_name, context={"message":"Failed to authenticate properly",
            "object": self.get_object(),
            "users":Account.objects.all()}))


class ChecklistCreateView(CreateView):
    """
    Form for creating new checklists by admin staff. 
    """
    template_name = os.path.join("checklists","checklist_createview.html")
    form_class = CheckListCreateForm
    success_url = reverse_lazy("maintenance:inbox")

    def get(self, *args, **kwargs):
        """The list of tasks that will be populated by Ajax requests"""
        self.request.session["tasks"] = []
        return super(ChecklistCreateView, self).get(*args, **kwargs)

    
    def post(self, *args, **kwargs):
        resp = super(ChecklistCreateView, self).post(*args, **kwargs)
        #makes sure there is at least one task in the session
        if len(self.request.session.get("tasks")) == 0:
            return HttpResponseRedirect(reverse("checklists:create_checklist"))
        
        checklist = Checklist.objects.get(pk=self.request.POST["title"])
        for id, task in enumerate(self.request.session["tasks"]):
            checklist.tasks.add(Task(created_for="checklist",
                task_number = id,
                description=task).save())
            checklist.save()
            self.request.session["tasks"] = []
            self.request.session.modified = True
        return resp


class ChecklistUpdateView(UpdateView):
    template_name = os.path.join("checklists","checklist_updateview.html")
    form_class = CheckListCreateForm
    model = Checklist
    success_url = reverse_lazy("maintenance:inbox")

    def get(self, *args, **kwargs):
        self.request.session["tasks"] = []
        return super(ChecklistUpdateView, self).get(*args, **kwargs)


    def post(self, *args, **kwargs):
        resp = super(ChecklistUpdateView, self).post(*args, **kwargs)
        if len(self.request.session.get("tasks")) == 0 \
         and self.get_object().task_set.count() == 0:
            return HttpResponseRedirect(reverse("checklists:update_checklist", 
                                        kwargs={"pk": self.kwargs["pk"]}))
        
        for id, task in enumerate(self.request.session["tasks"]):
            Task(created_for="checklist" ,
                task_number = id,
                description=task).save()
        
        self.request.session["tasks"] = []
        self.request.session.modified = True
        
        return resp

def delete_checklist(request, pk):
    try:
        Checklist.objects.get(pk=pk).delete()
    except:
        return Http404()
    else:
        return HttpResponseRedirect(reverse("maintenance:planned-maintenance"))



    

@csrf_exempt
def hold_checklist(request, pk):
    if not request.is_ajax():
        return Http404()
    if not authenticate(username=request.POST["username"],
                password=request.POST["password"]):
        return HttpResponse(json.dumps({"authenticated":False}), 
                            content_type="application/json")

    chk = Checklist.objects.get(pk=pk)
    auth = chk.resolver
    chk.on_hold = True
    chk.save()
    Comment(author=auth,
            created_for="checklist",
            content="HOLD:" + request.POST["reason"]).save()
    return HttpResponse(json.dumps({"authenticated":True}), 
                            content_type="application/json")


