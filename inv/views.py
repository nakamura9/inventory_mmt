from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
import os
import checklists
import jobcards
from .forms import userForm
from .models import *
from inv.models import Account
from django.views.generic import DetailView, ListView, TemplateView
from checklists.models import Checklist
from jobcards.models import Breakdown, PlannedJob
from collections import namedtuple
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

def login(request):
    if request.method == "GET":
       return render(request, os.path.join("inv", "login.html"))
    else:
        name = request.POST["name"]
        pwd = request.POST["pwd"]
        user= authenticate(username=name, password=pwd)
        if user:
            auth_login(request, user)
            return HttpResponseRedirect(reverse("client:browse"))
        else:
            return HttpResponseRedirect(reverse("login"))


def sign_up(request):
    if request.method == "GET":
        form = userForm()
        return render(request, os.path.join("inv", "signup.html"), context={"form": form})
    else:
        form = userForm(request.POST)
        if form.is_valid():
            try:
                new_user = Account.objects.create_user(**form.cleaned_data)
                new_user.save()
            except Exception as e:
                return render(request, os.path.join("inv", "signup.html"), context={"form": form})

            else:
                return HttpResponseRedirect(reverse("login"))
        else:
            return render(request, os.path.join("inv", "signup.html"), context={"form": form})

def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)

    return HttpResponseRedirect(reverse("login"))



class invHome(TemplateView):
    template_name = os.path.join("inv", "inv_home.html")
    
class PlantView(ListView):            
    model = Machine
    template_name = os.path.join("inv", "plantview.html")

class MachineView(DetailView):
    template_name = os.path.join("inv", "machine_details.html")
    model = Machine 
    ##start here finish of the context regarding the planned and unplanned jobs for a 
     
    def get_context_data(self, *args, **kwargs):
        context = super(MachineView, self).get_context_data(*args, **kwargs)
        Planned = namedtuple("Planned", "date resolver est_time type")
        planned_for_machine =PlannedJob.objects.filter(machine=self.object, 
                                                    completed=False)
        context["planned_jobs"] = [Planned(job.creation_epoch, job.resolver,
                                        job.estimated_time, "Planned Job") for job in planned_for_machine]
        checklist_on_machine = Checklist.objects.filter(machine = self.object)
        
        
        for check in checklist_on_machine:
            if check.is_open:
                context["planned_jobs"].append(Planned(check.creation_date, 
                                                        check.resolver, 
                                                        check.estimated_time,
                                                        "Checklist"))

        UnPlanned = namedtuple("UnPlanned", "date resolver description status")

        unplanned_job_on_machine = Breakdown.objects.filter(machine = self.object)
        
        
        context["unplanned_jobs"] = [UnPlanned(b.creation_epoch, b.resolver, b.description, b.completed) \
                                    for b in unplanned_job_on_machine]

        
        return context
class SubUnitView(DetailView):
    template_name = os.path.join("inv", "subunit_details.html")
    model = SubUnit

    def get_context_data(self, *args, **kwargs):
        context = super(SubUnitView, self).get_context_data(*args, **kwargs)
        Planned = namedtuple("Planned", "date resolver est_time type")
        planned_for_machine =PlannedJob.objects.filter(subunit=self.object, 
                                                    completed=False)
        context["planned_jobs"] = [Planned(job.creation_epoch, job.resolver,
                                        job.estimated_time, "Planned Job") for job in planned_for_machine]
        checklist_on_machine = Checklist.objects.filter(subunit = self.object)
        
        for check in checklist_on_machine:
            if check.is_open:
                context["planned_jobs"].append(Planned(check.creation_date, 
                                                        check.resolver, 
                                                        check.estimated_time,
                                                        "Checklist"))

        UnPlanned = namedtuple("UnPlanned", "date resolver description status")

        unplanned_job_on_machine = Breakdown.objects.filter(subunit = self.object)
                
        context["unplanned_jobs"] = [UnPlanned(b.creation_epoch, b.resolver, b.description, b.completed) \
                                    for b in unplanned_job_on_machine]

        return context


class ComponentView(DetailView):
    template_name = os.path.join("inv", "component_details.html")
    model = Component


class SubAssyView(DetailView):
    template_name = os.path.join("inv", "subassy_details.html")
    model = SubAssembly
    
    
class MaintenanceView(TemplateView):
    template_name = os.path.join("inv", "planned_maintenance_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(MaintenanceView, self).get_context_data(*args, **kwargs)
        
        context["checklists"] = checklists.models.Checklist.objects.all()
        context["planned_jobs"] = jobcards.models.PlannedJob.objects.all()
        return context

