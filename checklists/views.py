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
from  common_base.models import  Account
from django.contrib.auth import authenticate
import json

class ChecklistListView(ListView):
    """
    The List view acts as an inbox for artisans which divides maintenance tasks
    into checklists, planned and unplanned jobs.
    The page has a login form for resolvers as well as a welcome and login status message 
    """

    model = Checklist
    template_name = os.path.join("checklists","checklist_listview.html")

    def get_context_data(self, *args, **kwargs):
        context = super(ChecklistListView, self).get_context_data(*args, **kwargs)
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
                checklist = chk,
                        content=self.request.POST["comment"]).save()
            return HttpResponseRedirect(reverse("client:browse"))

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
    success_url = reverse_lazy("checklists:inbox")

    def get(self, *args, **kwargs):
        """The list of tasks that will be populated by Ajax requests"""
        self.request.session["tasks"] = []
        return super(ChecklistCreateView, self).get(*args, **kwargs)

    
    def post(self, *args, **kwargs):
        resp = super(ChecklistCreateView, self).post(*args, **kwargs)
        #makes sure there is at least one task in the session
        if len(self.request.session.get("tasks")) == 0:
            return HttpResponseRedirect(reverse("checklists:create_checklist"))
        
        print self.request.POST["title"]
        for id, task in enumerate(self.request.session["tasks"]):
            Task(checklist =Checklist.objects.get(title= self.request.POST["title"]) ,
                task_number = id,
                description=task).save()
            self.request.session["tasks"] = []
            self.request.session.modified = True
        return resp


class ChecklistUpdateView(UpdateView):
    template_name = os.path.join("checklists","checklist_updateview.html")
    form_class = CheckListCreateForm
    model = Checklist
    success_url = reverse_lazy("checklists:inbox")

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
            Task(checklist =Checklist.objects.get(title= self.request.POST["title"]) ,
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
        return HttpResponseRedirect(reverse("client:planned_maintenance"))


@csrf_exempt
def add_task(request):
    if request.is_ajax():
        if request.POST != "":
            request.session["tasks"].append(request.POST["task"])
            request.session.modified = True
            return HttpResponse("0")
        else:
            return HttpResponse("-1")
    else:
        return Http404()
    

@csrf_exempt
def hold_checklist(request, pk):
    if not request.is_ajax():
        return Http404()
    print request.POST
    if not authenticate(username=request.POST["username"],
                password=request.POST["password"]):
        return HttpResponse(json.dumps({"authenticated":False}), 
                            content_type="application/json")

    chk = Checklist.objects.get(pk=pk)
    auth = chk.resolver
    chk.on_hold = True
    chk.save()
    Comment(author=auth,
            checklist = chk,
            content="HOLD:" + request.POST["reason"]).save()
    return HttpResponse(json.dumps({"authenticated":True}), 
                            content_type="application/json")

@csrf_exempt
def remove_task(request):
    if not request.is_ajax:
        return Http404()
    if request.POST == "" or \
        "tasks" not in request.session:
        return HttpResponse("-1")

    if request.POST["task"] in request.session["tasks"]:
        request.session["tasks"].pop(request.POST["task"])
        request.session.modified = True
    try:
        Task.objects.get(description=request.POST["task"]).delete()
    except:
        return Http404()

    return HttpResponse("0")
