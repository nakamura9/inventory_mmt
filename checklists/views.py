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
from .forms import *
from django.forms import widgets
from  inv.models import  Account
from django.contrib.auth import authenticate

class ChecklistListView(ListView):
    model = Checklist
    template_name = os.path.join("checklists","checklist_listview.html")

    def get_context_data(self, *args, **kwargs):
        context = super(ChecklistListView, self).get_context_data(*args, **kwargs)
        context["message"] = ""
        context["users"] =widgets.Select(attrs= {"class": "form-control"},
                                    choices= ((u.username, u.username) for u in Account.objects.all())).render("username", "None")
        user =self.request.GET.get("username", None)
        
        if not user:
            context["message"] = "No user logged in" 
            return context
        
        if not authenticate(username=user, password=self.request.GET["pwd"]):
            context["message"] = "Wrong password"
            return context

        user = Account.objects.get(username= user)
        context["jobs"] = Breakdown.objects.filter(resolver = user)
        context["planned"] = PlannedJob.objects.filter(resolver = user)
        context["checklists"] = Checklist.objects.filter(resolver = user)

        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super(ChecklistListView, self).get_queryset(*args, **kwargs)
        user =self.request.GET.get("username", None)
        if user:
            queryset = queryset.filter(resolver=user)
        else:
            return []
        return [checklist for checklist in queryset if checklist.is_open]
        


class ChecklistDetailView(DetailView):
    template_name = os.path.join("checklists","checklist_detailview.html")
    model = Checklist

class ChecklistCompleteView(DetailView):
    template_name = os.path.join("checklists","checklist_actionview.html")
    model = Checklist

    def get_context_data(self, *args, **kwargs):
        context = super(ChecklistCompleteView, self).get_context_data(*args, **kwargs)
        context["users"] = inv.models.Account.objects.all()
        return context

    def post(self, *args, **kwargs):
        checklist = self.get_object()
        if checklist.resolver.username != self.request.POST["user"]:
            return HttpResponse(render(self.request, self.template_name,
                     context={"message":"The authenticated user is not the checklist resovler.",
            "object": self.get_object(),
            "users":inv.models.Account.objects.all()}))
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
            "users":inv.models.Account.objects.all()}))


class ChecklistCreateView(CreateView):
    template_name = os.path.join("checklists","checklist_createview.html")
    model = Checklist
    fields = ["title", "creation_date", 'estimated_time', 'start_time',"machine", "subunit", "subassembly", "resolver", "category", "frequency"]
    success_url = reverse_lazy("checklists:inbox")

    def get(self, *args, **kwargs):
        self.request.session["tasks"] = []
        return super(ChecklistCreateView, self).get(*args, **kwargs)

    def get_form(self, *args):
        form = super(ChecklistCreateView, self).get_form(*args)
        for field in form.fields:
            form.fields[field].widget.attrs["class"] ="form-control"

        form.fields["machine"].widget.attrs["onchange"] ="updateSubUnits()"
        form.fields["subunit"].widget.attrs["onchange"] ="updateSubAssemblies()"
        return form
    
    
    def post(self, *args, **kwargs):
        resp = super(ChecklistCreateView, self).post(*args, **kwargs)
        if len(self.request.session.get("tasks")) == 0:
            return HttpResponseRedirect(reverse("checklists:create_checklist"))
        
        for id, task in enumerate(self.request.session["tasks"]):
            Task(checklist =Checklist.objects.get(title= self.request.POST["title"]) ,
                task_number = id,
                description=task).save()
            self.request.session["tasks"] = []
            self.request.session.modified = True
        return resp


class ChecklistUpdateView(UpdateView):
    template_name = os.path.join("checklists","checklist_updateview.html")
    model = Checklist
    fields = ["title", "creation_date","machine", "subunit", "resolver", "category", "frequency"]
    success_url = reverse_lazy("checklists:inbox")

    def get(self, *args, **kwargs):
        self.request.session["tasks"] = []
        return super(ChecklistUpdateView, self).get(*args, **kwargs)

    def get_form(self, *args):
        form = super(ChecklistUpdateView, self).get_form(*args)
        form.fields["creation_date"].widget = DateInput()
        return form
    

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
    Checklist.objects.get(pk=pk).delete()
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
    
    chk = Checklist.objects.get(pk=pk)
    auth = chk.resolver
    Comment(author=auth,
            checklist = chk,
            content="HOLD:" + request.POST["reason"]).save()
    return HttpResponse("0")

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

@csrf_exempt
def validate_user(request):
    # check the user name password combineation for a match 
    return HttpResponse("0")
    

