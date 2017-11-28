import os
import datetime
import json

from django.contrib.auth import authenticate
from django.forms import widgets
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from jobcards.models import WorkOrder, PreventativeTask
from common_base.models import  Account, Task
from common_base.utilities import ajax_required
from .forms import CheckListCreateForm
from .models import *
import inv

class ChecklistDetailView(DetailView):
    """Page for viewing the details of a checklist without completing it"""

    template_name = os.path.join("checklists","checklist_detailview.html")
    model = Checklist

class ChecklistCompleteView(DetailView):
    """"Page for interacting with an existing checklist
    
    Page consists of a list of details concerning the checklist, a list of 
    all the tasks combined with checkboxes and a form of username, password
    and comments. It also provides the option of placing the checklist on hold
    where a reason field must be supplied
    """
    
    template_name = os.path.join("checklists","checklist_actionview.html")
    model = Checklist

    def get_context_data(self, *args, **kwargs):
        """The resolver select box depends on a list of registered accounts
        inserted here"""

        context = super(ChecklistCompleteView, self).get_context_data(*args, **kwargs)
        context["users"] = Account.objects.all()
        return context

    def post(self, *args, **kwargs):
        """completes the checklist
        
        Checks the resolver, authenticates him if valid and updates checklist details as appropriate. Creates a comment if necessary, returns the inventory home page if successful."""

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


   
    def post(self, *args, **kwargs):
        """Creates a new checklist and its related tasks
        
        Performs the necessary checks on the session and creates a list of tasks based on it. Associates each task with the checklist. Clears the session and saves the checklist."""
        resp = super(ChecklistCreateView, self).post(*args, **kwargs)
        checklist = Checklist.objects.latest("pk")

        n = 0
        for t in self.request.POST.getlist("tasks[]"):
            n += 1
            checklist.tasks.create(created_for="checklist",
                                task_number=n,
                                description=t)
        
        checklist.save()
        return resp


class ChecklistUpdateView(UpdateView):
    template_name = os.path.join("checklists","checklist_updateview.html")
    form_class = CheckListCreateForm
    model = Checklist
    success_url = reverse_lazy("maintenance:inbox")

    def get(self, *args, **kwargs):
        """Prepares the session for the addition of tasks"""

        self.request.session["tasks"] = []
        return super(ChecklistUpdateView, self).get(*args, **kwargs)


    def post(self, *args, **kwargs):
        """Updates checklist data
        
        Makes sure there is at least one task and that the tasks are associated with the checklist.
        """
        
        resp = super(ChecklistUpdateView, self).post(*args, **kwargs)
        checklist = self.get_object()
        if len(self.request.session.get("tasks")) == 0 \
         and checklist.task_set.count() == 0:
            checklist.delete()
            return HttpResponseRedirect(reverse("checklists:update_checklist", 
                                        kwargs={"pk": self.kwargs["pk"]}))
        
        
        for id, task in enumerate(self.request.session["tasks"]):
            _task = Task(created_for="checklist", task_number = id,
                            description=task)
            _task.save()
            checklist.tasks.add(_task)
            checklist.save()
        
        self.request.session["tasks"] = []
        self.request.session.modified = True
        
        return resp


def delete_checklist(request, pk):
    """Deletes the checklist at the push of a button using a pk"""

    try:
        Checklist.objects.get(pk=pk).delete()
    except:
        return Http404()
    else:
        return HttpResponseRedirect(reverse("maintenance:planned-maintenance"))

@csrf_exempt
@ajax_required(Http404)
def hold_checklist(request, pk):
    """Places the checklist on indefinite hold
    Input -> primary key and JSON
    Output -> JSON "authenticated": Boolean

    authenticates the user using json and uses the primray key to set the on_hold field of the checklist to true"""

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